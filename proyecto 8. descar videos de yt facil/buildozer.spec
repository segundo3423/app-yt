[app]
# (str) Title of your application
title = Descargador YouTube

# (str) Package name
package.name = yt_downloader

# (str) Package domain (reverse domain)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all)
source.include_exts = py,png,jpg,kv,txt,md

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# Keep them minimal; yt-dlp is pure-python so should be included.
# Note: imageio-ffmpeg may not package automatically; see README for ffmpeg bundling.
requirements = python3,kivy==2.2.1,yt-dlp,certifi,requests

# (str) Supported orientation (portrait, landscape or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) Targeted Android API
android.api = 33
android.minapi = 21
android.arch = armeabi-v7a, arm64-v8a

# (str) Presplash / icon (place your files in project root and reference here)
# presplash.filename = presplash.png
# icon.filename = icon.png

# (list) Pattern to include additional files (useful to include ffmpeg binary)
# If you bundle an ffmpeg binary, put it in ./ffmpeg and include it here
source.include_patterns = ffmpeg,assets/*

# (str) Application entry point
# Builds look for main.py by default, but for APK we will use `main_apk.py`
# You can override by renaming or setting this.
# (If you want the APK to use the Kivy port) set the entrypoint below.
# (Note: Buildozer by default uses `main.py` — we'll pass a quick instruction in README)

# (str) Preset to add arguments to python
# (not needed now)

[buildozer]
# (str) Path to buildozer
# buildozer = /usr/bin/buildozer

[appx]

[log]
# (int) Log level (0-debug,1-info,2-warning)
log_level = 1

[android]
# (bool) Android entrypoint related settings
# Use the default PythonActivity entrypoint

# (str) Android domain package
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Android additional requirements for p4a
# p4a.bootstrap = sdl2

# (bool) Copy library as assets (useful if bundling ffmpeg binary)
# android.copy_libs = 1

# (list) Additional source dirs for the Android build
# android.add_src = 

# (bool) Compile in debug mode
android.debug = 1

# (str) Gradle images / aars
# android.add_aars =

# Notes:
# - After creating this file, build inside WSL/Ubuntu: install dependencies, then run `buildozer -v android debug`.
# - You will likely need to bundle an ffmpeg binary for Android; see README_BUILD_APK.md for steps.
