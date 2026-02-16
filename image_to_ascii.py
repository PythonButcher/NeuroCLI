import sys
from pathlib import Path
from PIL import Image

# Grayscale characters (dense -> sparse)
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def resize_image(image, new_width=120):
    """Resize image preserving aspect ratio."""
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  # 0.55 balances terminal font
    return image.resize((new_width, new_height))

def grayify(image):
    """Convert image to grayscale."""
    return image.convert("L")

def pixels_to_ascii(image):
    """Map pixels to ASCII chars."""
    pixels = image.getdata()
    ascii_str = "".join(ASCII_CHARS[pixel // 25] for pixel in pixels)
    return ascii_str

def convert_image_to_ascii(image_path, new_width=120, output_path=None):
    """Convert image to ASCII and save or print it."""
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Unable to open image file {image_path}: {e}")
        return

    # Process
    image = resize_image(image, new_width)
    gray_image = grayify(image)
    ascii_str = pixels_to_ascii(gray_image)

    # Format into lines
    pixel_count = len(ascii_str)
    ascii_img = "\n".join(
        ascii_str[i:(i + new_width)] for i in range(0, pixel_count, new_width)
    )

    if output_path:
        Path(output_path).write_text(ascii_img, encoding="utf-8")
        print(f"✅ ASCII art written to {output_path}")
    else:
        print(ascii_img)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_to_ascii.py <image_path> [width] [output_file]")
    else:
        img_path = sys.argv[1]
        width = int(sys.argv[2]) if len(sys.argv) >= 3 else 120
        out_file = sys.argv[3] if len(sys.argv) == 4 else None
        convert_image_to_ascii(img_path, new_width=width, output_path=out_file)
