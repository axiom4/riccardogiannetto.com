"""
Base renderers for common use cases.
"""
from rest_framework import renderers


class WebPImageRenderer(renderers.BaseRenderer):
    """
    Base renderer for serving WebP images.
    """
    media_type = 'image/webp'
    format = 'webp'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders the image based on the provided width.

        Args:
            data: The data to render (unused for image rendering).
            accepted_media_type: The accepted media type.
            renderer_context: Context containing request details and kwargs.
        """
        if renderer_context['response'].status_code != 200:
            return b""

        width = self._get_width(renderer_context)
        if width <= 0:
            return b""

        return self._render_image(renderer_context, width)

    def _get_width(self, renderer_context):
        """Extract and validate width from renderer context."""
        try:
            return int(renderer_context['kwargs'].get('width', 0))
        except (ValueError, TypeError):
            return 0

    def _render_image(self, renderer_context, width):
        """
        Override this method to implement specific image rendering logic.

        Args:
            renderer_context: Context containing request details and kwargs.
            width: The width for the rendered image.

        Returns:
            bytes: The rendered image data.
        """
        raise NotImplementedError("Subclasses must implement _render_image")
