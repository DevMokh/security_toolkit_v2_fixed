#!/usr/bin/env python3
"""Fail early with a precise diagnostic if the generated Android app is not V2."""
from pathlib import Path
import xml.etree.ElementTree as ET

ANDROID = "http://schemas.android.com/apk/res/android"
manifest = Path("android/app/src/main/AndroidManifest.xml")
if not manifest.is_file():
    raise SystemExit(f"ERROR: Flutter build manifest missing: {manifest}")

try:
    root = ET.parse(manifest).getroot()
except ET.ParseError as exc:
    raise SystemExit(f"ERROR: Flutter build manifest is invalid XML: {exc}")

applications = root.findall("application")
if not applications:
    raise SystemExit("ERROR: Android manifest contains no application element.")
application = applications[0]
legacy_application = application.get(f"{{{ANDROID}}}name")
if legacy_application == "io.flutter.app.FlutterApplication":
    raise SystemExit("ERROR: V1 FlutterApplication remains in AndroidManifest.xml.")

embedding_values = [
    item.get(f"{{{ANDROID}}}value")
    for item in application.findall("meta-data")
    if item.get(f"{{{ANDROID}}}name") == "flutterEmbedding"
]
if "2" not in embedding_values:
    raise SystemExit(
        "ERROR: Android embedding is not V2. Expected <meta-data android:name=\"flutterEmbedding\" android:value=\"2\"/>."
    )

activity = Path("android/app/src/main/kotlin/com/security/toolkit/MainActivity.kt")
if not activity.is_file():
    raise SystemExit(f"ERROR: V2 MainActivity source missing: {activity}")
source = activity.read_text(encoding="utf-8")
if "io.flutter.embedding.android.FlutterActivity" not in source or "class MainActivity : FlutterActivity()" not in source:
    raise SystemExit("ERROR: MainActivity is not using the Android embedding V2 FlutterActivity.")

print("Android embedding verification passed.")
print(f"Manifest: {manifest}")
print(f"Activity: {activity}")
print("Embedding: V2")
