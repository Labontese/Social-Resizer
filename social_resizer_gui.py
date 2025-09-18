"""
SocialResizer — One-click, on-spec, on-brand.
GUI tool to batch-create social-ready images with cover/contain modes,
optional letterboxing (solid color or transparency), export as JPEG/PNG/Both,
preset bundles (Instagram, LinkedIn, etc.), and custom sizes.

Author: You + ChatGPT
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image

# ------------------------
# Canonical sizes (pixels)
# ------------------------
SIZES = {
    "Instagram Post (1080×1080)": ("instagram_post", (1080, 1080)),
    "Instagram Portrait 4:5 (1080×1350)": ("instagram_portrait", (1080, 1350)),
    "Instagram Story/Reel (1080×1920)": ("instagram_story", (1080, 1920)),
    "Facebook Post (1200×630)": ("facebook_post", (1200, 630)),
    "LinkedIn Post (1200×627)": ("linkedin_post", (1200, 627)),
    "X/Twitter Post (1600×900)": ("twitter_post", (1600, 900)),
    "YouTube Thumbnail (1280×720)": ("youtube_thumb", (1280, 720)),
    "Landscape 16:9 (1920×1080)": ("landscape_16_9", (1920, 1080)),
    "Pinterest Tall (1000×1500)": ("pinterest_tall", (1000, 1500)),
}

# ------------------------
# Preset bundles/profiles
# ------------------------
PRESETS = {
    "-- Choose preset --": [],
    "Instagram – All": [
        "Instagram Post (1080×1080)",
        "Instagram Portrait 4:5 (1080×1350)",
        "Instagram Story/Reel (1080×1920)",
    ],
    "Instagram – Feed Only": [
        "Instagram Post (1080×1080)",
        "Instagram Portrait 4:5 (1080×1350)",
    ],
    "Stories/Reels": [
        "Instagram Story/Reel (1080×1920)",
    ],
    "LinkedIn – Post": [
        "LinkedIn Post (1200×627)",
    ],
    "Facebook – Post": [
        "Facebook Post (1200×630)",
    ],
    "X/Twitter – Post": [
        "X/Twitter Post (1600×900)",
    ],
    # Paid ads oriented bundles
    "Meta Ads (IG+FB)": [
        "Instagram Post (1080×1080)",
        "Instagram Portrait 4:5 (1080×1350)",
        "Landscape 16:9 (1920×1080)",
    ],
    "LinkedIn Ads": [
        "LinkedIn Post (1200×627)",   # 1.91:1
        "Landscape 16:9 (1920×1080)",
    ],
    "YouTube – Thumbnail": [
        "YouTube Thumbnail (1280×720)",
    ],
    "All Platforms": list(SIZES.keys()),
}

# ------------------------
# Windows reserved names
# ------------------------
RESERVED = {
    "CON","PRN","AUX","NUL",
    "COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9",
    "LPT1","LPT2","LPT3","LPT4","LPT5","LPT6","LPT7","LPT8","LPT9",
}

def sanitize_basename(name: str) -> str:
    """Ensure safe Windows filename base (no reserved device names)."""
    base = name.strip().rstrip(". ")
    if base.upper() in RESERVED:
        base = f"{base}_img"
    return base

def hex_to_rgb(hx: str):
    """#RRGGBB -> (R,G,B). Gracefully fallback to white."""
    try:
        hx = hx.strip().lstrip("#")
        if len(hx) == 3:  # e.g., #fff
            hx = "".join(c*2 for c in hx)
        r = int(hx[0:2], 16)
        g = int(hx[2:4], 16)
        b = int(hx[4:6], 16)
        return (r, g, b)
    except Exception:
        return (255, 255, 255)

