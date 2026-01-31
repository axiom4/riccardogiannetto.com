""" Utility functions for extracting and converting EXIF GPS data from images. """
import logging
from PIL import Image

logger = logging.getLogger(__name__)


def to_float(value):
    """
    Converts a given value to a floating-point number.

    This function handles various types of input commonly found in EXIF data processing:
    - Objects with 'numerator' and 'denominator' attributes (e.g., rational numbers).
    - Standard numeric types (int, float, string representation of numbers).
    - Tuples or lists containing two elements representing (numerator, denominator).

    Args:
        value: The input value to convert. Can be a numeric type.

    Returns:
        float: The floating-point representation of the input. Returns 0.0 if the
               conversion fails or if a denominator is zero.
    """
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
    """
    converts DMS (Degrees, Minutes, Seconds) coordinates to decimal degrees.

    Calculates the decimal value from the DMS components and adjusts the sign
    based on the cardinal direction reference. South ('S') and West ('W')
    coordinates result in negative decimal values.

    Args:
        dms (tuple or list): A sequence containing (degrees, minutes, seconds)
            where each element can be converted to a float.
        ref (str): The cardinal reference direction (e.g., 'N', 'S', 'E', 'W').

    Returns:
        float: The coordinate value in decimal degrees.
    """
    degrees = to_float(dms[0])
    minutes = to_float(dms[1])
    seconds = to_float(dms[2])

    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

    if ref in ['S', 'W']:
        decimal = -decimal

    return decimal


def get_gps_data(image_input):
    """
    Extracts GPS latitude, longitude, and altitude from an image's EXIF data.

    Args:
        image_input: The file path to the image, or a PIL Image object.

    Returns:
        tuple: (latitude, longitude, altitude)
    """
    img = None
    should_close = False

    try:
        if isinstance(image_input, Image.Image):
            img = image_input
        else:
            img = Image.open(image_input)
            should_close = True

        gps_info = {}
        if hasattr(img, 'getexif'):
            exif = img.getexif()
            if exif:
                # Retrieve the GPS IFD (tag 0x8825 / 34853)
                gps_info = exif.get_ifd(0x8825)

        # Check if we got valid GPS data
        if gps_info:
            gps_latitude = gps_info.get(2)
            gps_latitude_ref = gps_info.get(1)
            gps_longitude = gps_info.get(4)
            gps_longitude_ref = gps_info.get(3)
            gps_altitude = gps_info.get(6)

            lat = None
            lon = None
            alt = None

            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                try:
                    lat = get_decimal_from_dms(gps_latitude, gps_latitude_ref)
                    lon = get_decimal_from_dms(
                        gps_longitude, gps_longitude_ref)
                except (ValueError, TypeError, IndexError) as e:
                    logger.error("Error converting DMS: %s", e)

            if gps_altitude:
                try:
                    alt = to_float(gps_altitude)
                except (ValueError, TypeError) as e:
                    logger.error("Error converting altitude: %s", e)

            return lat, lon, alt

    except (IOError, OSError, ValueError, TypeError, AttributeError, IndexError) as e:
        logger.error("Error extracting EXIF data: %s", e)
    finally:
        if should_close and img:
            img.close()

    return None, None, None
