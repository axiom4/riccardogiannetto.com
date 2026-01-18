import torch
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image

# Load model globally to avoid reloading on every request (if possible, but careful with memory)
# Ideally this should be loaded on startup or on first use and cached.
_model = None
_weights = None
_preprocess = None


def get_model():
    global _model, _weights, _preprocess
    if _model is None:
        _weights = ResNet50_Weights.DEFAULT
        _model = resnet50(weights=_weights)
        _model.eval()
        _preprocess = _weights.transforms()
    return _model, _weights, _preprocess


def classify_image(image_path, top_k=5):
    """
    Classifies an image and returns the top K tags.
    """
    try:
        model, weights, preprocess = get_model()

        img = Image.open(image_path).convert('RGB')
        batch = preprocess(img).unsqueeze(0)

        with torch.no_grad():
            prediction = model(batch).squeeze(0).softmax(0)

        # Get top K predictions
        top_scores, top_indices = torch.topk(prediction, k=top_k)

        tags = []
        categories = weights.meta["categories"]

        for score, class_id in zip(top_scores, top_indices):
            # Only include tags with a reasonable confidence (e.g., > 10% or just top K)
            # For now, we take top K regardless of score but you might want a threshold.
            if score.item() > 0.05:  # 5% threshold
                tag = categories[class_id.item()]
                tags.append(tag)

        return tags
    except Exception as e:
        print(f"Error classifying image {image_path}: {e}")
        return []