def cover_resize(src: Image.Image, W: int, H: int) -> Image.Image:
    """Fill target (COVER): crop overflow, then resize exactly to (W,H)."""
    src_ratio = src.width / src.height
    target_ratio = W / H
    if src_ratio > target_ratio:
        # Crop width
        new_height = src.height
        new_width = int(target_ratio * new_height)
    else:
        # Crop height
        new_width = src.width
        new_height = int(new_width / target_ratio)
    left = (src.width - new_width) // 2
    top = (src.height - new_height) // 2
    crop = src.crop((left, top, left + new_width, top + new_height))
    return crop.resize((W, H), Image.Resampling.LANCZOS)

def contain_resize(src: Image.Image, W: int, H: int) -> Image.Image:
    """Fit inside (CONTAIN): keep aspect ratio; result <= (W,H)."""
    out = src.copy()
    out.thumbnail((W, H), Image.Resampling.LANCZOS)
    return out

def letterbox_canvas(resized: Image.Image, W: int, H: int, transparent: bool, bg_rgb=(255,255,255)):
    """
    Center 'resized' on an exact WxH canvas.
    If transparent=True -> RGBA canvas; else RGB canvas filled with bg_rgb.
    """
    if transparent:
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    else:
        canvas = Image.new("RGB", (W, H), bg_rgb)
    x = (W - resized.width) // 2
    y = (H - resized.height) // 2
    if transparent and resized.mode != "RGBA":
        resized = resized.convert("RGBA")
    canvas.paste(resized, (x, y), resized if resized.mode == "RGBA" else None)
    return canvas

def flatten_if_needed(img: Image.Image, bg_rgb=(255,255,255)) -> Image.Image:
    """Ensure no alpha when saving to JPEG (composite on bg if needed)."""
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, bg_rgb)
        bg.paste(img, mask=img.split()[-1])  # use alpha channel as mask
        return bg
    if img.mode != "RGB":
        return img.convert("RGB")
    return img

