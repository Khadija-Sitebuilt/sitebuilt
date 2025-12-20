# app/utils/exif.py

from PIL import Image
import piexif
from datetime import datetime


def _convert_to_degrees(value):
    d = value[0][0] / value[0][1]
    m = value[1][0] / value[1][1]
    s = value[2][0] / value[2][1]
    return d + (m / 60.0) + (s / 3600.0)


def extract_exif(file_path: str):
    try:
        img = Image.open(file_path)
        exif_data = piexif.load(img.info.get("exif", b""))
    except Exception:
        return None, None, None

    lat = lng = timestamp = None

    gps = exif_data.get("GPS", {})
    if gps:
        lat_ref = gps.get(piexif.GPSIFD.GPSLatitudeRef)
        lat_val = gps.get(piexif.GPSIFD.GPSLatitude)
        lng_ref = gps.get(piexif.GPSIFD.GPSLongitudeRef)
        lng_val = gps.get(piexif.GPSIFD.GPSLongitude)

        if lat_ref and lat_val and lng_ref and lng_val:
            lat = _convert_to_degrees(lat_val)
            if lat_ref == b"S":
                lat = -lat

            lng = _convert_to_degrees(lng_val)
            if lng_ref == b"W":
                lng = -lng

    exif_time = exif_data.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal)
    if exif_time:
        try:
            timestamp = datetime.strptime(
                exif_time.decode(), "%Y:%m:%d %H:%M:%S"
            )
        except Exception:
            pass

    return lat, lng, timestamp
