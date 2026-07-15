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
    np_rng = np.random.default_rng(seed)

    base = np.full((height, width, 3), 176, dtype=np.uint8)
    x_gradient = np.linspace(-18, 24, width, dtype=np.float32)
    y_gradient = np.linspace(10, -16, height, dtype=np.float32)[:, None]
    lighting = x_gradient + y_gradient
    noise = np_rng.normal(0, 4.5, (height, width)).astype(np.float32)
    texture = lighting + noise

    for channel in range(3):
        base[:, :, channel] = np.clip(base[:, :, channel].astype(np.float32) + texture, 0, 255)

    frame = base.astype(np.uint8)

    # Panel seams and brushed-metal lines make the generated frames read as aircraft skin.
    for seam_x in (width // 3, 2 * width // 3):
        cv2.line(frame, (seam_x, 0), (seam_x + rng.randint(-8, 8), height), (116, 116, 116), 2, cv2.LINE_AA)
        cv2.line(frame, (seam_x + 3, 0), (seam_x + 3, height), (220, 220, 220), 1, cv2.LINE_AA)

    for seam_y in (height // 3, 2 * height // 3):
        cv2.line(frame, (0, seam_y), (width, seam_y + rng.randint(-6, 6)), (118, 118, 118), 2, cv2.LINE_AA)
        cv2.line(frame, (0, seam_y + 3), (width, seam_y + 3), (214, 214, 214), 1, cv2.LINE_AA)

    for y in range(42, height, 76):
        for x in range(44, width, 74):
            offset = rng.randint(-3, 3)
            center = (x + offset, y + rng.randint(-2, 2))
            cv2.circle(frame, center, 8, (118, 118, 118), -1, cv2.LINE_AA)
            cv2.circle(frame, center, 8, (225, 225, 225), 1, cv2.LINE_AA)
            cv2.circle(frame, (center[0] - 2, center[1] - 2), 3, (160, 160, 160), -1, cv2.LINE_AA)

    if rng.random() > 0.25:
        start = (rng.randint(70, width - 180), rng.randint(80, height - 130))
        current = start
        for _ in range(rng.randint(3, 5)):
            end = (current[0] + rng.randint(34, 74), current[1] + rng.randint(-14, 18))
            cv2.line(frame, current, end, (28, 28, 28), rng.randint(2, 3), cv2.LINE_AA)
            cv2.line(frame, (current[0], current[1] + 2), (end[0], end[1] + 2), (92, 92, 92), 1, cv2.LINE_AA)
            current = end

    if rng.random() > 0.45:
        center = (rng.randint(100, width - 100), rng.randint(100, height - 100))
        axes = (rng.randint(22, 48), rng.randint(12, 30))
        angle = rng.randint(0, 180)
        cv2.ellipse(frame, center, axes, angle, 0, 360, (80, 84, 82), -1, cv2.LINE_AA)
        cv2.ellipse(frame, (center[0] - 5, center[1] - 4), axes, angle, 0, 180, (218, 218, 210), 2, cv2.LINE_AA)

    if rng.random() > 0.35:
        pit_center = (rng.randint(90, width - 90), rng.randint(80, height - 80))
        for _ in range(rng.randint(5, 10)):
            center = (pit_center[0] + rng.randint(-24, 24), pit_center[1] + rng.randint(-18, 18))
            radius = rng.randint(3, 8)
            cv2.circle(frame, center, radius, (45, 52, 48), -1, cv2.LINE_AA)
            cv2.circle(frame, (center[0] - 1, center[1] - 1), radius, (95, 98, 92), 1, cv2.LINE_AA)

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
