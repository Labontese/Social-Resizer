# assets/make_icon.py
from PIL import Image, ImageDraw, ImageFont

def gradient_rect(w, h, c1=(0x5B,0x8D,0xEF), c2=(0x7C,0x3A,0xED)):
    base = Image.new("RGB", (w, h), c1)
    top = Image.new("RGB", (w, h), c2)
    mask = Image.linear_gradient("L").resize((w, h))
    return Image.composite(top, base, mask)

def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, w, h], radius=r, fill=255)
    return m

def main():
    W = H = 512
    bg = gradient_rect(W, H)
    mask = rounded_mask(W, H, r=100)
    icon = Image.new("RGBA", (W, H), (0,0,0,0))
    icon.paste(bg, (0,0), mask)

    d = ImageDraw.Draw(icon)
    # Try common fonts; fallback to default
    for fname in ("segoeuib.ttf", "arial.ttf"):
        try:
            font = ImageFont.truetype(fname, 260)
            break
        except:
            font = None
    if font is None:
        font = ImageFont.load_default()

    text = "SR"
    tw, th = d.textsize(text, font=font)
    x = (W - tw)//2
    y = (H - th)//2 - 10
    d.text((x+4, y+6), text, font=font, fill=(0,0,0,100))       # subtle shadow
    d.text((x, y), text, font=font, fill=(255,255,255,255))     # foreground

    icon.save("social_resizer.png", "PNG")
    icon.resize((256,256), Image.Resampling.LANCZOS).save(
        "social_resizer.ico", format="ICO",
        sizes=[(256,256),(128,128),(64,64),(32,32),(16,16)]
    )
    print("Saved social_resizer.png and social_resizer.ico")

if __name__ == "__main__":
    main()
