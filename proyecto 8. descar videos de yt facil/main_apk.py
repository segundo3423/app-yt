from pathlib import Path
import threading
import os
from functools import partial

from yt_dlp import YoutubeDL
import imageio_ffmpeg

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import mainthread
from kivy.properties import StringProperty, NumericProperty, BooleanProperty

KV = """
BoxLayout:
    orientation: 'vertical'
    padding: dp(8)
    spacing: dp(8)

    Label:
        text: app.title_text
        size_hint_y: None
        height: self.texture_size[1] + dp(8)
        font_size: '20sp'

    TextInput:
        id: url_in
        hint_text: 'Pegá la URL aquí'
        multiline: False
        size_hint_y: None
        height: dp(40)
        on_text_validate: app.on_url_enter(self.text)

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)

        ToggleButton:
            id: mode_video
            text: 'Video'
            state: 'down'
            on_state: app.set_mode(self.state == 'down')

        ToggleButton:
            id: mode_audio
            text: 'Solo audio'
            on_state: app.set_mode(not (self.state == 'normal'))

        Spinner:
            id: qlt
            text: 'Máxima calidad'
            values: ['Máxima calidad', '1080p', '720p', '480p', '360p']

        Spinner:
            id: vfmt
            text: 'mp4'
            values: ['mp4', 'mkv', 'webm']

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)

        Button:
            text: 'Ver formatos'
            on_release: app.show_formats()
        Button:
            text: 'Descargar'
            on_release: app.start_download()
        Button:
            text: 'Limpiar log'
            on_release: app.clear_log()

    ProgressBar:
        id: pb
        max: 100
        value: app.progress
        size_hint_y: None
        height: dp(24)

    Label:
        id: status
        text: app.status_text
        size_hint_y: None
        height: self.texture_size[1] + dp(8)
        font_size: '12sp'

    ScrollView:
        do_scroll_x: False
        do_scroll_y: True

        TextInput:
            id: log
            text: app.log_text
            readonly: True
            size_hint_y: None
            height: max(self.minimum_height, dp(200))
            font_name: 'RobotoMono'
            font_size: '12sp'
            background_color: 1,1,1,1

"""


def setup_ffmpeg() -> tuple[str, bool, str]:
    try:
        path = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = str(Path(path).parent)
        os.environ["FFMPEG_BINARY"] = path
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        return path, True, "✓ ffmpeg listo"
    except Exception as e:
        return "", False, f"✘ Error cargando ffmpeg: {e}"


def find_packaged_ffmpeg() -> tuple[str, bool, str]:
    """Busca un binario de ffmpeg incluido en la carpeta `ffmpeg/` del proyecto.
    Devuelve (path, True, msg) si lo encuentra y lo marca ejecutable.
    """
    p = Path.cwd() / "ffmpeg"
    if not p.exists():
        return "", False, "No hay carpeta ffmpeg incluida."

    # posibles rutas por arquitectura y nombres comunes
    candidates = [
        p / "arm64-v8a" / "ffmpeg",
        p / "armeabi-v7a" / "ffmpeg",
        p / "ffmpeg",
        p / "ffmpeg.exe",
    ]

    for c in candidates:
        if c.exists():
            try:
                # Asegurar permisos ejecutables (en Android no cambia, pero en tests sí)
                try:
                    c.chmod(0o755)
                except Exception:
                    pass
                os.environ["FFMPEG_BINARY"] = str(c)
                os.environ["PATH"] = str(c.parent) + os.pathsep + os.environ.get("PATH", "")
                return str(c), True, f"✓ ffmpeg incluido: {c.name}"
            except Exception as e:
                return "", False, f"Encontrado ffmpeg pero error al usarlo: {e}"

    return "", False, "No se encontró ffmpeg en carpeta ffmpeg/."


def get_output_dirs() -> tuple[Path, Path]:
    root = Path.home() / "Videos" / "videos de yt"
    if not (Path.home() / "Videos").exists():
        root = Path.home() / "videos de yt"
    videos = root / "videos"
    audios = root / "audios"
    videos.mkdir(parents=True, exist_ok=True)
    audios.mkdir(parents=True, exist_ok=True)
    return videos, audios


QUALITY_FMT_MAP = {
    "Máxima calidad": "bestvideo+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best",
    "480p": "bestvideo[height<=480]+bestaudio/best",
    "360p": "bestvideo[height<=360]+bestaudio/best",
}


def build_ydl_opts(target: Path, audio_mode: bool, video_quality: str, video_fmt: str, audio_codec: str, audio_quality: str, ffmpeg_path: str, format_id: str = "") -> dict:
    base = {
        "outtmpl": str(target / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "ffmpeg_location": ffmpeg_path,
    }

    if format_id:
        return {**base, "format": format_id, "merge_output_format": video_fmt}

    if audio_mode:
        bitrate = audio_quality.replace("k", "")
        return {
            **base,
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_codec,
                "preferredquality": bitrate,
            }],
        }

    fmt_str = QUALITY_FMT_MAP.get(video_quality, "bestvideo+bestaudio/best")
    return {**base, "format": fmt_str, "merge_output_format": video_fmt}


