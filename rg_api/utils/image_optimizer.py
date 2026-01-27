import os
import cv2
import numpy as np
import logging
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


class ImageOptimizer:
    @staticmethod
    def compress_and_resize(image_path_or_file, output_path=None, width=None, format='WEBP'):
        """
        Compresses and resizes an image using OpenCV and PIL.

        Args:
            image_path_or_file: Path to the image or a file-like object.
            output_path: Path where to save the result. If None, returns bytes.
            width: Target width. If None, uses original width.
            format: Output format (default 'WEBP').

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
                    cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
                else:
                    cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            if cv_img is None:
                return None

            original_height, original_width = cv_img.shape[:2]

            # Determine target dimensions
            if width and width < original_width:
                wpercent = (width / float(original_width))
                hsize = int((float(original_height) * float(wpercent)))

                # HIGH QUALITY RESIZING: Area (Better for compression)
                resize = cv2.resize(cv_img, (width, hsize),
                                    interpolation=cv2.INTER_AREA)
            else:
                width = original_width
                resize = cv_img

            # Quality settings
            if width <= 800:
                quality = 65
            elif width <= 1200:
                quality = 75
            else:
                quality = 82

            # Return to Pillow
            if resize.shape[2] == 4:
                result_rgb = cv2.cvtColor(resize, cv2.COLOR_BGRA2RGBA)
            else:
                result_rgb = cv2.cvtColor(resize, cv2.COLOR_BGR2RGB)

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
                'method': 6
            }

            if original_icc_profile:
                save_kwargs['icc_profile'] = original_icc_profile

            # Output handling
            if output_path:
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                pil_result.save(output_path, format, **save_kwargs)
                return True
            else:
                output = BytesIO()
                pil_result.save(output, format, **save_kwargs)
                output.seek(0)
                return output

        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return None
