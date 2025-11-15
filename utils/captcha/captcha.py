import random
import string
import uuid
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.cache import cache


def generate_captcha(width=150, height=40, font_size=32, length=5):
    # Generate random text
    text = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    # Create image
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    # Load font
    try:
        font = ImageFont.truetype("./font/RobotoMono-Regular.ttf", font_size)
    except Exception:
        font = ImageFont.load_default(font_size)

    # Optional: Add noise
    for _ in range(5):
        radius = random.randint(3, 10)
        color = tuple(random.randint(100, 200) for _ in range(3))
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius), fill=color, outline=None
        )

    # Calculate text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw the text
    draw.text((x, y), text, fill="black", font=font)

    # Encode to base64
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded_image = base64.b64encode(buffer.getvalue()).decode()

    # Store solution
    key = str(uuid.uuid4())
    cache.set(f"captcha_{key}", text.lower(), timeout=300)

    return key, encoded_image