class DownloaderApp(App):
    title_text = StringProperty("♡ Descargador YouTube ♡")
    log_text = StringProperty("")
    status_text = StringProperty("Listo")
    progress = NumericProperty(0)
    audio_mode = BooleanProperty(False)

    def build(self):
        # Primero intentar usar un ffmpeg incluido en el paquete (./ffmpeg/...)
        self.ffmpeg_path, ok_pkg, msg_pkg = find_packaged_ffmpeg()
        if ok_pkg:
            self.append_log(msg_pkg)
        else:
            # Fallback a imageio-ffmpeg (entorno de desarrollo)
            self.ffmpeg_path, ok, msg = setup_ffmpeg()
            if ok:
                self.append_log(f"ffmpeg: {self.ffmpeg_path}")
            else:
                self.append_log(msg)
        return Builder.load_string(KV)

    def append_log(self, text: str):
        self.log_text = self.log_text + text + "\n"
        # update TextInput widget content on main thread
        self.root.ids.log.text = self.log_text

    def clear_log(self):
        self.log_text = ""
        self.root.ids.log.text = self.log_text

    def set_mode(self, is_video: bool):
        self.audio_mode = not is_video
        self.status_text = "Modo audio" if self.audio_mode else "Modo video"

    def on_url_enter(self, url: str):
        # start background fetch
        threading.Thread(target=self.fetch_formats, args=(url,), daemon=True).start()
        self.status_text = "Analizando..."

    def show_formats(self):
        url = self.root.ids.url_in.text.strip()
        if not url:
            self.append_log("Ingresá la URL primero.")
            return
        threading.Thread(target=self.fetch_formats, args=(url,), daemon=True).start()
        self.status_text = "Obteniendo formatos..."

    def fetch_formats(self, url: str):
        try:
            opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "skip_download": True}
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False, process=True)

            formats = info.get("formats", [])
            title = info.get("title", "")
            lines = [f"▶ {title}", "Formats:"]
            for f in formats:
                fid = f.get("format_id")
                ext = f.get("ext")
                h = f.get("height")
                w = f.get("width")
                size = f.get("filesize") or f.get("filesize_approx")
                size_str = f"{size / 1_048_576:.1f} MB" if size else "?"
                res = f"{w}x{h}" if w and h else (f"{h}p" if h else "audio")
                lines.append(f"{fid} {ext} {res} {size_str}")

            self._on_formats_ready("\n".join(lines))
        except Exception as e:
            self._on_formats_error(str(e))

    @mainthread
    def _on_formats_ready(self, text: str):
        self.append_log(text)
        self.status_text = "Formatos listos"

    @mainthread
    def _on_formats_error(self, err: str):
        self.append_log(f"Error obteniendo formatos: {err}")
        self.status_text = "Error"

    def start_download(self):
        url = self.root.ids.url_in.text.strip()
        if not url:
            self.append_log("Ingresá la URL del video.")
            return
        videos_dir, audios_dir = get_output_dirs()
        target = audios_dir if self.audio_mode else videos_dir
        opts = build_ydl_opts(
            target=target,
            audio_mode=self.audio_mode,
            video_quality=self.root.ids.qlt.text,
            video_fmt=self.root.ids.vfmt.text,
            audio_codec='mp3',
            audio_quality='192k',
            ffmpeg_path=self.ffmpeg_path,
        )
        self.append_log(f"Iniciando descarga: {url}")
        self.progress = 0
        threading.Thread(target=self.download_thread, args=(url, opts), daemon=True).start()
        self.status_text = "Descargando..."

    def progress_hook(self, d):
        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes") or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            percent = int((downloaded / total * 100) if total else 0)
            text = f"{d.get('_percent_str','').strip()} ETA: {d.get('_eta_str','').strip()}"
            self._update_progress(percent, text)
        elif status == "finished":
            self._update_progress(100, "Procesando archivo...")

    @mainthread
    def _update_progress(self, pct: int, text: str):
        self.progress = pct
        self.root.ids.pb.value = pct
        self.append_log(text)
        if pct >= 100:
            self.status_text = "Completado"

    def download_thread(self, url: str, opts: dict):
        opts = dict(opts)
        opts["progress_hooks"] = [self.progress_hook]
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
            self._on_download_done()
        except Exception as e:
            self._on_download_error(str(e))

    @mainthread
    def _on_download_done(self):
        self.append_log("✓ Descarga completada.")
        self.status_text = "Archivo listo"

    @mainthread
    def _on_download_error(self, err: str):
        self.append_log(f"✘ Error: {err}")
        self.status_text = "Error"


if __name__ == '__main__':
    DownloaderApp().run()
