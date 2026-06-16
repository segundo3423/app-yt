#!/usr/bin/env bash
set -e

# Script helper para compilar APK en WSL/Ubuntu usando Buildozer.
# Uso: chmod +x build.sh && ./build.sh

if [ -z "$VIRTUAL_ENV" ]; then
  echo "Creando virtualenv..."
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install buildozer cython
pip install -r requirements.txt || true

# Usar main_apk.py como entrada copiándolo a main.py (buildozer busca main.py)
cp main_apk.py main.py

echo "Iniciando buildozer (esto descargarÃ¡ toolchains y puede tomar mucho tiempo)..."
buildozer -v android debug

echo "APK creado en bin/ (si la compilaciÃ³n fue exitosa)"
