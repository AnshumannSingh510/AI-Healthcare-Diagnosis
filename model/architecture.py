"""
Model builders for the chest X-ray multi-label classifier.
Primary backbone: DenseNet121 (transfer learning).
Alternate backbone: EfficientNet-B0, for comparison experiments.
"""
import torch.nn as nn
from torchvision import models

from model.labels import NUM_CLASSES


def build_densenet121(pretrained: bool = True, num_classes: int = NUM_CLASSES) -> nn.Module:
    weights = models.DenseNet121_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.densenet121(weights=weights)
    in_features = model.classifier.in_features
    model.classifier = nn.Linear(in_features, num_classes)
    return model


def build_efficientnet_b0(pretrained: bool = True, num_classes: int = NUM_CLASSES) -> nn.Module:
    weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.efficientnet_b0(weights=weights)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


def build_model(backbone: str = "densenet121", pretrained: bool = True, num_classes: int = NUM_CLASSES) -> nn.Module:
    if backbone == "densenet121":
        return build_densenet121(pretrained, num_classes)
    elif backbone == "efficientnet_b0":
        return build_efficientnet_b0(pretrained, num_classes)
    else:
        raise ValueError(f"Unknown backbone: {backbone}")
