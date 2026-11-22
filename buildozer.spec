[app]
title = JS Studio
package.name = jsstudio
package.domain = org.js
source.dir = .
source.include_exts = py
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 0

[android]
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.permissions =