"""Generate a high-resolution, modern editorial OpenGraph Image (1200x630) for Creavora.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_og_image(output_path: str = "docs/og-image.png") -> None:
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), (10, 12, 16, 255))
    draw = ImageDraw.Draw(img)

    # 1. Very subtle tech grid (low opacity)
    grid_color = (20, 26, 38, 255)
    for x in range(0, W, 48):
        draw.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(0, H, 48):
        draw.line([(0, y), (W, y)], fill=grid_color, width=1)

    # Subtle ambient gradient/card in center
    card_margin_x, card_margin_y = 48, 48
    draw.rounded_rectangle(
        [(card_margin_x, card_margin_y), (W - card_margin_x, H - card_margin_y)],
        radius=24,
        fill=(13, 16, 23, 230),
        outline=(30, 41, 59, 255),
        width=1,
    )

    # Inner amber highlight border
    draw.line([(card_margin_x + 24, card_margin_y), (card_margin_x + 240, card_margin_y)], fill=(245, 158, 11, 200), width=2)

    # Fonts
    font_brand = None
    font_headline = None
    font_bold = None
    font_desc = None
    font_mono = None
    font_small = None

    for fn in ["georgiab.ttf", "segoeuib.ttf", "arialbd.ttf"]:
        try:
            font_brand = ImageFont.truetype(fn, 60)
            font_headline = ImageFont.truetype(fn, 44)
            font_bold = ImageFont.truetype(fn, 28)
            break
        except Exception:
            pass

    for fn in ["consola.ttf", "cour.ttf"]:
        try:
            font_mono = ImageFont.truetype(fn, 16)
            break
        except Exception:
            pass

    for fn in ["segoeui.ttf", "arial.ttf"]:
        try:
            font_desc = ImageFont.truetype(fn, 24)
            font_small = ImageFont.truetype(fn, 18)
            break
        except Exception:
            pass

    if not font_brand:
        font_brand = ImageFont.load_default()
        font_headline = font_brand
        font_bold = font_brand
        font_desc = font_brand
        font_mono = font_brand
        font_small = font_brand

    # 2. Top Header Elements
    # Geometric Creavora Mark:
    # Outer dark circle with amber crescent
    icon_x, icon_y = 96, 96
    draw.ellipse([(icon_x, icon_y), (icon_x + 44, icon_y + 44)], fill=(22, 28, 42, 255), outline=(245, 158, 11, 160), width=2)
    draw.ellipse([(icon_x + 10, icon_y + 10), (icon_x + 34, icon_y + 34)], fill=(245, 158, 11, 255))
    draw.ellipse([(icon_x + 18, icon_y + 8), (icon_x + 38, icon_y + 28)], fill=(13, 16, 23, 255))

    # Brand Title
    draw.text((icon_x + 60, icon_y - 8), "Creavora", fill=(248, 250, 252, 255), font=font_brand)
    
    # Amber period
    c_bbox = draw.textbbox((icon_x + 60, icon_y - 8), "Creavora", font=font_brand)
    draw.ellipse([(c_bbox[2] + 4, c_bbox[3] - 16), (c_bbox[2] + 16, c_bbox[3] - 4)], fill=(245, 158, 11, 255))

    # Badge Pill (Right aligned): "06:00 WIB DAILY • 100% FREE"
    badge_text = "DAILY AT 06:00 WIB // 100% FREE"
    badge_w = 340
    badge_h = 40
    b_x = W - 96 - badge_w
    b_y = icon_y + 4
    draw.rounded_rectangle([(b_x, b_y), (b_x + badge_w, b_y + badge_h)], radius=20, fill=(20, 25, 36, 255), outline=(51, 65, 85, 255), width=1)
    draw.text((b_x + 24, b_y + 10), badge_text, fill=(245, 158, 11, 255), font=font_mono)

    # 3. Main Editorial Headline
    head_y = 200
    draw.text((96, head_y), "The Technical AI Intelligence You Read", fill=(241, 245, 249, 255), font=font_headline)
    draw.text((96, head_y + 56), "Before Your First Commit.", fill=(245, 158, 11, 255), font=font_headline)

    # 4. High-Density Pitch Description
    desc_y = 330
    desc_lines = [
        "Autonomous 3-minute morning briefings filtering arXiv preprints,",
        "frontier model architectures, GPU kernels, and developer tools.",
        "Strictly zero PR hype. 100% hard engineering signal.",
    ]
    for i, line in enumerate(desc_lines):
        draw.text((96, desc_y + (i * 36)), line, fill=(148, 163, 184, 255), font=font_desc)

    # 5. Bottom Metadata Bar & Pillars
    bar_y = 485
    draw.line([(96, bar_y), (W - 96, bar_y)], fill=(30, 41, 59, 255), width=1)

    pillars = [
        "[+] arXiv Preprints",
        "[+] Model Architectures",
        "[+] Developer Tools & Kernels",
    ]
    cur_x = 96
    for p in pillars:
        draw.text((cur_x, bar_y + 24), p, fill=(148, 163, 184, 255), font=font_mono)
        cur_x += 270

    # Domain Pill CTA
    cta_domain = "creavora.my.id ->"
    draw.text((W - 96 - 190, bar_y + 22), cta_domain, fill=(245, 158, 11, 255), font=font_mono)

    out_file = Path(output_path)
    out_file.parent.mkdir(exist_ok=True)
    img.save(out_file, "PNG", optimize=True)
    print(f"Generated clean OG Image at {out_file.resolve()}")

if __name__ == "__main__":
    generate_og_image()
