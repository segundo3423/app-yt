# Descargador YouTube (GUI)

Pequeña aplicación en Python con interfaz gráfica para descargar videos de YouTube en `mp4` o `mp3`.

Instrucciones rápidas:

1. Instala dependencias:

```bash
pip install -r requirements.txt
```

2. Necesitas `ffmpeg` instalado y en el PATH para convertir audio a MP3. Descarga desde https://ffmpeg.org/ y añade la carpeta `bin` a tu `PATH`.

3. Ejecuta la aplicación:

```bash
python yt_downloader_gui.py
```

Qué hace la app:
- Permite pegar la URL del video de YouTube.
- Elegir formato `mp4` o `mp3` y la calidad (highest, 720p, 480p, 360p, audio only).
- Si no existe, crea la carpeta `videos de yt` dentro de tu carpeta `Videos` de Windows y añade `videos` (para MP4) y `audios` (para MP3).

Los archivos descargados se guardan en las carpetas correspondientes.
