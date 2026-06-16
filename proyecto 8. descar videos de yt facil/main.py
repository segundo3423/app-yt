import os
import threading
from pathlib import Path

import PySimpleGUI as sg
from yt_dlp import YoutubeDL
import imageio_ffmpeg


THEME = {
    "BACKGROUND": "#F8EFF7",
    "TEXT": "#2F2340",
    "INPUT": "#FFFFFF",
    "TEXT_INPUT": "#241A33",
    "SCROLL": "#C8AFE8",
    "BUTTON": ("#241A33", "#F3A9C8"),
    "PROGRESS": ("#FFFFFF", "#B78AE6"),
    "BORDER": 0,
    "SLIDER_DEPTH": 0,
    "PROGRESS_DEPTH": 0,
}

BG = "#F8EFF7"
CARD = "#FFFCFE"
SOFT = "#F2E4F8"
PINK = "#F3A9C8"
LAV = "#D8BEFF"
MINT = "#BFECDD"
PEACH = "#F8CFB8"
TEXT = "#2F2340"
MUTED = "#5E4F78"
SUCCESS = "#2F7A58"
ERROR = "#B93768"
WHITE = "#FFFFFF"
LOG_TEXT = "#342746"
INPUT_TEXT = "#241A33"
PROGRESS_FILL = "#B78AE6"
PROGRESS_BG = "#F3EAF8"


def setup_ffmpeg() -> tuple[str, bool, str]:
    try:
        path = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = str(Path(path).parent)
        os.environ["FFMPEG_BINARY"] = path
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        return path, True, "✓ ffmpeg listo"
    except Exception as e:
        return "", False, f"✘ Error cargando ffmpeg: {e}"


def get_output_dirs() -> tuple[Path, Path]:
    root = Path.home() / "Videos" / "videos de yt"
    if not (Path.home() / "Videos").exists():
        root = Path.home() / "videos de yt"
    videos = root / "videos"
    audios = root / "audios"
    videos.mkdir(parents=True, exist_ok=True)
    audios.mkdir(parents=True, exist_ok=True)
    return videos, audios


DEFAULT_VIDEO_QUALITIES = ["Máxima calidad", "1080p", "720p", "480p", "360p"]
VIDEO_FORMATS = ["mp4", "mkv", "webm"]
AUDIO_CODECS = ["mp3", "opus", "m4a", "aac", "flac", "wav"]
AUDIO_QUALITIES = ["320k", "256k", "192k", "128k", "96k"]

QUALITY_FMT_MAP = {
    "Máxima calidad": "bestvideo+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best",
    "480p": "bestvideo[height<=480]+bestaudio/best",
    "360p": "bestvideo[height<=360]+bestaudio/best",
    "480p (solo video)": "bestvideo[height<=480]",
}


def build_ydl_opts(
    target: Path,
    audio_mode: bool,
    video_quality: str,
    video_fmt: str,
    audio_codec: str,
    audio_quality: str,
    ffmpeg_path: str,
    format_id: str = "",
) -> dict:
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

    if video_quality == "Máxima calidad":
        fmt_str = "bestvideo+bestaudio/best"
    elif video_quality.endswith("p") and video_quality[:-1].isdigit():
        h = video_quality[:-1]
        fmt_str = f"bestvideo[height<={h}]+bestaudio/best"
    else:
        fmt_str = QUALITY_FMT_MAP.get(video_quality, "bestvideo+bestaudio/best")

    return {
        **base,
        "format": fmt_str,
        "merge_output_format": video_fmt,
    }


def fetch_formats_thread(url: str, window: sg.Window):
    try:
        opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False, process=True)

        formats = info.get("formats", [])
        title = info.get("title", "")

        heights = sorted(
            {f.get("height") for f in formats if f.get("height") and f.get("vcodec", "none") != "none"},
            reverse=True,
        )
        video_qualities = ["Máxima calidad"] + [f"{h}p" for h in heights]

        exts = sorted({
            f.get("ext") for f in formats
            if f.get("ext") and f.get("vcodec", "none") != "none"
        })
        video_fmts = list(dict.fromkeys(["mp4", "mkv"] + [e for e in exts if e not in ("mp4", "mkv")]))

        audio_exts = sorted({
            f.get("ext") for f in formats
            if f.get("ext") and f.get("acodec", "none") != "none" and f.get("vcodec", "none") == "none"
        })
        audio_codecs_available = list(dict.fromkeys(
            [e for e in audio_exts if e in AUDIO_CODECS] + ["mp3", "opus", "m4a", "aac"]
        ))

        window.write_event_value("-INFO-DONE-", {
            "title": title,
            "video_qualities": video_qualities,
            "video_fmts": video_fmts,
            "audio_codecs": audio_codecs_available,
            "formats": formats,
        })

    except Exception as e:
        window.write_event_value("-INFO-ERROR-", str(e))


