""" Image optimization utilities using Pillow. """
import logging
from io import BytesIO
import os
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """
    A utility class for optimizing and resizing images using Pillow (PIL).

    This class provides methods to handle image compression, resizing, and format conversion
    while attempting to preserve quality and metadata like ICC profiles where appropriate.
    It is designed to work with both file paths and file-like objects.
    """

    @staticmethod
    def _determine_quality(width):
        """Determines compression quality based on image width."""
        if width <= 800:
            return 55
        if width <= 1200:
            return 65
        return 70

    @classmethod
    def compress_and_resize(cls,
                            image_path_or_file,
                            output_path=None,
                            width=None,
                            output_format='WEBP',
                            quality=None):
        """
        Compresses and resizes an image using Pillow.

        Args:
            image_path_or_file: Path to the image or a file-like object.
            output_path: Path where to save the result. If None, returns bytes.
            width: Target width. If None, uses original width.
            output_format: Output format (default 'WEBP').
            quality: Compression quality (1-100). If None, calculated based on width.

        Returns:
            bytes if output_path is None, else saves to file.
        """
        try:
            # Open the image
            with Image.open(image_path_or_file) as img:
                # Capture ICC profile before any operations
                original_icc_profile = img.info.get('icc_profile')
                
                # Auto-rotate based on EXIF tag
                img = ImageOps.exif_transpose(img)

                # Resize if needed
                if width and width < img.width:
                    wpercent = width / float(img.width)
                    hsize = int((float(img.height) * float(wpercent)))
                    
                    # Use LANCZOS for high quality downsampling (similar/better to Inter-Area)
                    img = img.resize((width, hsize), Image.Resampling.LANCZOS)

                # Handle Format Specific Conversions
                fmt = output_format.upper()
                
                # Check if we need to convert to RGB (e.g. for JPEG which doesn't support Alpha)
                if fmt == 'JPEG':
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        # Create white background for transparent images
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if img.mode in ('RGBA', 'LA'):
                            background.paste(img, mask=img.split()[-1])
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                
                # For WEBP/PNG, keeping RGBA is fine, but convert 'P' to RGBA/RGB to be safe
                elif img.mode == 'P':
                    img = img.convert('RGBA')

                # Determine Quality settings
                if quality is None:
                    quality = cls._determine_quality(img.width)
                    
                save_kwargs = {
                    'quality': quality,
                    'optimize': True,
                }

                if fmt == 'WEBP':
                    save_kwargs['method'] = 6
                elif fmt == 'JPEG':
                    save_kwargs['progressive'] = True
                elif fmt == 'PNG':
                    save_kwargs['compress_level'] = 9

                if original_icc_profile:
                    save_kwargs['icc_profile'] = original_icc_profile

                # Save
                if output_path:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    img.save(output_path, fmt, **save_kwargs)
                    return True
                else:
                    output = BytesIO()
                    img.save(output, fmt, **save_kwargs)
                    output.seek(0)
                    return output

        except Exception as e:
            logger.error("Error optimizing image: %s", e)
            return None
