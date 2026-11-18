#!/usr/bin/env python3
"""Normalize the Android app manifest to Flutter's Android embedding V2."""
from pathlib import Path
import xml.etree.ElementTree as ET

ANDROID = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", ANDROID)
manifest_path = Path("android/app/src/main/AndroidManifest.xml")
if not manifest_path.is_file():
    raise SystemExit(f"ERROR: Android manifest not found: {manifest_path}")

try:
    tree = ET.parse(manifest_path)
except ET.ParseError as exc:
    raise SystemExit(f"ERROR: Invalid AndroidManifest.xml: {exc}")
root = tree.getroot()

# Add required network and camera permissions only when absent.
permissions = {
    element.get(f"{{{ANDROID}}}name")
    for element in root.findall("uses-permission")
}
for permission in ("android.permission.INTERNET", "android.permission.CAMERA"):
    if permission not in permissions:
        ET.SubElement(root, "uses-permission", {f"{{{ANDROID}}}name": permission})

application = root.find("application")
if application is None:
    raise SystemExit("ERROR: Android manifest has no <application> element.")

app_name_key = f"{{{ANDROID}}}name"
if application.get(app_name_key) == "io.flutter.app.FlutterApplication":
    application.set(app_name_key, "${applicationName}")
application.set(f"{{{ANDROID}}}label", "Security Toolkit")
application.set(f"{{{ANDROID}}}usesCleartextTraffic", "false")

meta_name = f"{{{ANDROID}}}name"
meta_value = f"{{{ANDROID}}}value"
embedding = None
for item in application.findall("meta-data"):
    if item.get(meta_name) == "flutterEmbedding":
        embedding = item
        break
if embedding is None:
    embedding = ET.SubElement(application, "meta-data")
embedding.set(meta_name, "flutterEmbedding")
embedding.set(meta_value, "2")

# Remove the obsolete V1 splash-screen marker if one is present.
for item in list(application.findall("meta-data")):
    if item.get(meta_name) == "io.flutter.app.android.SplashScreenUntilFirstFrame":
        application.remove(item)

tree.write(manifest_path, encoding="utf-8", xml_declaration=True)
print(f"Normalized {manifest_path}: flutterEmbedding=2")
