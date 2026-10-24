"""
Gallery app configuration.
"""
import sys
import threading
from django.apps import AppConfig


class GalleryConfig(AppConfig):
    """
    Gallery app configuration.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'

    def ready(self):
        """
        Run when the app is ready.
        """
        # Avoid loading ML models during management commands (migrate, check, collectstatic, etc.)
        is_manage_py = any('manage.py' in arg for arg in sys.argv)
        is_server_cmd = any(cmd in ' '.join(sys.argv) for cmd in ('runserver', 'daphne', 'uvicorn', 'gunicorn'))

        if is_server_cmd or not is_manage_py:
            self._start_model_warmup()

    def _start_model_warmup(self):
        """Start the model warmup in a separate thread."""
        def warmup_model():
            print("--- Starting Background Model Warmup ---")
            try:
                from gallery.ml import get_model
                get_model()
                print("--- Model Warmup Complete ---")
            except (OSError, RuntimeError, ImportError) as e:
                print(f"--- Model Warmup Error: {e} ---")

        # Run in a daemon thread so it doesn't block startup but runs immediately
        threading.Thread(target=warmup_model, daemon=True).start()
