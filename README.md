# SocialResizer · *One-click, on-spec, on-brand.*

![App icon](assets/social_resizer.png)

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?logo=python&logoColor=white)](#)
[![GUI: Tk](https://img.shields.io/badge/GUI-Tkinter-1E6A8D)](#)
[![Imaging: Pillow](https://img.shields.io/badge/Imaging-Pillow-5B8DEF)](#)
[![Platforms](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-0F172A)](#)

> Batch-create perfectly sized social images in seconds.  
> Presets for major platforms, custom sizes, **cover/contain** modes, **letterbox** (solid color or **transparent**), and export to **JPEG / PNG / Both**.

---

## ✨ What problem does it solve?

Producing on-spec visuals for multiple platforms is slow and error-prone: every network uses different aspect ratios, and manual cropping wastes time and consistency. **SocialResizer** turns one source image into a complete, platform-ready set—**correct sizes, correct formats, consistent branding**—with a single run.

- **Save time:** One input → many outputs.
- **Protect the composition:** *Cover* to fill without awkward bars, or *Contain* to preserve the full image.
- **Stay on brand:** Letterbox with your brand color or transparent padding for compositing.

---

## 🚀 Features

- **Preset bundles**: Instagram (All/Feed/Stories), LinkedIn, Facebook, X/Twitter, YouTube thumbnails, Ads profiles, and more.
- **Custom sizes**: Add your own name + width × height on the fly.
- **Two resize modes**:
  - **Cover** (crop to fill, perfect fit, no bars)
  - **Contain** (keep aspect; optional **letterbox** to exact size)
- **Letterbox options**:
  - Solid color (pick any hex)
  - **Transparent** (PNG only)
- **Export formats**: **JPEG**, **PNG**, or **Both** (with progressive JPEGs).
- **Safe filenames**: Avoids Windows reserved names (e.g., `PRN`, `CON`, …).
- **Clean, single-file GUI** (Tkinter).

---

## 🧭 Supported sizes (built-in)

| Label | Pixels |
|---|---|
| Instagram Post | 1080 × 1080 |
| Instagram Portrait (4:5) | 1080 × 1350 |
| Instagram Story / Reel | 1080 × 1920 |
| Facebook Post | 1200 × 630 |
| LinkedIn Post | 1200 × 627 |
| X/Twitter Post | 1600 × 900 |
| YouTube Thumbnail | 1280 × 720 |
| Landscape 16:9 | 1920 × 1080 |
| Pinterest Tall | 1000 × 1500 |

> You can add more under the `SIZES` dictionary, or create ad-hoc **Custom size** entries in the app.

---

## 🎨 Brand profile (used in app & icon)

- **Primary:** `#5B8DEF`   ▉  
- **Accent:** `#FF6F61`    ▉  
- **Dark base:** `#0F172A` ▉  
- **Light base:** `#F8FAFC` ▉  
- **Gradient (icon):** `#5B8DEF → #7C3AED`

The repository includes a tiny script to generate the app icon from this palette: `assets/make_icon.py` → creates `assets/social_resizer.png` and `assets/social_resizer.ico`.

---

## 📦 Installation

### 1) From source
```bash
# 1) Get dependencies
pip install pillow
# Linux may also need:
# sudo apt install python3-tk

# 2) Run
python social_resizer_gui.py
```

### 2) Standalone .exe (Windows)

**PowerShell (one line):**
```powershell
python -m PyInstaller --onefile --noconsole --name SocialResizer --add-data "assets/social_resizer.ico;assets" --icon "assets/social_resizer.ico" social_resizer_gui.py
```

**cmd.exe (multi-line):**
```cmd
python -m PyInstaller --onefile --noconsole --name SocialResizer ^
  --add-data "assets\social_resizer.ico;assets" ^
  --icon assets\social_resizer.ico social_resizer_gui.py
```

**macOS / Linux** (note the colon in `--add-data`):
```bash
python -m PyInstaller --onefile --noconsole --name SocialResizer \
  --add-data "assets/social_resizer.ico:assets" \
  --icon assets/social_resizer.ico social_resizer_gui.py
```

> Tip: Generate the icon first (`python assets/make_icon.py`) so the build gets a nice app icon.

---

## 🖱️ How to use (GUI)

1. **Source image** → *Browse…* and pick your file (`.jpg`, `.png`, `.webp`, `.tiff`, …).  
2. **Output folder** → choose where to save results.  
3. **Preset bundles** → pick one (e.g., *Instagram – All*) and click **Apply preset**.  
4. **Platforms** → fine-tune by (de)selecting individual sizes or add a **Custom size**.  
5. **Mode**:
   - **Cover**: crops overflow to **fill** the target size exactly.
   - **Contain**: keeps the full image; optionally **Pad to exact size (letterbox)**.
6. **Letterbox**:
   - Choose **Letterbox color** (hex) **or** **Transparent pad** (PNG only).
7. **Export**: pick **JPEG / PNG / Both** and set **JPEG quality**.  
8. Click **Run**. Check the **Log** pane and your output folder.

---

## 🔧 Power user notes

- **Transparent letterbox + JPEG**: JPEG doesn’t support alpha; the chosen color will be used for the JPEG version, while PNG keeps transparency.
- **Windows reserved names**: Filenames like `PRN.jpg` are invalid on Windows. The app sanitizes these automatically.
- **Add or rename presets**: Edit the `PRESETS` dictionary to customize bundles for campaigns (e.g., “Organic”, “Ads”, “Stories only”).

---

## 🧪 Troubleshooting

- **`Import "PIL" could not be resolved`**  
  Install Pillow in the same environment you run the app from:
  ```bash
  python -m pip install pillow
  ```
- **`Tkinter` missing on Linux**  
  ```bash
  sudo apt install python3-tk
  ```
- **PyInstaller command doesn’t work**  
  Use the syntax that matches your shell (PowerShell vs cmd). See the *Installation* section above.
- **`Unable to initialize device PRN` on Windows**  
  Your file or folder name collides with a reserved device name (`PRN`, `CON`, `AUX`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`). Rename it; the app also guards against this.

---

## 🧰 Project structure

```
.
├── social_resizer_gui.py        # Main GUI application (single-file)
└── assets/
    ├── make_icon.py             # Generates brand icon (PNG + ICO)
    ├── social_resizer.png       # App icon (PNG) – generated
    └── social_resizer.ico       # App icon (ICO) – generated
```

---

## 🗺️ Roadmap (nice-to-have)

- Drag-and-drop images into the window  
- Batch over multiple source images  
- Filename prefixes per preset (e.g., `_ads`, `_organic`)  
- Preset import/export (JSON)

---

## 🔐 Privacy

- 100% local. No telemetry, no network calls, no data leaves your machine.

---

## 🤝 Contributing

PRs are welcome! Keep code comments **in English**, and try to match the current style (small, dependency-light, platform-agnostic).  
For new presets, include a brief note and references to official size specs if relevant.

---

## 📝 License

Choose a license that fits your goals (MIT is a popular permissive option).  
If unsure, create a `LICENSE` file with MIT:

```
MIT License

Copyright (c) [year] [your name]
…
```

---

## 📷 Screenshots (optional)

> Add a couple of screenshots or GIFs here for your GitHub page:
>
> - `assets/screenshot-main.png` — main UI  
> - `assets/screenshot-exported.png` — example output set

---

**SocialResizer** — *One-click, on-spec, on-brand.*