def build_formats_table(info: dict) -> str:
    formats = info.get("formats", [])
    title = info.get("title", "")
    if not formats:
        return "No se encontraron formatos."

    col_w = [12, 6, 9, 5, 18, 18, 10]
    header = (
        f"{'ID':<{col_w[0]}} {'EXT':<{col_w[1]}} {'RES':<{col_w[2]}} "
        f"{'FPS':<{col_w[3]}} {'VIDEO':<{col_w[4]}} {'AUDIO':<{col_w[5]}} {'TAMAÑO':>{col_w[6]}}"
    )
    sep = "─" * len(header)
    lines = [f"▶ {title}", sep, header, sep]
    for f in formats:
        h, w = f.get("height"), f.get("width")
        res = f"{w}x{h}" if w and h else (f"{h}p" if h else "audio")
        size = f.get("filesize") or f.get("filesize_approx")
        size_str = f"{size / 1_048_576:.1f} MB" if size else "?"
        lines.append(
            f"{str(f.get('format_id', '')):<{col_w[0]}} "
            f"{str(f.get('ext', '')):<{col_w[1]}} "
            f"{res:<{col_w[2]}} "
            f"{str(f.get('fps', '')):<{col_w[3]}} "
            f"{str(f.get('vcodec', 'none'))[:col_w[4]]:<{col_w[4]}} "
            f"{str(f.get('acodec', 'none'))[:col_w[5]]} "
            f"{size_str:>{col_w[6]}}"
        )
    lines += [sep, "✦ Pegá el ID en 'Format ID' para usarlo directamente."]
    return "\n".join(lines)


def make_progress_hook(window: sg.Window):
    def hook(d):
        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes") or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            percent = (downloaded / total * 100) if total else 0
            text = f"{d.get('_percent_str', '').strip()}  ETA: {d.get('_eta_str', '').strip()}"
            window.write_event_value("-PROG-", {"percent": percent, "text": text})
        elif status == "finished":
            window.write_event_value("-PROG-", {"percent": 100, "text": "Procesando archivo..."})
    return hook


def download_thread(url: str, opts: dict, window: sg.Window):
    opts["progress_hooks"] = [make_progress_hook(window)]
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        window.write_event_value("-DONE-", "")
    except Exception as e:
        window.write_event_value("-ERROR-", str(e))


def t(text, *, size=10, color=TEXT, bg=None, bold=False, key=None, pad=None):
    return sg.Text(
        text,
        key=key,
        text_color=color,
        background_color=bg,
        font=("Segoe UI", size, "bold" if bold else "normal"),
        pad=pad,
    )


def soft_button(label, key, bg, *, fg=TEXT, size=(16, 1)):
    return sg.Button(
        label,
        key=key,
        button_color=(fg, bg),
        border_width=0,
        mouseover_colors=(fg, WHITE),
        font=("Segoe UI", 10, "bold"),
        size=size,
        pad=(5, 5),
    )


def card_title(title, subtitle):
    return [
        t(title, size=11, bold=True, bg=CARD),
        t(subtitle, size=9, color=MUTED, bg=CARD, pad=((10, 0), (2, 2))),
    ]


