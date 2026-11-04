"""Import before transformers.

On the lab PC the installed torchvision fails to load its C ops
("operator torchvision::nms does not exist"), which breaks transformers' model
imports. These scripts need no vision code, so torchvision is blocked.
"""
import sys

sys.modules.setdefault("torchvision", None)

import transformers.utils.import_utils as _iu  # noqa: E402

_iu.is_torchvision_available = lambda: False
_iu.is_torchvision_v2_available = lambda: False
