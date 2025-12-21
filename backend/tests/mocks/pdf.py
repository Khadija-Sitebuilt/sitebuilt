from PIL import Image

def mock_convert_from_bytes(*args, **kwargs):
    return [Image.new("RGB", (800, 600), "white")]