def build_layout(ffmpeg_ok: bool, ffmpeg_msg: str):
    hero = sg.Frame(
        "",
        [
            [t("♡ Descargador YouTube ♡", size=20, bold=True, bg=SOFT)],
            [t("Pastel, limpio y con mejor contraste.", size=10, color=MUTED, bg=SOFT)],
        ],
        background_color=SOFT,
        border_width=0,
        expand_x=True,
        pad=(0, 0),
    )

    url_card = sg.Frame(
        "  ♡ Video  ",
        [
            card_title("Link del video", "pegá la URL y analizo formatos automáticamente"),
            [sg.Input(
                key="-URL-",
                expand_x=True,
                enable_events=True,
                background_color=WHITE,
                text_color=INPUT_TEXT,
                border_width=0,
                font=("Segoe UI", 11),
                pad=((0, 0), (6, 8)),
            )],
            [t("Esperando URL...", key="-URL-STATUS-", size=9, color=MUTED, bg=CARD)],
        ],
        title_color=TEXT,
        background_color=CARD,
        border_width=0,
        expand_x=True,
        pad=(10, 10),
    )

    mode_card = sg.Frame(
        "  ✦ Modo  ",
        [
            card_title("Elegí tu tipo de descarga", "video completo o solo audio"),
            [
                sg.Radio("▷ Video", "MODE", key="-MODE-VIDEO-", default=True, enable_events=True,
                         background_color=CARD, text_color=TEXT, font=("Segoe UI", 10, "bold")),
                sg.Radio("♪ Solo audio", "MODE", key="-MODE-AUDIO-", enable_events=True,
                         background_color=CARD, text_color=TEXT, font=("Segoe UI", 10, "bold")),
                sg.Push(background_color=CARD),
                t("Format ID", size=10, color=MUTED, bg=CARD, bold=True),
                sg.Input(key="-FMTID-", size=(10, 1), background_color=WHITE, text_color=INPUT_TEXT, border_width=0),
            ],
        ],
        title_color=TEXT,
        background_color=CARD,
        border_width=0,
        expand_x=True,
        pad=(10, 10),
    )

    video_card = sg.Frame(
        "  ▷ Video  ",
        [[
            t("Calidad", size=10, bg=CARD, bold=True),
            sg.Combo(DEFAULT_VIDEO_QUALITIES, default_value="Máxima calidad", key="-QLT-", readonly=True,
                     size=(16, 1), background_color=WHITE, text_color=TEXT),
            t("Contenedor", size=10, bg=CARD, bold=True, pad=((18, 4), 4)),
            sg.Combo(VIDEO_FORMATS, default_value="mp4", key="-VFMT-", readonly=True,
                     size=(8, 1), background_color=WHITE, text_color=TEXT),
        ]],
        key="-VIDEO-OPTS-",
        title_color=TEXT,
        background_color=CARD,
        border_width=0,
        expand_x=True,
        pad=(10, 10),
    )

    audio_card = sg.Frame(
        "  ♪ Audio  ",
        [[
            t("Codec", size=10, bg=CARD, bold=True),
            sg.Combo(AUDIO_CODECS, default_value="mp3", key="-ACODEC-", readonly=True,
                     size=(10, 1), background_color=WHITE, text_color=TEXT),
            t("Bitrate", size=10, bg=CARD, bold=True, pad=((18, 4), 4)),
            sg.Combo(AUDIO_QUALITIES, default_value="192k", key="-ABRATE-", readonly=True,
                     size=(8, 1), background_color=WHITE, text_color=TEXT),
        ]],
        key="-AUDIO-OPTS-",
        title_color=TEXT,
        background_color=CARD,
        border_width=0,
        expand_x=True,
        visible=False,
        pad=(10, 10),
    )

    action_card = sg.Frame(
        "  ▣ Acciones  ",
        [[
            soft_button("♡ Descargar", "-DL-", PINK),
            soft_button("✦ Ver formatos", "-SHOWTABLE-", LAV),
            soft_button("⌁ Limpiar log", "-CLEARLOG-", MINT),
            sg.Push(background_color=CARD),
            soft_button("Salir", "Salir", PEACH, size=(10, 1)),
        ]],
        title_color=TEXT,
        background_color=CARD,
        border_width=0,
        expand_x=True,
        pad=(10, 10),
    )

    progress_card = sg.Frame(
        "  ◌ Progreso  ",
        [
            card_title("Estado de la descarga", "seguimiento en tiempo real"),
            [sg.ProgressBar(100, orientation="h", size=(42, 18), key="-PB-", expand_x=True, bar_color=(PROGRESS_FILL, PROGRESS_BG))],
            [t("Lista para empezar.", key="-STATUS-LINE-", size=9, color=MUTED, bg=CARD)],
        ],
        title_color=TEXT,
        background_color=CARD,
        border_width=0,
        expand_x=True,
        pad=(10, 10),
    )

    log_card = sg.Frame(
        "  • Diario  ",
        [[
            sg.Multiline(
                size=(92, 14),
                key="-LOG-",
                disabled=True,
                autoscroll=True,
                font=("Consolas", 9),
                background_color="#FFFCFE",
                text_color=LOG_TEXT,
                border_width=0,
                expand_x=True,
                expand_y=True,
            )
        ]],
        title_color=TEXT,
        background_color=CARD,
        border_width=0,
        expand_x=True,
        expand_y=True,
        pad=(10, 10),
    )

    footer = sg.Frame(
        "",
        [[
            t(ffmpeg_msg, size=9, color=SUCCESS if ffmpeg_ok else ERROR, bg=SOFT, bold=True),
            sg.Push(background_color=SOFT),
            t("♡ contraste mejorado", size=9, color=MUTED, bg=SOFT),
        ]],
        background_color=SOFT,
        border_width=0,
        pad=(0, 0),
        expand_x=True,
    )

    return [
        [hero],
        [url_card],
        [mode_card],
        [video_card],
        [audio_card],
        [action_card],
        [progress_card],
        [log_card],
        [footer],
    ]


