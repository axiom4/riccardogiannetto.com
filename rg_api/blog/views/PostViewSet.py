from rest_framework import viewsets
from blog.models import Post
from rest_framework import permissions
from blog.serializers import PostSerializer, PostPreviewSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

import os
import numpy as np
import cv2
from PIL import Image
from django.conf import settings
from rest_framework import renderers
from rest_framework.decorators import action


class PostImageRenderer(renderers.BaseRenderer):
    media_type = 'image/webp'
    format = 'webp'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        if renderer_context['response'].status_code != 200:
            return b""

        try:
            width = int(renderer_context['kwargs'].get('width', 0))
            if width <= 0:
                return b""
        except (ValueError, TypeError):
            return b""

        try:
            this_object = Post.objects.get(
                pk=renderer_context['kwargs']['pk'])
        except Post.DoesNotExist:
            return b""

        if not this_object.image:
            return b""

        # Ensure directory exists
        preview_dir = f"{settings.MEDIA_ROOT}/blog/preview"
        os.makedirs(preview_dir, exist_ok=True)

        filename = f"{preview_dir}/{this_object.pk}_{width}.webp"

        if os.path.exists(filename) == False:
            try:
                # STRATEGY FOR MAX COLOR FIDELITY:
                # 1. Preserve Original ICC Profile
                # 2. Use OpenCV Lanczos4 for sharpening/resizing.
                # 3. Embed the original ICC profile in the output WEBP.

                with Image.open(this_object.image.path) as pil_img:
                    original_icc_profile = pil_img.info.get('icc_profile')

                    # Only preserve ICC profile if the image is already in RGB/RGBA mode.
                    # Mapping CMYK profile to RGB image would result in color distortion.
                    if pil_img.mode not in ('RGB', 'RGBA'):
                        original_icc_profile = None
                        pil_img = pil_img.convert('RGB')

                    img_array = np.array(pil_img)
                    if img_array.shape[2] == 4:
                        cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
                    else:
                        cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

                if cv_img is None:
                    return b""

                original_height, original_width = cv_img.shape[:2]
                wpercent = (width / float(original_width))
                hsize = int((float(original_height) * float(wpercent)))

                # HIGH QUALITY RESIZING: Area (Better for compression)
                resize = cv2.resize(cv_img, (width, hsize),
                                    interpolation=cv2.INTER_AREA)

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

                # Ensure RGB for JPEG (Drop Alpha channel)
                if pil_result.mode == 'RGBA':
                    background = Image.new(
                        "RGB", pil_result.size, (255, 255, 255))
                    background.paste(pil_result, mask=pil_result.split()[3])
                    pil_result = background
                elif pil_result.mode != 'RGB':
                    pil_result = pil_result.convert('RGB')

                # Save as WEBP
                save_kwargs = {
                    'quality': quality,
                    'method': 6
                }
                # Embed the original ICC profile in the output WEBP.
                if original_icc_profile:
                    save_kwargs['icc_profile'] = original_icc_profile

                pil_result.save(filename, 'WEBP', **save_kwargs)
                with open(filename, "rb") as f:
                    return f.read()

            except Exception as e:
                print(f"Error generating preview: {e}")
                return b""

        else:
            with open(filename, "rb") as f:
                return f.read()


class PostPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12


@method_decorator(cache_page(60 * 60 * 2), name='list')
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ['get']
    pagination_class = PostPagination

    ordering_fields = '__all__'

    filterset_fields = ['categories__name']

    search_fields = [
        '$title',
        '$body'
    ]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostPreviewSerializer
        else:
            return self.serializer_class

    @method_decorator(cache_page(60 * 60 * 24 * 365))
    @action(methods=['get'], detail=True, url_path='width/(?P<width>[0-9]+)', url_name='size', renderer_classes=[PostImageRenderer])
    def image(self, request, *args, **kwargs):
        data = self.retrieve(request, *args, **kwargs)
        return data
