""" ImageGallery model for storing images and their metadata in galleries. """
import logging
from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils.html import mark_safe

from gallery.models import Gallery
from gallery.exif_utils import get_gps_data
from PIL import Image, ExifTags
from taggit.managers import TaggableManager

logger = logging.getLogger(__name__)


class ImageGallery(models.Model):
    """
    Model representing an image within a gallery.

    This model stores metadata for images including EXIF data extracted from the image file.
    Images are organized into galleries and can be tagged. The model automatically extracts
    and stores technical photography metadata such as camera settings, lens information,
    and GPS coordinates when available.

    Attributes:
        title (CharField): The title of the image.
        image (ImageField): The image file.
        gallery (ForeignKey): Reference to the parent Gallery.
        tags (TaggableManager): Tags associated with the image.
        width (IntegerField): Image width in pixels.
        height (IntegerField): Image height in pixels.
        author (ForeignKey): The user who uploaded the image.
        created_at (DateTimeField): Timestamp when the image was created.
        updated_at (DateTimeField): Timestamp when the image was last updated.
        camera_model (CharField): Camera model extracted from EXIF data.
        lens_model (CharField): Lens model extracted from EXIF data.
        iso_speed (IntegerField): ISO speed setting extracted from EXIF data.
        aperture_f_number (FloatField): F-number aperture value extracted from EXIF data.
        shutter_speed (FloatField): Shutter speed in seconds extracted from EXIF data.
        focal_length (FloatField): Focal length in mm extracted from EXIF data.
        artist (CharField): Artist name extracted from EXIF data.
        copyright (CharField): Copyright information extracted from EXIF data.
        latitude (FloatField): GPS latitude coordinate.
        longitude (FloatField): GPS longitude coordinate.
        altitude (FloatField): GPS altitude in meters.
        location (CharField): Human-readable location name.
        date (DateTimeField): Original photo capture date extracted from EXIF data.
    """
    title = models.CharField(max_length=250, null=False, blank=False)
    image = models.ImageField(
        null=False
    )
    gallery = models.ForeignKey(
        Gallery, related_name='images', on_delete=models.CASCADE)

    tags = TaggableManager(blank=True)

    width = models.IntegerField()
    height = models.IntegerField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    camera_model = models.CharField(max_length=250, blank=True)
    lens_model = models.CharField(max_length=250, blank=True)
    iso_speed = models.IntegerField(null=True, blank=True)
    aperture_f_number = models.FloatField(null=True, blank=True)
    shutter_speed = models.FloatField(null=True, blank=True)
    focal_length = models.FloatField(null=True, blank=True)

    artist = models.CharField(max_length=250, blank=True)
    copyright = models.CharField(max_length=250, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=250, blank=True)

    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.title)

    def image_tag(self):
        """
        Generates an HTML image tag for the gallery image.

        Returns:
            str: A safe HTML string containing an <img> tag with a constructed source URL 
             pointing to the image generator, or an empty string if no image exists.
        """
        return mark_safe(
            f'<img src="{settings.IMAGE_GENERATOR_BASE_URL}/{self.pk}/width/700" width="150" />'
        ) if self.image else ''

    image_tag.short_description = 'Image Preview'

    def save(self, *args, **kwargs):
        """Save method with image metadata extraction."""
        if self.image:
            try:
                with Image.open(self.image) as img:
                    width, height = img.size
                    self.width = width
                    self.height = height

                    exif_data = img.getexif()
                    if exif_data:
                        self.extract_exif_data(exif_data)

                    # Extract GPS data
                    # Passed 'img' directly since get_gps_data now supports it
                    try:
                        lat, lon, alt = get_gps_data(img)
                        if lat is not None:
                            self.latitude = lat
                        if lon is not None:
                            self.longitude = lon
                        if alt is not None:
                            self.altitude = alt
                    except (ValueError, TypeError, AttributeError, KeyError) as e:
                        logger.error(
                            "Error extracting GPS data for image %s: %s", self.title, e)

            except (OSError, ValueError, TypeError, AttributeError) as e:
                logger.error("Error processing image %s: %s", self.title, e)

        super().save(*args, **kwargs)

    def extract_exif_data(self, exif_data):
        """
        Extract EXIF metadata from image data and populate instance attributes.

        This method parses EXIF data from an image and maps it to corresponding
        instance attributes. It handles various EXIF tag types including rational
        numbers, tuples, and Pillow IFDRational objects. Special handling is provided
        for shutter speed (preferring ExposureTime over ShutterSpeedValue APEX value),
        date formatting, and numeric fields like aperture and focal length.

        Args:
            exif_data (dict): A dictionary of EXIF tags and their values, typically
                obtained from PIL Image._getexif() or Image.getexif().

        Side Effects:
            Updates instance attributes based on EXIF data:
            - camera_model, lens_model, iso_speed, aperture_f_number
            - focal_length, artist, date, copyright, shutter_speed
            Invalid or missing EXIF data is silently ignored.
        """
        # Create a dictionary from the top-level EXIF data
        combined_exif = dict(exif_data)

        # Merge specific IFDs if available (Exif Private IFD)
        # 0x8769 = 34665 (Exif Offset)
        if hasattr(exif_data, 'get_ifd'):
            exif_ifd = exif_data.get_ifd(0x8769)
            if exif_ifd:
                combined_exif.update(exif_ifd)

        # Update exif_data reference to use the combined dictionary
        exif_data = combined_exif

        exif_mapping = {
            'Model': 'camera_model',
            'LensModel': 'lens_model',
            'ISOSpeedRatings': 'iso_speed',
            'FNumber': 'aperture_f_number',
            'FocalLength': 'focal_length',
            'Artist': 'artist',
            'DateTimeOriginal': 'date',
            'Copyright': 'copyright'
        }

        def get_float(val):
            try:
                # Handle tuple/list (numerator, denominator)
                if isinstance(val, (tuple, list)) and len(val) == 2:
                    if float(val[1]) != 0:
                        return float(val[0]) / float(val[1])
                    return 0.0
                # Handle Pillow IFDRational (has numerator/denominator attrs)
                if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
                    return float(val)
                return float(val)
            except (ValueError, TypeError):
                return None

        # Handle Shutter Speed Priority: ExposureTime (33434) > ShutterSpeedValue (37377)
        exp_time = exif_data.get(33434)
        shutter_val = exif_data.get(37377)

        if exp_time:
            self.shutter_speed = get_float(exp_time)
        elif shutter_val:
            apex = get_float(shutter_val)
            if apex is not None:
                self.shutter_speed = 1 / (2 ** apex)

        for key, val in exif_data.items():
            tag_name = ExifTags.TAGS.get(key)
            if tag_name:
                attribute = exif_mapping.get(tag_name)
                if attribute:
                    if attribute == 'date':
                        try:
                            self.date = datetime.strptime(
                                str(val), '%Y:%m:%d %H:%M:%S')
                        except (ValueError, TypeError):
                            # Invalid or unexpected EXIF date format;
                            # ignore and leave self.date unset
                            logger.debug(
                                "Unable to parse EXIF DateTimeOriginal value %r for image %s",
                                val,
                                getattr(self, "id", None),
                            )
                    elif attribute in ['aperture_f_number', 'focal_length']:
                        f_val = get_float(val)
                        if f_val is not None:
                            setattr(self, attribute, f_val)
                    else:
                        setattr(self, attribute, val)

    class Meta:
        """
        Metadata configuration for the Image model.

        Configures the plural display name and database indexes for optimized querying
        on frequently filtered fields (title, created_at, and date).
        """
        verbose_name_plural = 'images'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['created_at']),
            models.Index(fields=['date']),
        ]
