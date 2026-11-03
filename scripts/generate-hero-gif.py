#!/usr/bin/env python3
"""Generate a GitHub-README-safe animated Java-first hero banner.

The GIF is used instead of an animated SVG because GitHub documents that
SVG images in repository pages do not support animation.
"""
from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH, HEIGHT = 1280, 540
FRAME_COUNT = 20
OUTPUT = Path("hero.gif")

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def load_font(path: str, size: int):
    return ImageFont.truetype(path, size)


FONT_MICRO = load_font(FONT_BOLD, 10)
FONT_TAG = load_font(FONT_BOLD, 13)
FONT_GREETING = load_font(FONT_REGULAR, 28)
FONT_NAME = load_font(FONT_BOLD, 48)
FONT_ROLE = load_font(FONT_BOLD, 20)
FONT_BODY = load_font(FONT_REGULAR, 17)
FONT_CHIP = load_font(FONT_BOLD, 12)
FONT_JAVA = load_font(FONT_BOLD, 28)
FONT_MONO = load_font(FONT_MONO, 12)

BG_START = (11, 18, 32)
BG_END = (17, 22, 43)
WHITE = (236, 242, 250)
MUTED = (163, 177, 198)
CYAN = (56, 189, 248)
PURPLE = (139, 92, 246)
MINT = (52, 211, 153)


def interpolate(start, end, amount):
    return tuple(
        int(start[index] + (end[index] - start[index]) * amount)
        for index in range(3)
    )


