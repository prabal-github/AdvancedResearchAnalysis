import os
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap


def load_font(preferred: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in preferred:
        try:
            if os.path.isfile(path):
                return ImageFont.truetype(path, size)
        except Exception:
            continue
    # Fallback to default PIL bitmap font (limited sizing, but avoids crash)
    return ImageFont.load_default()


def render_slide(text: str, out_path: str, width=1600, height=900,
                 title_color=(233, 238, 249), body_color=(200, 215, 240),
                 bg=(15, 19, 32)) -> None:
    # Prepare canvas
    img = Image.new("RGB", (width, height), color=bg)
    draw = ImageDraw.Draw(img)

    # Load fonts (add common Windows fonts first)
    title_font = load_font([
        r"C:\\Windows\\Fonts\\segoeuib.ttf",  # Segoe UI Semibold
        r"C:\\Windows\\Fonts\\segoeui.ttf",
        r"C:\\Windows\\Fonts\\arialbd.ttf",
        r"C:\\Windows\\Fonts\\arial.ttf",
    ], size=60)
    body_font = load_font([
        r"C:\\Windows\\Fonts\\segoeui.ttf",
        r"C:\\Windows\\Fonts\\arial.ttf",
        r"C:\\Windows\\Fonts\\calibri.ttf",
    ], size=36)

    # Try to split first line as title
    lines = text.strip().splitlines()
    title = lines[0].strip() if lines else ""
    content = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    # Draw title
    margin_x = 80
    margin_y = 70
    draw.text((margin_x, margin_y), title, font=title_font, fill=title_color)

    # Prepare wrapped body
    body_top = margin_y + 100
    max_text_width = width - 2 * margin_x

    # Split paragraphs, then wrap each paragraph separately
    paragraphs = [p for p in content.split('\n')]
    y = body_top
    line_spacing = 14

    def measure(text_line: str) -> int:
        # getbbox gives more accurate width/height for truetype fonts
        bbox = draw.textbbox((0, 0), text_line, font=body_font)
        return bbox[2] - bbox[0]

    for para in paragraphs:
        para = para.rstrip()
        if not para:
            y += int(body_font.size * 0.6)  # paragraph spacer
            continue

        # dynamic wrapping by binary search on chars-per-line
        # start with a heuristic chars-per-line guess
        cpl = max(10, int(max_text_width / (body_font.size * 0.55)))
        wrapped = []
        for chunk in wrap(para, cpl):
            # if still too wide, hard-split further
            if measure(chunk) > max_text_width:
                # break by words, enforce width
                words = chunk.split()
                cur = []
                for w in words:
                    test = (" ".join(cur + [w])).strip()
                    if measure(test) <= max_text_width:
                        cur.append(w)
                    else:
                        if cur:
                            wrapped.append(" ".join(cur))
                        cur = [w]
                if cur:
                    wrapped.append(" ".join(cur))
            else:
                wrapped.append(chunk)

        for wline in wrapped:
            if y + body_font.size + line_spacing > height - margin_y:
                # No more vertical space
                break
            draw.text((margin_x, y), wline, font=body_font, fill=body_color)
            y += body_font.size + line_spacing

    # Save
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, format="PNG")


def split_into_slides(text: str, max_lines_first=18, max_lines_other=22) -> list[str]:
    # Split by blank line blocks to keep sections together
    blocks = [b.strip() for b in text.strip().split("\n\n") if b.strip()]
    slides: list[str] = []
    current: list[str] = []
    limit = max_lines_first
    for b in blocks:
        block_lines = b.splitlines()
        if len(current) + len(block_lines) > limit and current:
            slides.append("\n".join(current))
            current = block_lines
            limit = max_lines_other
        else:
            current += block_lines
    if current:
        slides.append("\n".join(current))
    return slides


def generate_png_slides(input_path: str, output_dir: str) -> list[str]:
    with open(input_path, "r", encoding="utf-8") as f:
        raw = f.read()
    # Ensure fonts feel large/readable
    slides_text = split_into_slides(raw)
    out_paths: list[str] = []
    for i, s in enumerate(slides_text, start=1):
        out_file = os.path.join(output_dir, f"slide_{i:02d}.png")
        render_slide(s, out_file)
        out_paths.append(out_file)
    return out_paths


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    input_file = os.path.join(base_dir, "secure_artifacts", "PublishableML", "ShortTerm_RelativeStrength_RotationModel_input.txt")
    out_dir = os.path.join(base_dir, "secure_artifacts", "PublishableML", "slides")
    paths = generate_png_slides(input_file, out_dir)
    print("Generated:")
    for p in paths:
        print(" -", p)
