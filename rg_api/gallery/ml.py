""" Machine learning utilities for image classification using BLIP-2. """
import logging
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
from django.conf import settings
from PIL import Image

logger = logging.getLogger(__name__)

# Model caching using function attributes


def get_model():
    """
    Loads Salesforce BLIP-2 (Bootstrapping Language-Image Pre-training 
    with Frozen Image Encoders and Large Language Models).
    This model (opt-2.7b) uses a Q-Former to bridge visual features with 
    a language model, creating extremely detailed 
    and context-aware descriptions that far surpass standard classification 
    or early captioning models.
    """
    if not settings.ENABLE_ML_MODELS:
        logger.info("BLIP-2 Model loading is disabled.")
        return None, None

    if not hasattr(get_model, "processor"):
        get_model.processor = None
    if not hasattr(get_model, "model"):
        get_model.model = None

    if get_model.model is None:
        logger.info(
            "Loading BLIP-2 Model (OPT-2.7b)... this may take a moment.")

        model_id = "Salesforce/blip2-opt-2.7b"

        # Determine device: MPS (Apple Silicon), CUDA, or CPU
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"

        logger.info("Using device: %s", device)

        # Explicitly set use_fast=True to suppress warning and future-proof
        get_model.processor = Blip2Processor.from_pretrained(
            model_id, use_fast=True)

        # device_map="auto" is excellent for CUDA but can cause shape errors on MPS/Mac.
        # For MPS, it's safer to load manually and move to device.
        try:
            if device == "cuda":
                get_model.model = Blip2ForConditionalGeneration.from_pretrained(
                    model_id,
                    device_map="auto",
                    dtype=torch.float16,
                    low_cpu_mem_usage=True
                )
            elif device == "mps":
                # MPS supports float16. low_cpu_mem_usage=True uses
                # accelerate to load faster avoiding RAM spikes
                get_model.model = Blip2ForConditionalGeneration.from_pretrained(
                    model_id,
                    dtype=torch.float16,
                    low_cpu_mem_usage=True
                )
                get_model.model.to("mps")
            else:
                get_model.model = Blip2ForConditionalGeneration.from_pretrained(
                    model_id,
                    dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
        except (RecursionError, OSError, RuntimeError, ValueError) as e1:

            logger.warning(
                "Primary load failed (%s), retrying on CPU/standard...", e1)

            # Fallback if acceleration fails
            get_model.model = Blip2ForConditionalGeneration.from_pretrained(
                model_id, low_cpu_mem_usage=True)
            get_model.model.to("cpu")

        get_model.model.eval()
        logger.info("BLIP-2 model loaded.")

    return get_model.processor, get_model.model


def classify_image(image_path):
    """
    Generates a sophisticated caption using BLIP-2 and extracts high-level tags.
    """
    try:
        processor, model = get_model()
        device = model.device

        with Image.open(image_path) as raw_image:
            # BLIP-2 allows asking questions! We can guide it to list objects.
            # But a general caption is usually best for tagging "wild nature".
            inputs = processor(images=raw_image.convert('RGB'), return_tensors="pt").to(
                device, torch.float16 if device.type != 'cpu' else torch.float32)

            with torch.no_grad():
                generated_ids = model.generate(**inputs, max_new_tokens=50)

            caption = processor.batch_decode(
                generated_ids, skip_special_tokens=True)[0].strip()
            logger.info("BLIP-2 Caption: %s", caption)

            # Advanced keyword extraction from the rich caption
            stopwords = {
                'a', 'an', 'the', 'in', 'on', 'at', 'with', 'and', 'of',
                'is', 'are', 'sitting', 'standing', 'looking', 'walking',
                'flying', 'background',
                'foreground', 'photo', 'picture', 'image', 'view', 'large',
                'small', 'close', 'up', 'close-up', 'next', 'to', 'by', 'near',
                'front', 'shot', 'full', 'frame'
            }

            words = caption.lower().replace('.', '').replace(',', '').split()
            tags = []
            for w in words:
                if w not in stopwords and len(w) > 2:
                    # Basic singularization could happen here, but keeping it simple
                    tags.append(w)

        return list(set(tags))

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error classifying image %s: %s", image_path, e)
        return []
