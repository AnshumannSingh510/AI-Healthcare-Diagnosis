"""
Grad-CAM implementation for the chest X-ray classifier.

Targets the last convolutional block of DenseNet121 (`features.norm5`'s
input, i.e. the last dense block's output) by default. Produces a heatmap
overlaid on the original X-ray image and saves it as a PNG.
"""
import cv2
import numpy as np
import torch
import torch.nn.functional as F


class GradCAM:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, inp, out):
            self.activations = out.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor: torch.Tensor, class_idx: int) -> np.ndarray:
        """
        input_tensor: shape (1, C, H, W), already normalized/preprocessed.
        class_idx: index of the target class to explain.
        Returns a (H, W) heatmap normalized to [0, 1].
        """
        self.model.zero_grad()
        output = self.model(input_tensor)
        score = output[0, class_idx]
        score.backward(retain_graph=True)

        # Global-average-pool the gradients to get per-channel importance weights
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)  # (1, 1, H, W)
        cam = F.relu(cam)

        cam = cam.squeeze().cpu().numpy()
        cam = cam - cam.min()
        if cam.max() > 0:
            cam = cam / cam.max()
        return cam


def find_densenet_target_layer(model: torch.nn.Module) -> torch.nn.Module:
    """
    Returns the last convolutional layer of a torchvision DenseNet121:
    features.denseblock4 (the final dense block, before the final norm/pool).
    """
    return model.features.denseblock4


def overlay_heatmap_on_image(
    original_image_bgr: np.ndarray, cam: np.ndarray, output_path: str, alpha: float = 0.4
) -> str:
    """
    original_image_bgr: the original image as a BGR numpy array (cv2 format),
        at any resolution — will be resized to match cam's aspect handling.
    cam: (H, W) array in [0, 1] from GradCAM.generate().
    """
    h, w = original_image_bgr.shape[:2]
    cam_resized = cv2.resize(cam, (w, h))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(heatmap, alpha, original_image_bgr, 1 - alpha, 0)
    cv2.imwrite(output_path, overlay)
    return output_path
