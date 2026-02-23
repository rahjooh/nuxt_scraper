"""Random viewport size generation for anti-detection."""

from __future__ import annotations

import random
from typing import Tuple

# A selection of common and realistic desktop viewport sizes.
# It's good practice to update this list periodically based on web statistics.
REALISTIC_VIEWPORTS: list[Tuple[int, int]] = [
    (1920, 1080), # Full HD
    (1366, 768), # Common laptop resolution
    (1440, 900), # Apple Retina
    (1536, 864), # Common laptop resolution
    (1280, 720), # HD
    (1600, 900), # QHD variant
    (1024, 768), # Older desktop/tablet
    (1280, 800), # Older laptop
    (1920, 1200), # WUXGA
]

def get_random_viewport() -> Tuple[int, int]:
    """
    Returns a random realistic viewport size (width, height) from a predefined list.
    """
    return random.choice(REALISTIC_VIEWPORTS)
