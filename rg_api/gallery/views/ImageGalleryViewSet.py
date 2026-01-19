
# Create your views here.
import os
import numpy as np
from PIL import Image, ImageCms, ImageEnhance
from django.conf import settings
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from gallery.models import ImageGallery
from gallery.serializers import ImageGallerySerializer
from rest_framework import renderers

from rest_framework.decorators import action
import cv2

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class ImageGalleryPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100


class ImageRenderer(renderers.BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpeg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        width = int(renderer_context['kwargs']['width'])

        this_object = ImageGallery.objects.get(
            pk=renderer_context['kwargs']['pk'])

        filename = f"{settings.MEDIA_ROOT}/preview/{this_object.pk}_{width}.jpg"

        if os.path.exists(filename) == False:
            try:
                # STRATEGY FOR MAX COLOR FIDELITY:
                # 1. Preserve Original ICC Profile
                # 2. Use OpenCV Lanczos4 for sharpening/resizing.
                # 3. Embed the original ICC profile in the output JPEG.

                with Image.open(this_object.image.path) as pil_img:
                    original_icc_profile = pil_img.info.get('icc_profile')
                    
                    if pil_img.mode not in ('RGB', 'RGBA'):
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

                # HIGH QUALITY RESIZING: Lanczos4
                resize = cv2.resize(cv_img, (width, hsize), interpolation=cv2.INTER_LANCZOS4)

                # Quality settings
                if width <= 800:
                    quality = 80 
                elif width <= 1200:
                    quality = 90
                else:
                    quality = 95

                # Return to Pillow
                if resize.shape[2] == 4:
                    result_rgb = cv2.cvtColor(resize, cv2.COLOR_BGRA2RGBA)
                else:
                    result_rgb = cv2.cvtColor(resize, cv2.COLOR_BGR2RGB)
                
                pil_result = Image.fromarray(result_rgb)
                
                # Ensure RGB for JPEG (Drop Alpha channel)
                if pil_result.mode == 'RGBA':
                    background = Image.new("RGB", pil_result.size, (255, 255, 255))
                    background.paste(pil_result, mask=pil_result.split()[3])
                    pil_result = background
                elif pil_result.mode != 'RGB':
                    pil_result = pil_result.convert('RGB')

                # KEY STEP: Re-embed the original ICC profile
                save_kwargs = {
                    'quality': quality,
                    'optimize': True,
                    'subsampling': 0  # 4:4:4 chroma subsampling for best color detail
                }
                if original_icc_profile:
                    save_kwargs['icc_profile'] = original_icc_profile

                pil_result.save(filename, 'JPEG', **save_kwargs)
                
                with open(filename, "rb") as f:
                    return f.read()

            except Exception as e:
                print(f"Error generating preview: {e}")
                return b""

        else:
            with open(filename, "rb") as f:
                return f.read()


@method_decorator(cache_page(60 * 60 * 2), name='list')
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')
class ImageGalleryViewSet(viewsets.ModelViewSet):

    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ['get']
    pagination_class = ImageGalleryPagination
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer]

    ordering_fields = ['title', 'created_at', 'gallery', 'date', 'id']

    filterset_fields = ['gallery']

    search_fields = [
        '$title'
    ]

    @method_decorator(cache_page(60 * 60 * 24 * 365))
    @action(methods=['get'], detail=True, url_path='width/(?P<width>[0-9]+)', url_name='size', renderer_classes=[ImageRenderer])
    def jpeg(self, request, *args, **kwargs):
        data = self.retrieve(request, *args, **kwargs)
        return data
