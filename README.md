# QR Code Generator

A clean, modern desktop app to generate QR codes from URLs or text. Built with Python and Tkinter.

## Features

- **Instant generation** — enter a URL or text and get a QR code immediately
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

## Development

### Prerequisites

- Python 3.7+
- [qrcode](https://pypi.org/project/qrcode/) + [Pillow](https://pypi.org/project/Pillow/)

### Run from source

```bash
pip install qrcode[pil]
python qr_generator.py
```

### Build executable

```powershell
.\build.ps1
```

The script installs PyInstaller automatically if missing.

## CI/CD

Pushing a version tag triggers [GitHub Actions](.github/workflows/build-and-release.yml):

```bash
git tag v1.1.0 && git push origin v1.1.0
```

The workflow builds the `.exe`, attaches it to a new Release, and generates release notes.

## License

MIT — see [LICENSE](LICENSE).
