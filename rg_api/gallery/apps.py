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
        # pylint: disable=unused-import, import-outside-toplevel
        import gallery.signals

        # Heuristic to detect if we are running a server (runserver, daphne, etc.)
        # and avoid loading the model during management commands like migrate.
        is_server_cmd = 'runserver' in sys.argv or \
                        any('daphne' in arg for arg in sys.argv) or \
                        'asgi' in str(sys.argv)

        is_management = 'migrate' in sys.argv or \
                        'makemigrations' in sys.argv or \
                        'collectstatic' in sys.argv or \
                        'test' in sys.argv

        if is_server_cmd or not is_management:
            self._start_model_warmup()

    def _start_model_warmup(self):
        """Start the model warmup in a separate thread."""
        def warmup_model():
            from gallery.ml import get_model  # pylint: disable=import-outside-toplevel
            print("--- Starting Background Model Warmup ---")
            try:
                get_model()
                print("--- Model Warmup Complete ---")
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"--- Model Warmup Error: {e} ---")

        # Run in a daemon thread so it doesn't block startup but runs immediately
        threading.Thread(target=warmup_model, daemon=True).start()
