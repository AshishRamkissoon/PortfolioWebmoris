"""Generate gradient placeholder images for demo content."""

import io

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


def placeholder_image(text, size=(1600, 1000), colors=("#8b5cf6", "#22e3ff"), name="demo.png"):
    width, height = size
    start, end = (Image.new("RGB", (1, 1), c).getpixel((0, 0)) for c in colors)

    # Diagonal gradient: average a vertical and a horizontal ramp, i.e. (x + y) / 2.
    vertical = Image.linear_gradient("L")
    gradient = Image.blend(vertical, vertical.rotate(90), 0.5).resize(size)
    image = Image.composite(Image.new("RGB", size, end), Image.new("RGB", size, start), gradient)

    # Dark wash so the white label stays readable, like a real screenshot frame.
    image = Image.blend(image, Image.new("RGB", size, "#05060a"), 0.35)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=max(24, width // 18))
    box = draw.textbbox((0, 0), text, font=font)
    position = ((width - (box[2] - box[0])) / 2, (height - (box[3] - box[1])) / 2)
    draw.text(position, text, fill="#eef0f6", font=font)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return ContentFile(buffer.getvalue(), name=name)
