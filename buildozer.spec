[app]

# (str) Title of your application
title = JS Studio

# (str) Package name
package.name = jsstudio

# (str) Package domain (needed for android/ios packaging)
package.domain = org.js

# (str) Version of your application
version = 0.1

# (int) Version code
version.code = 1

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

# (str) Presplash background color
android.presplash_color = #000000

# (list) Permissions
android.permissions =

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (int) Android NDK version to use
android.ndk = 28c

# (int) NDK min/target API (p4a 会用它编译原生代码)
android.ndk_api = 21

# (int) Android build tools version
android.build_tools_version = 33.0.2

# (bool) Accept all the licenses of the Android SDK automatically
android.accept_sdk_license = True

# (list) Architecture, one of: arm64-v8a, armeabi-v7a, x86, x86_64
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Warn if root
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 1

# (bool) Warn on root
warn_on_root = 1
