# QR Code Generator

Generate, protect, and decrypt QR codes — on **desktop** (Python/Tkinter) and **mobile/web** (Flutter).

## Features

- **Instant generation** — enter a URL or text and get a QR code immediately
- **Password protection** — encrypt the URL with a password; recipient needs it to decrypt
- **Decrypt mode** — built-in tool to decrypt protected QR codes
- **Error correction** — choose L, M, Q, or H level
- **Size control** — Small, Medium, or Large QR codes
- **Auto-save** — generated QR codes are saved to `Desktop\QR_Codes\`
- **Flexible export** — Save As, Copy Path, or Open Folder
- **Portable** — single `.exe`, no Python installation required

## Download

Grab the latest executable from the [Releases page](https://github.com/anayghatpande/QR_Generator/releases).

## Usage

1. Download `QR_Generator.exe` from Releases
2. Double-click to launch
3. Paste a URL or type text
4. Click **Generate** — the QR code appears and auto-saves
5. Use **Save As...**, **Copy Path**, or **Open Folder** as needed

### Password-protected QR codes

1. Check **Protect with password**
2. Enter and confirm a password
3. Click **Generate** — the QR code encrypts the URL
4. Three files are saved to `Desktop\QR_Codes\`:
   - `*.png` — the protected QR code
   - `*.enc` — the encrypted data (share this if the QR is scanned remotely)
   - `*.key` — the password hint file (keep private)
5. Send the QR image (or `.enc` file) + password to the recipient

### Decrypt a protected QR code

1. Click **Decrypt QR** in the app
2. Load the `.enc` file (or paste the encrypted text directly)
3. Enter the password and click **Decrypt**
4. The original URL is revealed — open it or copy to clipboard

## Development

### Prerequisites

- Python 3.7+
- [qrcode](https://pypi.org/project/qrcode/) + [Pillow](https://pypi.org/project/Pillow/)

### Run from source

```bash
pip install qrcode[pil] cryptography
python qr_generator.py
```

### Build executable

```powershell
.\build.ps1
```

The script installs PyInstaller automatically if missing.

## Flutter App (Android / iOS / Web)

A cross-platform version inside `flutter_qr_app/` with the same features.

### Features

- **Generate** — URL/text input, error correction (L/M/Q/H), size control, password protection
- **Decrypt** — scan QR with camera, paste encrypted text, decrypt with password
- **Cross-compatible** — QR codes encrypted in the Python app can be decrypted in the Flutter app and vice versa

### Run from source

```bash
cd flutter_qr_app
flutter pub get
flutter run           # Android/iOS
flutter run -d chrome # Web
```

### Build

```bash
flutter build apk --release         # Android
flutter build ios --release         # iOS
flutter build web --release         # Web
```

## CI/CD

### Desktop (Python)

Push a version tag to build the `.exe` and create a Release:

```bash
git tag v1.1.0 && git push origin v1.1.0
```

### Flutter (Android + Web)

Push a `flutter-v*` tag:

```bash
git tag flutter-v1.0.0 && git push origin flutter-v1.0.0
```

The workflow builds an **APK** and **Web bundle**, then creates a Release with both.

## License

MIT — see [LICENSE](LICENSE).