def resource_path(relative_path: str) -> str:
    """
    Resolve asset path both for dev and when frozen by PyInstaller.
    """
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def resize_for_platforms(
    input_file,
    output_dir,
    selection,
    mode="cover",                 # "cover" or "contain"
    pad_exact=False,              # only for contain
    transparent_pad=False,        # only for contain+pad and PNG
    bg_hex="#FFFFFF",
    export_fmt="JPEG",            # "JPEG", "PNG", "Both"
    quality=95,
    logger=None
):
    def log(msg):
        (logger or print)(msg)

    os.makedirs(output_dir, exist_ok=True)
    if os.path.basename(os.path.normpath(output_dir)).upper() in RESERVED:
        output_dir = output_dir + "_out"
        os.makedirs(output_dir, exist_ok=True)

    with Image.open(input_file) as img:
        src = img.convert("RGB")  # canonical working mode
        base_name = sanitize_basename(os.path.splitext(os.path.basename(input_file))[0])
        bg_rgb = hex_to_rgb(bg_hex)

        for label, (platform_key, (W, H)) in selection:
            # Produce the base output image according to mode
            if mode == "cover":
                out = cover_resize(src, W, H)
            else:
                resized = contain_resize(src, W, H)
                if pad_exact:
                    out = letterbox_canvas(
                        resized, W, H,
                        transparent=(transparent_pad and (export_fmt in ("PNG", "Both"))),
                        bg_rgb=bg_rgb
                    )
                else:
                    out = resized  # may be smaller than (W,H)

            # Save in chosen format(s)
            if export_fmt in ("JPEG", "Both"):
                out_jpg = flatten_if_needed(out, bg_rgb=bg_rgb)
                jpg_name = f"{base_name}_{platform_key}.jpg"
                if os.path.splitext(jpg_name)[0].upper() in RESERVED:
                    jpg_name = os.path.splitext(jpg_name)[0] + "_img.jpg"
                out_jpg.save(os.path.join(output_dir, jpg_name), "JPEG",
                             quality=quality, optimize=True, progressive=True)
                log(f"Saved: {os.path.join(output_dir, jpg_name)}")

            if export_fmt in ("PNG", "Both"):
                out_png = out if out.mode in ("RGB", "RGBA") else out.convert("RGBA")
                png_name = f"{base_name}_{platform_key}.png"
                if os.path.splitext(png_name)[0].upper() in RESERVED:
                    png_name = os.path.splitext(png_name)[0] + "_img.png"
                out_png.save(os.path.join(output_dir, png_name), "PNG", optimize=True)
                log(f"Saved: {os.path.join(output_dir, png_name)}")

        log("Done! ✅")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SocialResizer")
        self.minsize(780, 700)

        # Try to set app/window icon if available
        try:
            ico_path = resource_path(os.path.join("assets", "social_resizer.ico"))
            if os.path.exists(ico_path):
                # Windows
                self.iconbitmap(ico_path)
        except Exception:
            pass

        # --- State variables ---
        self.input_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "output"))

        # Mode: "cover" or "contain"
        self.mode = tk.StringVar(value="cover")
        self.pad_exact = tk.BooleanVar(value=True)         # only for contain
        self.transparent_pad = tk.BooleanVar(value=False)  # PNG letterbox transparency
        self.bg_color = tk.StringVar(value="#FFFFFF")      # letterbox color

        self.quality = tk.IntVar(value=95)                 # JPEG quality
        self.export_fmt = tk.StringVar(value="JPEG")       # "JPEG", "PNG", "Both"

        # Platform checkboxes
        self.platform_vars = {label: tk.BooleanVar(value=False) for label in SIZES.keys()}

        # Custom sizes: label -> (key, (W,H))
        self.custom_sizes = {}

        self._build_ui()

    # ---------- UI construction ----------
    def _build_ui(self):
        pad = {"padx": 10, "pady": 8}

        # File selection
        frm_file = ttk.LabelFrame(self, text="Source image")
        frm_file.pack(fill="x", **pad)
        row = ttk.Frame(frm_file); row.pack(fill="x", padx=10, pady=10)
        ttk.Entry(row, textvariable=self.input_path).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", command=self.choose_file).pack(side="left", padx=6)

        # Output dir
        frm_out = ttk.LabelFrame(self, text="Output folder")
        frm_out.pack(fill="x", **pad)
        row2 = ttk.Frame(frm_out); row2.pack(fill="x", padx=10, pady=10)
        ttk.Entry(row2, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(row2, text="Choose…", command=self.choose_dir).pack(side="left", padx=6)

        # Presets
        frm_presets = ttk.LabelFrame(self, text="Preset bundles/profiles")
        frm_presets.pack(fill="x", **pad)
        inner = ttk.Frame(frm_presets); inner.pack(fill="x", padx=10, pady=8)
        self.preset_var = tk.StringVar(value="-- Choose preset --")
        self.preset_cb = ttk.Combobox(inner, textvariable=self.preset_var, values=list(PRESETS.keys()), state="readonly")
        self.preset_cb.pack(side="left", fill="x", expand=True)
        ttk.Button(inner, text="Apply preset", command=self.apply_preset).pack(side="left", padx=8)

        # Platforms
        frm_plat = ttk.LabelFrame(self, text="Platforms")
        frm_plat.pack(fill="x", **pad)
        plat_rows = ttk.Frame(frm_plat); plat_rows.pack(fill="x", padx=10, pady=6)
        self.platform_container_left = ttk.Frame(plat_rows); self.platform_container_left.pack(side="left", fill="x", expand=True)
        self.platform_container_right = ttk.Frame(plat_rows); self.platform_container_right.pack(side="left", fill="x", expand=True)
        self._render_platform_checkboxes()

        btns = ttk.Frame(frm_plat); btns.pack(fill="x", padx=10, pady=4)
        ttk.Button(btns, text="Select all", command=self.select_all).pack(side="left")
        ttk.Button(btns, text="Deselect all", command=self.deselect_all).pack(side="left", padx=6)

        # Custom size
        frm_custom = ttk.LabelFrame(self, text="Custom size")
        frm_custom.pack(fill="x", **pad)
        rowc1 = ttk.Frame(frm_custom); rowc1.pack(fill="x", padx=10, pady=6)
        self.custom_name = tk.StringVar(); self.custom_w = tk.StringVar(); self.custom_h = tk.StringVar()
        ttk.Label(rowc1, text="Name:").pack(side="left")
        ttk.Entry(rowc1, width=28, textvariable=self.custom_name).pack(side="left", padx=6)
        ttk.Label(rowc1, text="Width:").pack(side="left")
        ttk.Entry(rowc1, width=8, textvariable=self.custom_w).pack(side="left", padx=6)
        ttk.Label(rowc1, text="Height:").pack(side="left")
        ttk.Entry(rowc1, width=8, textvariable=self.custom_h).pack(side="left", padx=6)
        ttk.Button(rowc1, text="Add", command=self.add_custom_size).pack(side="left", padx=8)

        # Options
        frm_opts = ttk.LabelFrame(self, text="Options")
        frm_opts.pack(fill="x", **pad)

        # Resize mode
        row_mode = ttk.Frame(frm_opts); row_mode.pack(fill="x", padx=10, pady=6)
        ttk.Label(row_mode, text="Mode:").pack(side="left")
        ttk.Radiobutton(row_mode, text="Cover (crop to fill)", variable=self.mode, value="cover").pack(side="left", padx=10)
        ttk.Radiobutton(row_mode, text="Contain (keep aspect)", variable=self.mode, value="contain").pack(side="left", padx=10)

        # Letterbox options (effective for contain)
        row_lb = ttk.Frame(frm_opts); row_lb.pack(fill="x", padx=10, pady=6)
        ttk.Checkbutton(row_lb, text="Pad to exact size (letterbox)", variable=self.pad_exact).pack(side="left")
        ttk.Checkbutton(row_lb, text="Transparent pad (PNG only)", variable=self.transparent_pad).pack(side="left", padx=10)

        # Background color picker
        row_bg = ttk.Frame(frm_opts); row_bg.pack(fill="x", padx=10, pady=6)
        ttk.Label(row_bg, text="Letterbox color:").pack(side="left")
        self.bg_preview = ttk.Label(row_bg, textvariable=self.bg_color, relief="solid", padding=4)
        self.bg_preview.pack(side="left", padx=8)
        ttk.Button(row_bg, text="Pick color…", command=self.pick_color).pack(side="left")

        # Export options
        row_exp = ttk.Frame(frm_opts); row_exp.pack(fill="x", padx=10, pady=6)
        ttk.Label(row_exp, text="Export format:").pack(side="left")
        ttk.Combobox(row_exp, textvariable=self.export_fmt, values=["JPEG", "PNG", "Both"], state="readonly", width=8).pack(side="left", padx=8)
        ttk.Label(row_exp, text="JPEG quality:").pack(side="left", padx=10)
        ttk.Scale(row_exp, from_=60, to=100, orient="horizontal", variable=self.quality).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Label(row_exp, textvariable=self.quality).pack(side="left")

        # Run & log
        run_frame = ttk.Frame(self); run_frame.pack(fill="x", **pad)
        ttk.Button(run_frame, text="Run", command=self.run).pack(side="right")

        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.pack(fill="both", expand=True, **pad)
        self.log_text = tk.Text(log_frame, height=10, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.log("Ready.")

    # ---------- helpers ----------
    def _render_platform_checkboxes(self):
        # Clear
        for w in self.platform_container_left.winfo_children():
            w.destroy()
        for w in self.platform_container_right.winfo_children():
            w.destroy()
        # Combine standard + custom
        labels = list(SIZES.keys()) + list(self.custom_sizes.keys())
        labels.sort()
        half = (len(labels) + 1) // 2
        for lbl in labels[:half]:
            ttk.Checkbutton(self.platform_container_left, text=lbl, variable=self._get_var_for_label(lbl)).pack(anchor="w", pady=2)
        for lbl in labels[half:]:
            ttk.Checkbutton(self.platform_container_right, text=lbl, variable=self._get_var_for_label(lbl)).pack(anchor="w", pady=2)

    def _get_var_for_label(self, lbl):
        if lbl not in self.platform_vars:
            self.platform_vars[lbl] = tk.BooleanVar(value=True)
        return self.platform_vars[lbl]

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Choose image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff"), ("All files", "*.*")]
        )
        if path:
            self.input_path.set(path)

    def choose_dir(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d:
            self.output_dir.set(d)

    def pick_color(self):
        initial = self.bg_color.get()
        (rgb, hx) = colorchooser.askcolor(color=initial, title="Pick letterbox color")
        if hx:
            self.bg_color.set(hx)

    def select_all(self):
        for v in self.platform_vars.values():
            v.set(True)

    def deselect_all(self):
        for v in self.platform_vars.values():
            v.set(False)

    def apply_preset(self):
        preset = self.preset_var.get()
        if preset not in PRESETS:
            return
        self.deselect_all()
        for lbl in PRESETS[preset]:
            if lbl in self.platform_vars:
                self.platform_vars[lbl].set(True)
        self.log(f"Applied preset: {preset}")

    def add_custom_size(self):
        name = self.custom_name.get().strip()
        w = self.custom_w.get().strip()
        h = self.custom_h.get().strip()
        if not name or not w.isdigit() or not h.isdigit():
            messagebox.showwarning("Invalid input", "Enter name, width and height (integers).")
            return
        W, H = int(w), int(h)
        label = f"{name} ({W}×{H})"
        key = f"custom_{name.lower().replace(' ', '_')}_{W}x{H}"
        self.custom_sizes[label] = (key, (W, H))
        self.platform_vars[label] = tk.BooleanVar(value=True)
        self._render_platform_checkboxes()
        self.custom_name.set(""); self.custom_w.set(""); self.custom_h.set("")
        self.log(f"Added custom size: {label}")

    def log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.update_idletasks()

    def run(self):
        input_file = self.input_path.get().strip()
        output_dir = self.output_dir.get().strip()
        if not input_file:
            messagebox.showwarning("Missing file", "Choose a source image first.")
            return
        if not os.path.isfile(input_file):
            messagebox.showerror("Error", "Source image not found.")
            return
        if not output_dir:
            messagebox.showwarning("Missing output folder", "Choose an output folder.")
            return

        # Build selection from checked items (standard + custom)
        selection = []
        for lbl, var in self.platform_vars.items():
            if not var.get():
                continue
            if lbl in SIZES:
                selection.append((lbl, SIZES[lbl]))
            elif lbl in self.custom_sizes:
                selection.append((lbl, self.custom_sizes[lbl]))

        if not selection:
            messagebox.showwarning("No platforms selected", "Select at least one platform.")
            return

        # Validate transparency choice vs export format
        if self.transparent_pad.get() and self.export_fmt.get() == "JPEG" and self.mode.get() == "contain" and self.pad_exact.get():
            self.log("Note: Transparent padding selected but JPEG has no alpha — letterbox color will be used for JPEG.")

        self.log("Processing…")
        try:
            resize_for_platforms(
                input_file=input_file,
                output_dir=output_dir,
                selection=selection,
                mode=self.mode.get(),
                pad_exact=self.pad_exact.get(),
                transparent_pad=self.transparent_pad.get(),
                bg_hex=self.bg_color.get(),
                export_fmt=self.export_fmt.get(),
                quality=int(self.quality.get()),
                logger=self.log
            )
            messagebox.showinfo("Done", "Export completed!")
        except Exception as e:
            messagebox.showerror("Export error", str(e))

def main():
    try:
        app = App()
        app.mainloop()
    except tk.TclError as e:
        sys.stderr.write(f"Tkinter error: {e}\n")

if __name__ == "__main__":
    main()