def log(window: sg.Window, text: str):
    window["-LOG-"].print(text)


def set_busy(window: sg.Window, busy: bool):
    window["-DL-"].update(disabled=busy)
    window["-SHOWTABLE-"].update(disabled=busy)


def set_audio_mode(window: sg.Window, audio: bool):
    window["-VIDEO-OPTS-"].update(visible=not audio)
    window["-AUDIO-OPTS-"].update(visible=audio)


def adjust_ui_for_width(window: sg.Window, width: int):
    """Ajusta fuentes y tamaños de algunos elementos según el ancho de la ventana.
    Esto mejora la legibilidad en pantallas pequeñas (móviles) y en ventanas estrechas.
    """
    try:
        if width <= 420:
            title_sz = 16
            text_sz = 9
            input_sz = 10
            btn_sz = 9
            log_cols = 40
        elif width <= 720:
            title_sz = 18
            text_sz = 10
            input_sz = 11
            btn_sz = 10
            log_cols = 70
        else:
            title_sz = 20
            text_sz = 11
            input_sz = 11
            btn_sz = 10
            log_cols = 92

        # Element updates (silently ignore missing keys)
        for k in ("-URL-STATUS-", "-STATUS-LINE-"):
            if k in window.AllKeysDict:
                window[k].update(font=("Segoe UI", text_sz))

        if "-URL-" in window.AllKeysDict:
            window["-URL-"].update(font=("Segoe UI", input_sz))

        for k in ("-QLT-", "-VFMT-", "-ACODEC-", "-ABRATE-", "-FMTID-"):
            if k in window.AllKeysDict:
                try:
                    window[k].update(font=("Segoe UI", text_sz))
                except Exception:
                    pass

        # Buttons
        for k in ("-DL-", "-SHOWTABLE-", "-CLEARLOG-", "Salir"):
            if k in window.AllKeysDict:
                try:
                    window[k].update(font=("Segoe UI", btn_sz, "bold"))
                except Exception:
                    pass

        # Log multiline size (columns adaptivas)
        if "-LOG-" in window.AllKeysDict:
            try:
                window["-LOG-"].update(size=(log_cols, 14), font=("Consolas", max(8, text_sz - 1)))
            except Exception:
                pass
    except Exception:
        pass


