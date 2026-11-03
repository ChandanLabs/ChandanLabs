#!/usr/bin/env python3
"""Generate an animated GIF banner for a GitHub profile README."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FRAMES = 1280, 540, 24
OUTPUT = Path("hero.gif")
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
fonts = {
    "small": ImageFont.truetype(BOLD, 10),
    "tag": ImageFont.truetype(BOLD, 13),
    "greeting": ImageFont.truetype(REG, 28),
    "name": ImageFont.truetype(BOLD, 48),
    "role": ImageFont.truetype(BOLD, 20),
    "body": ImageFont.truetype(REG, 17),
    "chip": ImageFont.truetype(BOLD, 12),
    "java": ImageFont.truetype(BOLD, 28),
    "mono": ImageFont.truetype(MONO, 12),
}
NAVY1, NAVY2 = (11, 18, 32), (17, 22, 43)
WHITE, MUTED = (236, 242, 250), (163, 177, 198)
CYAN, VIOLET, MINT = (56, 189, 248), (139, 92, 246), (52, 211, 153)


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def pill(draw, x, y, text, color, font, pad=24, height=30):
    tw = draw.textbbox((0, 0), text, font=font)[2]
    width = tw + pad
    draw.rounded_rectangle((x-width/2, y-height/2, x+width/2, y+height/2),
                           radius=height//2, fill=(13, 23, 38, 250),
                           outline=color+(235,), width=2)
    draw.text((x, y), text, font=font, fill=WHITE, anchor="mm")


def make_frame(index):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        for x in range(W):
            t = min(1.0, max(0.0, x/W*0.58 + y/H*0.42))
            px[x, y] = mix(NAVY1, NAVY2, t)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((820, 70, 1260, 470), fill=(56, 189, 248, 28))
    gd.ellipse((900, 110, 1190, 420), fill=(139, 92, 246, 24))
    img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(48)))
    d = ImageDraw.Draw(img, "RGBA")

    for x in range(30, W, 28):
        for y in range(25, H, 28):
            d.ellipse((x, y, x+1, y+1), fill=(139, 92, 246, 26))
    d.rounded_rectangle((1, 1, W-2, H-2), radius=28,
                        outline=(76, 111, 153, 190), width=2)
    d.line((34, 80, 34, 38, 76, 38), fill=CYAN+(220,), width=3)
    d.line((W-76, 38, W-34, 38, W-34, 80), fill=VIOLET+(220,), width=3)

    d.rounded_rectangle((70, 58, 390, 99), radius=20,
                        fill=(17, 39, 50, 245), outline=CYAN+(125,), width=1)
    pulse = .55 + .45 * math.sin(2*math.pi*index/FRAMES)
    d.ellipse((88, 73, 100, 85), fill=(52, 211, 153, int(90+165*pulse)))
    d.text((115, 78), "JAVA-FIRST  /  QUALITY-FOCUSED",
           font=fonts["small"], fill=(194, 246, 255), anchor="lm")

    d.text((72, 145), "Hi, I'm", font=fonts["greeting"], fill=MUTED)
    d.text((68, 205), "Chandan Kumar", font=fonts["name"], fill=WHITE)
    d.text((68, 261), "Sah Teli", font=fonts["name"], fill=CYAN)
    d.rounded_rectangle((72, 302, 690, 350), radius=13,
                        fill=(16, 26, 43, 245), outline=VIOLET+(150,), width=1)
    d.rounded_rectangle((72, 302, 79, 350), radius=3, fill=CYAN)
    d.text((99, 326), "Java Developer  |  Automation Testing Learner",
           font=fonts["role"], fill=WHITE, anchor="lm")
    d.text((74, 391), "Building backend systems, learning test automation,",
           font=fonts["body"], fill=MUTED)
    d.text((74, 418), "and improving through hands-on practice.",
           font=fonts["body"], fill=MUTED)

    tag_x = 74
    for label, color in (("CORE JAVA", CYAN), ("BACKEND", VIOLET), ("TEST AUTOMATION", MINT)):
        tw = d.textbbox((0, 0), label, font=fonts["tag"])[2]
        d.rounded_rectangle((tag_x, 466, tag_x+tw+30, 501), radius=16,
                            fill=(17, 27, 44, 250), outline=color+(200,), width=1)
        d.text((tag_x+15, 484), label, font=fonts["tag"], fill=color, anchor="lm")
        tag_x += tw + 43

    # Orbit area is deliberately kept separate from the left-hand text.
    d.text((775, 62), "ENGINEERING STACK  /  IN MOTION",
           font=fonts["small"], fill=VIOLET, anchor="lm")
    cx, cy = 1000, 260
    for rad, color in ((92, CYAN), (132, VIOLET), (178, MINT)):
        d.ellipse((cx-rad, cy-rad, cx+rad, cy+rad), outline=color+(85,), width=2)

    d.ellipse((cx-68, cy-68, cx+68, cy+68), fill=(14, 29, 45, 255),
              outline=CYAN+(255,), width=3)
    d.ellipse((cx-54, cy-54, cx+54, cy+54), outline=VIOLET+(180,), width=2)
    d.text((cx, cy-5), "JAVA", font=fonts["java"], fill=WHITE, anchor="mm")
    d.text((cx, cy+26), "PRIMARY", font=fonts["small"], fill=CYAN, anchor="mm")

    inner = (("Spring Boot", CYAN), ("Node.js", CYAN),
             ("Python", VIOLET), ("JavaScript", VIOLET))
    outer = (("Selenium", MINT), ("Playwright", MINT), ("TestNG", MINT),
             ("Cucumber", MINT), ("REST Assured", MINT), ("Postman", MINT),
             ("Maven", MINT), ("GitHub Actions", MINT))
    rotation = 2*math.pi*index/FRAMES
    for n, (label, color) in enumerate(inner):
        a = rotation + n*2*math.pi/len(inner)
        pill(d, cx+132*math.cos(a), cy+132*math.sin(a), label, color, fonts["chip"])
    for n, (label, color) in enumerate(outer):
        a = -rotation*.65 + (n+.5)*2*math.pi/len(outer)
        pill(d, cx+178*math.cos(a), cy+178*math.sin(a), label, color, fonts["chip"])

    d.rounded_rectangle((800, 463, 1205, 516), radius=12,
                        fill=(13, 21, 35, 247), outline=(61, 79, 108, 220), width=1)
    for n, color in enumerate((MINT, VIOLET, CYAN)):
        d.ellipse((819+n*15, 476, 828+n*15, 485), fill=color)
    d.text((819, 499), "class QualityFirst { test(); improve(); }",
           font=fonts["mono"], fill=(190, 211, 235))
    if index % 2 == 0:
        d.rectangle((1177, 489, 1183, 504), fill=MINT)
    return img.convert("RGB")


def main():
    rendered = [make_frame(i) for i in range(FRAMES)]
    common_palette = rendered[0].convert("P", palette=Image.Palette.ADAPTIVE, colors=96)
    frames = [frame.quantize(palette=common_palette, dither=Image.Dither.NONE)
              for frame in rendered]
    frames[0].save(OUTPUT, save_all=True, append_images=frames[1:],
                   duration=120, loop=0, optimize=True, disposal=1)
    print(f"Generated {OUTPUT}: {FRAMES} frames, {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
