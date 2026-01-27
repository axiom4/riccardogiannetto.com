import logging
from PIL import Image, ExifTags

logger = logging.getLogger(__name__)


def to_float(value):
    if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
        if value.denominator == 0:
            return 0.0
        return float(value.numerator) / float(value.denominator)
    try:
        return float(value)
    except (ValueError, TypeError):
        # Fallback for tuple encoding (num, den)
        if hasattr(value, '__getitem__') and len(value) == 2:
            try:
                if value[1] == 0:
                    return 0.0
                return float(value[0]) / float(value[1])
            except (ValueError, TypeError):
                pass
        return 0.0


def get_decimal_from_dms(dms, ref):
    degrees = to_float(dms[0])
    minutes = to_float(dms[1])
    seconds = to_float(dms[2])

    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

    if ref in ['S', 'W']:
        decimal = -decimal

    return decimal


def get_gps_data(image_path):
    try:
        with Image.open(image_path) as image:
            exif_data = {}
            if hasattr(image, '_getexif'):
                exif_info = image._getexif()
                if exif_info:
                    for tag, value in exif_info.items():
                        decoded = ExifTags.TAGS.get(tag, tag)
                        exif_data[decoded] = value

            if 'GPSInfo' in exif_data:
                gps_info = exif_data['GPSInfo']

                # GPS tags are often keys in a dictionary inside GPSInfo
                gps_latitude = gps_info.get(2)  # GPSLatitude
                gps_latitude_ref = gps_info.get(1)  # GPSLatitudeRef
                gps_longitude = gps_info.get(4)  # GPSLongitude
                gps_longitude_ref = gps_info.get(3)  # GPSLongitudeRef
                gps_altitude = gps_info.get(6)  # GPSAltitude

                lat = None
                lon = None
                alt = None

                if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                    try:
                        lat = get_decimal_from_dms(gps_latitude, gps_latitude_ref)
                        lon = get_decimal_from_dms(
                            gps_longitude, gps_longitude_ref)
                    except Exception as e:
                        logger.error(f"Error converting DMS: {e}")

                if gps_altitude:
                    try:
                        alt = to_float(gps_altitude)
                    except Exception:
                        pass

                return lat, lon, alt

    except Exception as e:
        logger.error(f"Error extracting EXIF data: {e}")
        return None, None, None

    return None, None, None
