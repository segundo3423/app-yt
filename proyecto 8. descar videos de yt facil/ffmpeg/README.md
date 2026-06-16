Instrucciones para incluir binarios ffmpeg para Android

Para que `yt-dlp` funcione correctamente en Android y pueda unir/convertir streams, se recomienda incluir binarios `ffmpeg` precompilados dentro del paquete.

Estructura sugerida del proyecto:

ffmpeg/
  armeabi-v7a/
    ffmpeg   # ejecutable para armeabi-v7a
  arm64-v8a/
    ffmpeg   # ejecutable para arm64-v8a

Cómo obtener binarios:
- Puedes descargar builds precompilados de ffmpeg para Android desde repositorios como:
  - https://johnvansickle.com/ffmpeg/ (linux builds, no Android)
  - Repositorios de terceros que entregan ffmpeg compilado para Android (buscar "ffmpeg android build").
- Asegurate de que el binario sea ejecutable y compatible con la arquitectura objetivo.

Incluyendo los binarios en el APK:
- Coloca los binarios en la ruta `ffmpeg/armeabi-v7a/ffmpeg` y `ffmpeg/arm64-v8a/ffmpeg`.
- `buildozer.spec` ya incluye `source.include_patterns = ffmpeg,assets/*`, por lo que serán empaquetados.

Uso desde la app:
- `main_apk.py` busca automáticamente en `./ffmpeg` y ajusta `FFMPEG_BINARY` para apuntar al ejecutable incluido.

Notas:
- Empaquetar binarios aumenta el tamaño del APK.
- Asegurate de cumplir licencias y redistribución de ffmpeg.
