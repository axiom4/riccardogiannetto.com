"""
Script to optimize static assets (images) in the frontend assets directory.

This script must be run from the workspace root directory.
"""
import os
import concurrent.futures
from functools import partial

from image_utils import ImageOptimizer

ASSETS_DIR = 'rg_web/src/assets/images'


def optimize_file(file_name):
    """
    Optimizes a single file.
    """
    full_path = os.path.join(ASSETS_DIR, file_name)
    print(f"Optimizing {file_name}...")

    # Determine format from extension
    # We default to JPEG as per original logic, though extension usually dictates format
    fmt = 'JPEG'

    try:
        old_size = os.path.getsize(full_path)

        # We want to keep original dimensions
        optimized_bytes = ImageOptimizer.compress_and_resize(
            full_path,
            width=None,
            output_format=fmt
        )

        if optimized_bytes:
            # Compare sizes
            new_size = len(optimized_bytes.getvalue())

            if new_size < old_size:
                with open(full_path, 'wb') as output_file:
                    output_file.write(optimized_bytes.getvalue())
                return f"  Saved {old_size - new_size} bytes ({(old_size-new_size)/old_size:.1%}) for {file_name}"
            else:
                return f"  Skipped (larger or same: {new_size} vs {old_size}) for {file_name}"
    except (OSError, ValueError, IOError) as e:
        return f"  Error optimizing {file_name}: {e}"

    return f"  No result for {file_name}"


def optimize_static_assets():
    """
    Optimizes all .jpg files in the assets directory in place using parallel processing.
    """
    if not os.path.isdir(ASSETS_DIR):
        print(f"Directory not found: {ASSETS_DIR}")
        return

    files = [f for f in os.listdir(ASSETS_DIR) if f.lower().endswith('.jpg')]

    if not files:
        print("No .jpg files found to optimize.")
        return

    # Use ThreadPoolExecutor for I/O bound tasks (reading/writing files)
    # or ProcessPoolExecutor for CPU bound tasks (image compression).
    # Pillow releases GIL, so threading might be okay, but ProcessPool is safer for heavy compression.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(optimize_file, files))

    for result in results:
        print(result)


if __name__ == '__main__':
    optimize_static_assets()
