""" Image optimization utilities using OpenCV and Pillow. """
import logging
from io import BytesIO
import os
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """
    A utility class for optimizing and resizing images using OpenCV and Pillow (PIL).

    This class provides methods to handle image compression, resizing, and format conversion
    while attempting to preserve quality and metadata like ICC profiles where appropriate.
    It is designed to work with both file paths and file-like objects.
    """

    @staticmethod
    def compress_and_resize(image_path_or_file, output_path=None, width=None, output_format='WEBP'):
        """
        Compresses and resizes an image using OpenCV and PIL.

        Args:
            image_path_or_file: Path to the image or a file-like object.
            output_path: Path where to save the result. If None, returns bytes.
            width: Target width. If None, uses original width.
            output_format: Output format (default 'WEBP').

        Returns:
            bytes if output_path is None, else saves to file.
        """

        try:
            # Handle input: path or file-like object
            if isinstance(image_path_or_file, str):
                pil_img = Image.open(image_path_or_file)
            else:
                pil_img = Image.open(image_path_or_file)

            with pil_img:
                original_icc_profile = pil_img.info.get('icc_profile')

                # Only preserve ICC profile if the image is already in RGB/RGBA mode.
                if pil_img.mode not in ('RGB', 'RGBA'):
                    original_icc_profile = None
                    pil_img = pil_img.convert('RGB')

                img_array = np.array(pil_img)
                if img_array.shape[2] == 4:
                    # Convert RGBA to BGRA using numpy slicing
                    cv_img = img_array[..., [2, 1, 0, 3]]
                else:
                    # Convert RGB to BGR using numpy slicing
                    cv_img = img_array[..., ::-1]

            if cv_img is None:
                return None

            original_height, original_width = cv_img.shape[:2]

            # Determine target dimensions
            if width and width < original_width:
                wpercent = width / float(original_width)
                hsize = int((float(original_height) * float(wpercent)))

                # HIGH QUALITY RESIZING: Area (Better for compression)
                resize = cv2.resize(cv_img, (width, hsize),
                                    interpolation=cv2.INTER_AREA)
            else:
                width = original_width
                resize = cv_img

            # Quality settings
            if width <= 800:
                quality = 55
            elif width <= 1200:
                quality = 65
            else:
                quality = 70

            # Return to Pillow
            if resize.shape[2] == 4:
                # Convert BGRA to RGBA using numpy slicing
                result_rgb = resize[..., [2, 1, 0, 3]]
            else:
                # Convert BGR to RGB using numpy slicing
                result_rgb = resize[..., ::-1]

            pil_result = Image.fromarray(result_rgb)

            # Ensure RGB for JPEG support (Drop Alpha channel if needed) or simple cleanup
            if pil_result.mode == 'RGBA':
                background = Image.new("RGB", pil_result.size, (255, 255, 255))
                background.paste(pil_result, mask=pil_result.split()[3])
                pil_result = background
            elif pil_result.mode != 'RGB':
                pil_result = pil_result.convert('RGB')

            # Prepare save arguments
            save_kwargs = {
                'quality': quality,
                'optimize': True,
            }

            if output_format.upper() == 'WEBP':
                save_kwargs['method'] = 6
            elif output_format.upper() == 'JPEG':
                save_kwargs['progressive'] = True
            elif output_format.upper() == 'PNG':
                save_kwargs['compress_level'] = 9

            if original_icc_profile:
                save_kwargs['icc_profile'] = original_icc_profile

            # Output handling
            if output_path:
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                pil_result.save(output_path, output_format, **save_kwargs)
                return True
            else:
                output = BytesIO()
                pil_result.save(output, output_format, **save_kwargs)
                output.seek(0)
                return output

        except (OSError, ValueError, cv2.error) as e:  # pylint: disable=catching-non-exception
            logger.error("Error optimizing image: %s", e)
            return None
