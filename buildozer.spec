[app]

# (str) Title of your application
title = JS Studio

# (str) Package name
package.name = jsstudio

# (str) Package domain (needed for android/ios packaging)
package.domain = org.js

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
requirements = python3,kivy

# (str) Supported orientation: one of: landscape, portrait, all
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Permissions
android.permissions =

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Android SDK/NDK version to use
android.sdk = 33
android.ndk = 28c
android.ndk_api = 21

# (int) Android build tools version
android.build_tools_version = 33.0.2

# (bool) Accept all the licenses of the Android SDK automatically
android.accept_sdk_license = True

# (list) Architecture, one of: arm64-v8a, armeabi-v7a, x86, x86_64
android.archs = arm64-v8a

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android App Theme
#android.app_theme = M

# (str) Presplash background color (for new android toolchain)
android.presplash_color = #000000

# (list) gradle options
android.gradle_dependencies =

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Activate the service to take screenshots
android.add_jars =

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 1

# (bool) Warn on root
warn_on_root = 1