def run_ui():
    sg.theme_add_new("KawaiiSimpleIconsContrast", THEME)
    sg.theme("KawaiiSimpleIconsContrast")

    ffmpeg_path, ffmpeg_ok, ffmpeg_msg = setup_ffmpeg()

    window = sg.Window(
        "♡ Descargador YouTube ♡",
        build_layout(ffmpeg_ok, ffmpeg_msg),
        finalize=True,
        resizable=True,
        margins=(16, 16),
        element_padding=(6, 6),
        background_color=BG,
        use_custom_titlebar=True,
        alpha_channel=0.98,
    )

    # Ajustes iniciales según tamaño de ventana
    try:
        win_w, win_h = window.size
        adjust_ui_for_width(window, win_w)
    except Exception:
        pass

    if ffmpeg_ok:
        log(window, f"ffmpeg: {ffmpeg_path}")
    else:
        log(window, "⚠ Reinstalá con: pip install imageio-ffmpeg --upgrade")

    last_url_analyzed = ""
    cached_info: dict | None = None
    _url_timer: list[int] = [0]
    DEBOUNCE_TICKS = 8

    while True:
        event, values = window.read(timeout=200)

        if event in (sg.WIN_CLOSED, "Salir"):
            break

        # Detectar resize y ajustar UI para pantallas estrechas/móviles
        if event == "__WINDOW_RESIZED__" or event == sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED:
            try:
                win_w, win_h = window.size
                adjust_ui_for_width(window, win_w)
            except Exception:
                pass

        if event == "-CLEARLOG-":
            window["-LOG-"].update("")
            window["-STATUS-LINE-"].update("Log limpito.", text_color=MUTED)

        if event == "-URL-":
            _url_timer[0] = DEBOUNCE_TICKS
            window["-URL-STATUS-"].update("Escribiendo URL...", text_color=MUTED)

        if _url_timer[0] > 0:
            _url_timer[0] -= 1
            if _url_timer[0] == 0:
                url = values["-URL-"].strip()
                if (
                    url
                    and url.startswith(("http://", "https://"))
                    and url != last_url_analyzed
                ):
                    last_url_analyzed = url
                    cached_info = None
                    set_busy(window, True)
                    window["-URL-STATUS-"].update("Analizando video...", text_color=MUTED)
                    window["-STATUS-LINE-"].update("Buscando calidades y formatos...", text_color=MUTED)
                    threading.Thread(target=fetch_formats_thread, args=(url, window), daemon=True).start()

        if event in ("-MODE-VIDEO-", "-MODE-AUDIO-"):
            set_audio_mode(window, audio=values["-MODE-AUDIO-"])
            window["-STATUS-LINE-"].update(
                "Modo audio activo." if values["-MODE-AUDIO-"] else "Modo video activo.",
                text_color=MUTED,
            )

        elif event == "-INFO-DONE-":
            info = values["-INFO-DONE-"]
            cached_info = info
            title = info.get("title", "")
            vq = info.get("video_qualities", DEFAULT_VIDEO_QUALITIES)
            vf = info.get("video_fmts", VIDEO_FORMATS)
            ac = info.get("audio_codecs", AUDIO_CODECS)

            window["-QLT-"].update(values=vq, value=vq[0])
            window["-VFMT-"].update(values=vf, value=vf[0])
            window["-ACODEC-"].update(values=ac, value=ac[0])
            window["-URL-STATUS-"].update(f"✓ {title}" if title else "✓ Video encontrado", text_color=SUCCESS)
            window["-STATUS-LINE-"].update("Todo listo para descargar.", text_color=SUCCESS)
            set_busy(window, False)

        elif event == "-INFO-ERROR-":
            window["-URL-STATUS-"].update("✘ No se pudo obtener info del video", text_color=ERROR)
            window["-STATUS-LINE-"].update("No se pudo analizar la URL.", text_color=ERROR)
            set_busy(window, False)

        elif event == "-SHOWTABLE-":
            if cached_info:
                window["-LOG-"].update("")
                log(window, build_formats_table(cached_info))
            else:
                url = values["-URL-"].strip()
                if not url:
                    sg.popup_ok("Ingresá la URL primero.", title="URL requerida", background_color=CARD, text_color=TEXT)
                    continue
                window["-LOG-"].update("")
                log(window, "Obteniendo tabla de formatos...")
                set_busy(window, True)
                threading.Thread(target=fetch_formats_thread, args=(url, window), daemon=True).start()

        elif event == "-DL-":
            url = values["-URL-"].strip()
            if not url:
                sg.popup_ok("Ingresá la URL del video.", title="URL requerida", background_color=CARD, text_color=TEXT)
                continue
            if not url.startswith(("http://", "https://")):
                sg.popup_ok("La URL debe empezar con http:// o https://", title="URL inválida", background_color=CARD, text_color=TEXT)
                continue

            audio_mode = values["-MODE-AUDIO-"]
            videos_dir, audios_dir = get_output_dirs()
            target = audios_dir if audio_mode else videos_dir

            opts = build_ydl_opts(
                target=target,
                audio_mode=audio_mode,
                video_quality=values["-QLT-"],
                video_fmt=values["-VFMT-"],
                audio_codec=values["-ACODEC-"],
                audio_quality=values["-ABRATE-"],
                ffmpeg_path=ffmpeg_path,
                format_id=values["-FMTID-"].strip(),
            )

            window["-LOG-"].update("")
            window["-PB-"].update(0)
            set_busy(window, True)
            log(window, f"Iniciando descarga: {url}")
            window["-STATUS-LINE-"].update("Preparando descarga...", text_color=MUTED)

            threading.Thread(
                target=download_thread,
                args=(url, opts, window),
                daemon=True,
            ).start()

        elif event == "-PROG-":
            data = values["-PROG-"]
            if isinstance(data, dict):
                pct = min(max(int(data.get("percent", 0)), 0), 100)
                window["-PB-"].update(pct)
                window["-STATUS-LINE-"].update(f"Descargando... {pct}%", text_color=TEXT if pct < 100 else SUCCESS)
                if data.get("text"):
                    log(window, data["text"])

        elif event == "-DONE-":
            window["-PB-"].update(100)
            log(window, "✓ Descarga completada.")
            window["-STATUS-LINE-"].update("Archivo listo.", text_color=SUCCESS)
            set_busy(window, False)
            sg.popup_ok("¡Descarga completada!", title="Listo", background_color=CARD, text_color=TEXT)

        elif event == "-ERROR-":
            err = values["-ERROR-"]
            log(window, f"✘ Error: {err}")
            window["-STATUS-LINE-"].update("Ocurrió un error.", text_color=ERROR)
            set_busy(window, False)
            sg.popup_error(str(err), title="Error")

    window.close()


if __name__ == "__main__":
    run_ui()