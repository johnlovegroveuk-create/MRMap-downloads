# MRMap downloads

This repository contains only the public download page, release information and published APKs. The app source and release signing key are kept separately.

Permanent download page: https://johnlovegroveuk-create.github.io/MRMap-downloads/

Enable GitHub Pages in Settings → Pages → Deploy from a branch → main → / (root).

For a new release, upload the permanently signed APK as a published GitHub Release using the tag and filename in `latest.json`. Then update `index.html` and `latest.json` together. Publish the APK before the manifest so the app never advertises a missing download. Never put signing keys, passwords, MRMap credentials or private source code here.