def rounded(draw, bounds, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(
        bounds, radius=radius, fill=fill, outline=outline, width=width
    )


def centered(draw, x, y, value, font, fill):
    draw.text((x, y), value, font=font, fill=fill, anchor="mm")


def draw_frame(frame_index: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()

    for y in range(HEIGHT):
        for x in range(WIDTH):
            amount = max(0, min(1, (x / WIDTH) * 0.58 + (y / HEIGHT) * 0.42))
            pixels[x, y] = interpolate(BG_START, BG_END, amount)

    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((830, 60, 1260, 470), fill=(56, 189, 248, 32))
    glow_draw.ellipse((890, 110, 1200, 430), fill=(139, 92, 246, 23))
    glow = glow.filter(ImageFilter.GaussianBlur(52))
    image = Image.alpha_composite(image.convert("RGBA"), glow)
    draw = ImageDraw.Draw(image, "RGBA")

    # Subtle dotted background and frame accents.
    for x in range(32, WIDTH, 28):
        for y in range(25, HEIGHT, 28):
            draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(139, 92, 246, 30))

    rounded(draw, (1, 1, WIDTH - 2, HEIGHT - 2), 28,
            (0, 0, 0, 0), (76, 111, 153, 190), 2)
    draw.line((34, 80, 34, 38, 76, 38), fill=CYAN + (220,), width=3)
    draw.line((WIDTH - 76, 38, WIDTH - 34, 38, WIDTH - 34, 80),
              fill=PURPLE + (220,), width=3)

    # Java-first identity pill with a subtle pulsing status light.
    rounded(draw, (70, 58, 390, 99), 20,
            (17, 39, 50, 245), (56, 189, 248, 125), 1)
    pulse = 0.55 + 0.45 * math.sin(2 * math.pi * frame_index / FRAME_COUNT)
    draw.ellipse((88, 73, 100, 85),
                 fill=(52, 211, 153, int(90 + 165 * pulse)))
    draw.text((115, 78), "JAVA-FIRST  /  QUALITY-FOCUSED",
              font=FONT_MICRO, fill=(194, 246, 255), anchor="lm")

    # Profile identity and current learning direction.
    draw.text((72, 145), "Hi, I'm", font=FONT_GREETING, fill=MUTED)
    draw.text((68, 205), "Chandan Kumar", font=FONT_NAME, fill=WHITE)
    draw.text((68, 261), "Sah Teli", font=FONT_NAME, fill=CYAN)

    rounded(draw, (72, 302, 690, 350), 13,
            (16, 26, 43, 245), (139, 92, 246, 150), 1)
    draw.rounded_rectangle((72, 302, 79, 350), radius=3, fill=CYAN)
    draw.text((99, 326), "Java Developer  |  Automation Testing Learner",
              font=FONT_ROLE, fill=WHITE, anchor="lm")

    draw.text((74, 391), "Building backend systems, learning test automation,",
              font=FONT_BODY, fill=MUTED)
    draw.text((74, 418), "and improving through hands-on practice.",
              font=FONT_BODY, fill=MUTED)

    tag_x = 74
    for label, color in (
        ("CORE JAVA", CYAN),
        ("BACKEND", PURPLE),
        ("TEST AUTOMATION", MINT),
    ):
        text_width = draw.textbbox((0, 0), label, font=FONT_TAG)[2]
        rounded(draw, (tag_x, 466, tag_x + text_width + 30, 501), 16,
                (17, 27, 44, 250), color + (200,), 1)
        draw.text((tag_x + 15, 484), label, font=FONT_TAG,
                  fill=color, anchor="lm")
        tag_x += text_width + 43

    # Rotating technology orbit. Java remains fixed at its centre.
    draw.text((775, 64), "ENGINEERING STACK  /  IN MOTION",
              font=FONT_MICRO, fill=PURPLE, anchor="lm")
    center_x, center_y = 1000, 254
    for radius, color in ((125, CYAN), (190, PURPLE), (226, MINT)):
        draw.ellipse(
            (center_x - radius, center_y - radius,
             center_x + radius, center_y + radius),
            outline=color + (78,), width=2
        )

    draw.ellipse((center_x - 68, center_y - 68,
                  center_x + 68, center_y + 68),
                 fill=(14, 29, 45, 255), outline=CYAN + (255,), width=3)
    draw.ellipse((center_x - 54, center_y - 54,
                  center_x + 54, center_y + 54),
                 outline=PURPLE + (180,), width=2)
    centered(draw, center_x, center_y - 5, "JAVA", FONT_JAVA, WHITE)
    centered(draw, center_x, center_y + 26, "PRIMARY", FONT_MICRO, CYAN)

    inner_tools = (
        ("Spring Boot", CYAN),
        ("Node.js", CYAN),
        ("Python", PURPLE),
        ("JavaScript", PURPLE),
    )
    outer_tools = (
        ("Selenium", MINT),
        ("Playwright", MINT),
        ("TestNG", MINT),
        ("Cucumber", MINT),
        ("REST Assured", MINT),
        ("Postman", MINT),
        ("Maven", MINT),
        ("GitHub Actions", MINT),
    )
    rotation = 2 * math.pi * frame_index / FRAME_COUNT

    for index, (label, color) in enumerate(inner_tools):
        angle = rotation + index * 2 * math.pi / len(inner_tools)
        x = center_x + 125 * math.cos(angle)
        y = center_y + 125 * math.sin(angle)
        text_width = draw.textbbox((0, 0), label, font=FONT_CHIP)[2]
        box_width, box_height = text_width + 27, 30
        rounded(draw, (x - box_width / 2, y - box_height / 2,
                       x + box_width / 2, y + box_height / 2), 14,
                (13, 23, 38, 252), color + (235,), 2)
        centered(draw, x, y, label, FONT_CHIP, WHITE)

    for index, (label, color) in enumerate(outer_tools):
        angle = -rotation * 0.70 + (index + 0.5) * 2 * math.pi / len(outer_tools)
        x = center_x + 226 * math.cos(angle)
        y = center_y + 226 * math.sin(angle)
        text_width = draw.textbbox((0, 0), label, font=FONT_CHIP)[2]
        box_width, box_height = text_width + 24, 29
        rounded(draw, (x - box_width / 2, y - box_height / 2,
                       x + box_width / 2, y + box_height / 2), 14,
                (13, 23, 38, 252), color + (235,), 2)
        centered(draw, x, y, label, FONT_CHIP, WHITE)

    # Small terminal panel and blinking caret.
    rounded(draw, (810, 445, 1200, 510), 13,
            (13, 21, 35, 247), (61, 79, 108, 220), 1)
    for index, color in enumerate((MINT, PURPLE, CYAN)):
        draw.ellipse((828 + index * 15, 457, 837 + index * 15, 466),
                     fill=color)
    draw.text((830, 485), "class QualityFirst { test(); improve(); }",
              font=FONT_MONO, fill=(190, 211, 235))
    if frame_index % 2 == 0:
        draw.rectangle((1174, 474, 1180, 490), fill=MINT)

    return image.convert("RGB")


def main():
    rgb_frames = [draw_frame(index) for index in range(FRAME_COUNT)]
    shared_palette = rgb_frames[0].convert(
        "P", palette=Image.Palette.ADAPTIVE, colors=96
    )
    frames = [
        image.quantize(palette=shared_palette, dither=Image.Dither.NONE)
        for image in rgb_frames
    ]
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=120,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"Generated {OUTPUT} with {FRAME_COUNT} frames ({OUTPUT.stat().st_size} bytes).")


if __name__ == "__main__":
    main()
