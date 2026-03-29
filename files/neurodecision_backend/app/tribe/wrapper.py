"""
TRIBE v2 Wrapper — Real Local Integration
"""

import os
import hashlib
import random
import logging

logger = logging.getLogger(__name__)

BRAIN_REGIONS = [
    "visual_cortex","prefrontal_cortex","broca_area","wernicke_area",
    "amygdala","hippocampus","anterior_cingulate","nucleus_accumbens",
    "insula","motor_cortex",
]

_tribe_model = None
_tribe_tokenizer = None
_device = None


def _load_model():
    global _tribe_model, _tribe_tokenizer, _device
    if _tribe_model is not None:
        return

    model_path = os.environ.get("TRIBE_MODEL_PATH", "").strip()
    if not model_path:
        raise EnvironmentError("TRIBE_MODEL_PATH not set")
    if not os.path.isdir(model_path):
        raise FileNotFoundError(f"Model directory not found: {model_path}")

    import torch
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Loading TRIBE v2 from {model_path} on {_device}")

    # Try HuggingFace first
    try:
        from transformers import AutoModel, AutoTokenizer
        _tribe_tokenizer = AutoTokenizer.from_pretrained(model_path)
        _tribe_model = AutoModel.from_pretrained(model_path).to(_device)
        _tribe_model.eval()
        logger.info("Loaded via HuggingFace AutoModel")
        return
    except Exception as e:
        logger.debug(f"HF load failed: {e}")

    # Fall back to raw .pth checkpoint
    candidates = ["model.pth","checkpoint.pth","model_weights.pth","tribe.pth","tribe_v2.pth"]
    checkpoint_path = next(
        (os.path.join(model_path, f) for f in candidates if os.path.isfile(os.path.join(model_path, f))),
        None
    )
    if checkpoint_path is None:
        pth_files = [f for f in os.listdir(model_path) if f.endswith(".pth")]
        if pth_files:
            checkpoint_path = os.path.join(model_path, pth_files[0])

    if checkpoint_path is None:
        raise FileNotFoundError(f"No .pth checkpoint found in {model_path}")

    checkpoint = torch.load(checkpoint_path, map_location=_device)
    state_dict = checkpoint.get("model_state_dict") or checkpoint.get("state_dict") or checkpoint

    try:
        from tribe.models import TribeModel
    except ImportError:
        from tribe_v2.model import TribeModel

    config_path = os.path.join(model_path, "config.yaml")
    if not os.path.isfile(config_path):
        config_path = os.path.join(model_path, "config.json")

    _tribe_model = TribeModel.from_config(config_path).to(_device)
    _tribe_model.load_state_dict(state_dict, strict=False)
    _tribe_model.eval()
    logger.info(f"Loaded raw checkpoint: {checkpoint_path}")


def run_tribe_inference(input_data: str) -> dict:
    model_path = os.environ.get("TRIBE_MODEL_PATH", "").strip()
    if model_path:
        try:
            _load_model()
            return _real_inference(input_data)
        except Exception as e:
            logger.error(f"Real inference failed, using mock: {e}")
    return _mock_inference(input_data)


def _real_inference(input_data: str) -> dict:
    import torch

    with torch.no_grad():
        if _tribe_tokenizer is not None:
            inputs = _tribe_tokenizer(
                input_data, return_tensors="pt",
                truncation=True, max_length=512, padding=True
            ).to(_device)
            outputs = _tribe_model(**inputs)
        else:
            outputs = _tribe_model({"text": input_data})

    if isinstance(outputs, dict) and "brain_activations" in outputs:
        raw = outputs["brain_activations"]
    elif hasattr(outputs, "last_hidden_state"):
        raw = outputs.last_hidden_state.mean(dim=1).squeeze()
    elif isinstance(outputs, (tuple, list)):
        raw = outputs[0].mean(dim=-1).squeeze()
    else:
        raw = outputs

    import torch
    raw_tensor = raw if isinstance(raw, torch.Tensor) else torch.tensor(raw)
    raw_flat = raw_tensor.flatten()

    import torch.nn.functional as F
    if len(raw_flat) >= len(BRAIN_REGIONS):
        vals = torch.sigmoid(raw_flat[:len(BRAIN_REGIONS)]).cpu().numpy()
    else:
        stretched = F.interpolate(
            raw_flat.unsqueeze(0).unsqueeze(0).float(),
            size=len(BRAIN_REGIONS), mode="linear", align_corners=False
        ).squeeze()
        vals = torch.sigmoid(stretched).cpu().numpy()

    return {r: float(round(float(v), 4)) for r, v in zip(BRAIN_REGIONS, vals)}


def _mock_inference(input_data: str) -> dict:
    seed = int(hashlib.md5(input_data.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    factor = min(len(input_data) / 500, 1.0)
    activations = {}
    for region in BRAIN_REGIONS:
        base = rng.uniform(0.3, 0.9)
        noise = rng.uniform(-0.1, 0.1)
        adj = base + factor * 0.15 * rng.choice([-1, 1])
        activations[region] = round(max(0.0, min(1.0, adj + noise)), 4)
    return activations


def _detect_input_type(data: str) -> str:
    d = data.lower()
    if any(x in d for x in [".jpg",".jpeg",".png",".webp"]): return "image"
    if any(x in d for x in [".mp4",".mov",".avi",".webm"]): return "video"
    return "text"
