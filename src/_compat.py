"""Import before transformers.

If torchvision is installed but does not match torch (it fails with
"operator torchvision::nms does not exist"), transformers cannot import models.
These scripts need no vision code, so in that case torchvision is blocked.
With a matching torchvision this file does nothing.
"""
import sys

try:
    import torchvision  # noqa: F401
except Exception:
    sys.modules["torchvision"] = None
    import transformers.utils.import_utils as _iu

    _iu.is_torchvision_available = lambda: False
    _iu.is_torchvision_v2_available = lambda: False
