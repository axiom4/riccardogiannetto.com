import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image

# Global variables for model caching
_processor = None
_model = None


def get_model():
    """
    Loads Salesforce BLIP-2 (Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models).
    This model (opt-2.7b) uses a Q-Former to bridge visual features with a language model, creating extremely detailed 
    and context-aware descriptions that far surpass standard classification or early captioning models.
    """
    global _processor, _model
    if _model is None:
        print("Loading BLIP-2 Model (OPT-2.7b)... this may take a moment.")

        model_id = "Salesforce/blip2-opt-2.7b"

        # Determine device: MPS (Apple Silicon), CUDA, or CPU
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"

        print(f"Using device: {device}")

        _processor = Blip2Processor.from_pretrained(model_id)
        # Using device_map="auto" via accelerate if possible, or manual move
        try:
            _model = Blip2ForConditionalGeneration.from_pretrained(
                model_id,
                device_map="auto" if device != "cpu" else None,
                torch_dtype=torch.float16 if device != "cpu" else torch.float32
            )
        except Exception:
            # Fallback if accelerate/device_map fails
            _model = Blip2ForConditionalGeneration.from_pretrained(model_id)
            _model.to(device)

        _model.eval()
        print("BLIP-2 model loaded.")

    return _processor, _model


def classify_image(image_path, top_k=5):
    """
    Generates a sophisticated caption using BLIP-2 and extracts high-level tags.
    """
    try:
        processor, model = get_model()
        device = model.device

        raw_image = Image.open(image_path).convert('RGB')

        # BLIP-2 allows asking questions! We can guide it to list objects.
        # But a general caption is usually best for tagging "wild nature".
        inputs = processor(images=raw_image, return_tensors="pt").to(
            device, torch.float16 if device.type != 'cpu' else torch.float32)

        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_new_tokens=50)

        caption = processor.batch_decode(
            generated_ids, skip_special_tokens=True)[0].strip()
        print(f"BLIP-2 Caption: {caption}")

        # Advanced keyword extraction from the rich caption
        stopwords = {'a', 'an', 'the', 'in', 'on', 'at', 'with', 'and', 'of', 'is', 'are', 'sitting', 'standing', 'looking', 'walking', 'flying', 'background',
                     'foreground', 'photo', 'picture', 'image', 'view', 'large', 'small', 'close', 'up', 'close-up', 'next', 'to', 'by', 'near', 'front', 'shot', 'full', 'frame'}

        words = caption.lower().replace('.', '').replace(',', '').split()
        tags = []
        for w in words:
            if w not in stopwords and len(w) > 2:
                # Basic singularization could happen here, but keeping it simple
                tags.append(w)

        return list(set(tags))

    except Exception as e:
        print(f"Error classifying image {image_path}: {e}")
        return []
