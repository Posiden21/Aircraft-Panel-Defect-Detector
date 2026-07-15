#!/usr/bin/env python3
"""Generate synthetic aircraft panel images for local demos."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import cv2
import numpy as np


def generate_panel(seed: int, width: int = 640, height: int = 480) -> np.ndarray:
    rng = random.Random(seed)
    frame = np.full((height, width, 3), 180, dtype=np.uint8)
    noise = np.random.default_rng(seed).normal(0, 5, frame.shape).astype(np.int16)
    frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    for y in range(40, height, 80):
        for x in range(40, width, 80):
            cv2.circle(frame, (x, y), 7, (130, 130, 130), -1)
            cv2.circle(frame, (x, y), 7, (215, 215, 215), 1)

    if rng.random() > 0.25:
        start = (rng.randint(80, width - 160), rng.randint(80, height - 120))
        end = (start[0] + rng.randint(45, 140), start[1] + rng.randint(-25, 35))
        cv2.line(frame, start, end, (25, 25, 25), rng.randint(2, 4), cv2.LINE_AA)

    if rng.random() > 0.45:
        center = (rng.randint(100, width - 100), rng.randint(100, height - 100))
        axes = (rng.randint(12, 35), rng.randint(8, 24))
        cv2.ellipse(frame, center, axes, rng.randint(0, 180), 0, 360, (55, 60, 58), -1)

    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic aircraft panel defect images.")
    parser.add_argument("--output-dir", type=Path, default=Path("datasets/sample_images"))
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for index in range(args.count):
        frame = generate_panel(args.seed + index)
        cv2.imwrite(str(args.output_dir / f"panel_{index:03d}.png"), frame)

    print(f"Wrote {args.count} synthetic panel images to {args.output_dir}")


if __name__ == "__main__":
    main()
