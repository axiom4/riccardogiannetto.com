from utils.image_optimizer import ImageOptimizer
import os
import sys
# import django

# Setup Django if needed for imports, but we just need utils
sys.path.append(os.path.join(os.getcwd(), 'rg_api'))

ASSETS_DIR = 'rg_web/src/assets/images'


def optimize_static_assets():
    files = [f for f in os.listdir(ASSETS_DIR) if f.lower().endswith('.jpg')]
    for file in files:
        full_path = os.path.join(ASSETS_DIR, file)
        print(f"Optimizing {file}...")

        # Determine format from extension
        fmt = 'JPEG'

        # Read file
        with open(full_path, 'rb') as f:
            content = f.read()

        from io import BytesIO
        file_obj = BytesIO(content)

        # Optimize
        try:
            # We want to keep original dimensions
            optimized_bytes = ImageOptimizer.compress_and_resize(
                file_obj,
                width=None,
                img_format=fmt
            )

            if optimized_bytes:
                # Compare sizes
                old_size = len(content)
                new_size = len(optimized_bytes.getvalue())

                if new_size < old_size:
                    with open(full_path, 'wb') as f:
                        f.write(optimized_bytes.getvalue())
                    print(
                        f"  Saved {old_size - new_size} bytes ({(old_size-new_size)/old_size:.1%})")
                else:
                    print(
                        f"  Skipped (larger or same: {new_size} vs {old_size})")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == '__main__':
    optimize_static_assets()
