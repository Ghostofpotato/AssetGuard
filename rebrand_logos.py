from PIL import Image, ImageDraw, ImageFont
import struct, zlib, os

# ── AG Logo generators ─────────────────────────────────────────

def make_ag_png(width, height, path):
    img = Image.new("RGBA", (width, height), (18, 18, 18, 255))
    draw = ImageDraw.Draw(img)
    # Green AG text centered
    font_size = int(min(width, height) * 0.45)
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()
    text = "AG"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) / 2 - bbox[0]
    y = (height - th) / 2 - bbox[1]
    draw.text((x, y), text, fill=(0, 200, 100, 255), font=font)
    img.save(path, format="PNG")
    print(f"  [PNG] {path}")

def make_ag_jpg(width, height, path):
    img = Image.new("RGB", (width, height), (18, 18, 18))
    draw = ImageDraw.Draw(img)
    font_size = int(min(width, height) * 0.45)
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()
    text = "AG"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) / 2 - bbox[0]
    y = (height - th) / 2 - bbox[1]
    draw.text((x, y), text, fill=(0, 200, 100), font=font)
    img.save(path, format="JPEG", quality=95)
    print(f"  [JPG] {path}")

def make_ag_ico(path):
    sizes = [16, 32, 48, 256]
    imgs = []
    for size in sizes:
        img = Image.new("RGBA", (size, size), (18, 18, 18, 255))
        draw = ImageDraw.Draw(img)
        font_size = int(size * 0.45)
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            font = ImageFont.load_default()
        text = "AG"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (size - tw) / 2 - bbox[0]
        y = (size - th) / 2 - bbox[1]
        draw.text((x, y), text, fill=(0, 200, 100, 255), font=font)
        imgs.append(img)
    imgs[0].save(path, format="ICO", sizes=[(s, s) for s in sizes], append_images=imgs[1:])
    print(f"  [ICO] {path}")

# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🎨 Generating AssetGuard logos...\n")

    # Installer banner (typically 493x58 or similar wide format)
    make_ag_jpg(493, 58,  r"src\win32\ui\bannrbmp.jpg")

    # Installer dialog background (typically 493x312)
    make_ag_jpg(493, 312, r"src\win32\ui\dlgbmp.jpg")

    # Favicons
    make_ag_ico(r"src\win32\ui\favicon.ico")
    make_ag_ico(r"src\win32\favicon.ico")

    # Installer icons
    make_ag_ico(r"src\win32\install.ico")
    make_ag_ico(r"src\win32\uninstall.ico")

    print("\n✅ All logos replaced!")