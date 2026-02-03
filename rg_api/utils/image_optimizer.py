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
    def _load_files_to_cv2(image_path_or_file):
        """
        Loads an image from path or file object into OpenCV format (numpy array).
        Returns the OpenCV image and the ICC profile (if applicable).
        """
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
            # Handle RGBA/RGB conversions to BGR (OpenCV standard)
            if img_array.shape[2] == 4:
                # Convert RGBA to BGRA using numpy slicing
                cv_img = img_array[..., [2, 1, 0, 3]]
            else:
                # Convert RGB to BGR using numpy slicing
                cv_img = img_array[..., ::-1]

        return cv_img, original_icc_profile

    @staticmethod
    def _resize_cv2(cv_img, width):
        """Resizes the OpenCV image using partial interpolation."""
        original_height, original_width = cv_img.shape[:2]

        if width and width < original_width:
            wpercent = width / float(original_width)
            hsize = int((float(original_height) * float(wpercent)))

            # HIGH QUALITY RESIZING: Area (Better for compression)
          
            return cv2.resize(cv_img, (width, hsize),
                              interpolation=cv2.INTER_AREA)

        return cv_img

    @staticmethod
    def _determine_quality(width):
        """Determines compression quality based on image width."""
        if width <= 800:
            return 55
        if width <= 1200:
            return 65
        return 70

    @staticmethod
    def _convert_cv2_to_pil(cv_img):
        """Converts an OpenCV image back to a Pillow Image."""
        if cv_img.shape[2] == 4:
            # Convert BGRA to RGBA using numpy slicing
            result_rgb = cv_img[..., [2, 1, 0, 3]]
        else:
            # Convert BGR to RGB using numpy slicing
            result_rgb = cv_img[..., ::-1]

        pil_result = Image.fromarray(result_rgb)

        # Ensure RGB for standard format compatibility (e.g. JPEG)
        if pil_result.mode == 'RGBA':
            background = Image.new("RGB", pil_result.size, (255, 255, 255))
            background.paste(pil_result, mask=pil_result.split()[3])
            pil_result = background
        elif pil_result.mode != 'RGB':
            pil_result = pil_result.convert('RGB')

        return pil_result

    @staticmethod
    def _save_image(pil_img, output_path, output_format, settings_kwargs):
        """Saves the PIL image to items path or bytes."""
        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pil_img.save(output_path, output_format, **settings_kwargs)
            return True

        output = BytesIO()
        pil_img.save(output, output_format, **settings_kwargs)
        output.seek(0)
        return output

    @classmethod
    def compress_and_resize(cls,
                            image_path_or_file,
                            output_path=None,
                            width=None,
                            output_format='WEBP'):
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
            cv_img, original_icc_profile = cls._load_files_to_cv2(
                image_path_or_file)

            if cv_img is None:
                return None

            resize = cls._resize_cv2(cv_img, width)
            pil_result = cls._convert_cv2_to_pil(resize)

            # Determine final width for quality calculation
            # Use original width if resize width wasn't applied or was None
            final_width = width if width else cv_img.shape[1]
            quality = cls._determine_quality(final_width)

            save_kwargs = {
                'quality': quality,
                'optimize': True,
            }

            fmt = output_format.upper()
            if fmt == 'WEBP':
                save_kwargs['method'] = 6
            elif fmt == 'JPEG':
                save_kwargs['progressive'] = True
            elif fmt == 'PNG':
                save_kwargs['compress_level'] = 9

            if original_icc_profile:
                save_kwargs['icc_profile'] = original_icc_profile

            return cls._save_image(pil_result, output_path, output_format, save_kwargs)

      
        except (OSError, ValueError, cv2.error) as e:
            logger.error("Error optimizing image: %s", e)
            return None
