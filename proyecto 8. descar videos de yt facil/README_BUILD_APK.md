Guía rápida: compilar APK con Buildozer (WSL/Ubuntu)

Resumen: usar Buildozer + python-for-android para construir la app Android desde el código Kivy (`main_apk.py`). Recomendado: usar WSL2 con Ubuntu o una máquina Linux.

1) Requisitos (WSL/Ubuntu)

- WSL2 con Ubuntu 20.04/22.04 o una VM Linux
- Paquetes básicos:

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git build-essential libssl-dev libffi-dev
sudo apt install -y openjdk-11-jdk unzip zip autoconf automake libtool pkg-config
```

2) Crear entorno y preparar proyecto

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install buildozer
pip install cython
# Instalar dependencias locales para test (opcional)
pip install -r requirements.txt
```

3) Inicializar Buildozer (si aún no existe)

```bash
buildozer init
# Esto generará buildozer.spec; puedes reemplazarlo por el que está en el repo
```

4) Ajustes importantes

- Entrada de app: buildozer por defecto buscará `main.py`. Para usar la versión Kivy que generé, renombra o copia:

```bash
cp main_apk.py main.py
```

- ffmpeg: `yt-dlp` necesita `ffmpeg` para unir video/audio y convertir. Android no trae ffmpeg por defecto.
  - Opción A (más simple): incluir un binario `ffmpeg` precompilado para Android en la carpeta `ffmpeg/` del proyecto y añadir `source.include_patterns = ffmpeg` en `buildozer.spec`. Luego en la app, al arrancar, detectar la ruta y exportar `FFMPEG_BINARY` apuntando al ejecutable.
  - Opción B (más complejo): compilar un recipe para python-for-android o usar una receta ya existente que incluya ffmpeg.

Nota: Empaquetar ffmpeg debe hacerse con cuidado: el binario tiene que ser para la arquitectura correcta (`armeabi-v7a` y/o `arm64-v8a`).

5) Compilar

Desde la raíz del proyecto (en WSL):

```bash
# modo debug (más rápido) — requiere mucho tiempo la primera vez (descarga toolchains)
buildozer -v android debug

# genera un APK en bin/
# Para instalar en un dispositivo conectado por USB:
buildozer android deploy run
```

6) Errores comunes y soluciones

- Faltan recetas de dependencias: revisa los logs para ver qué paquete falla; muchas dependencias puras Python funcionan, pero paquetes que requieren compilación C necesitan receta o wheel.
- `imageio-ffmpeg` probablemente no funcione como en escritorio; por eso recomendamos incluir ffmpeg binario.
- Permisos de almacenamiento en Android 11+: puede requerir usar SAF (Storage Access Framework). Para pruebas iniciales, WRITE_EXTERNAL_STORAGE puede funcionar en dispositivos antiguos; para Play Store hay que migrar a almacenamiento seguro.

7) Alternativa: compilación en la nube

Si no quieres configurar WSL, puedes usar GitHub Actions (o servicios de pago) que ejecuten Buildozer en contenedores Linux y devuelvan el APK. Puedo preparar un flujo de GitHub Actions si lo prefieres.

Si querés, ya preparé un workflow de GitHub Actions que intenta compilar el APK en un contenedor preconfigurado de Buildozer.

CI notes y uso:

- El workflow está en `.github/workflows/build_apk.yml` y se ejecuta manualmente (`workflow_dispatch`).
- El job usa la imagen `kivy/buildozer:latest` y ejecuta `buildozer -v android debug`.
- Si querés usar la versión Kivy (creada en `main_apk.py`), el workflow copia `main_apk.py` a `main.py` antes de compilar.
- Si la compilación es exitosa, el APK aparecerá como artifact descargable desde la página del workflow.

Limitaciones y tips:

- La compilación en CI puede fallar por dependencias nativas o por la falta de binarios `ffmpeg`. Para resolverlo, agrega los binarios en `ffmpeg/` (ver `ffmpeg/README.md`) o prepara una recipe de `ffmpeg` para python-for-android.
- Primer build tardará mucho (descarga toolchains). Usá el log del workflow para depurar problemas.

Siguiente paso: si querés que lo ejecute ahora en GitHub, dímelo y lo lanzo; si preferís que lo ajuste (por ejemplo añadir signing keys o soporte por ABI específicos), lo preparo antes.

- Generar script `build.sh` con los comandos y comprobaciones para WSL.
- Añadir plantilla para incluir binarios `ffmpeg/armeabi-v7a/ffmpeg` y ajustar `main_apk.py` para usar esa ruta.
- Preparar GitHub Actions workflow para compilar automáticamente.

Si querés, empiezo generando un `build.sh` y una carpeta `ffmpeg/README.md` con instrucciones para añadir binarios. ¿Lo genero ahora?