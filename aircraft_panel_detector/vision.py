"""OpenCV defect detection utilities for aircraft panel imagery."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import cv2
import numpy as np


@dataclass(frozen=True)
class Detection:
    """Single defect candidate returned by the vision pipeline."""

    x: int
    y: int
    w: int
    h: int
    area: float
    score: float

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def detect_defects(
    frame: np.ndarray,
    *,
    min_area: int = 80,
    dark_threshold: int = 85,
    blur_kernel: int = 5,
) -> tuple[list[Detection], np.ndarray]:
    """Detect dark scratches, spots, and surface anomalies in a BGR or grayscale image."""
    if frame is None or frame.size == 0:
        raise ValueError("frame must be a non-empty image")

    gray = _to_grayscale(frame)
    kernel_size = _odd_kernel_size(blur_kernel)
    blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

    _, dark_mask = cv2.threshold(blurred, dark_threshold, 255, cv2.THRESH_BINARY_INV)
    edges = cv2.Canny(blurred, 60, 160)
    combined = cv2.bitwise_or(dark_mask, edges)

    kernel = np.ones((3, 3), dtype=np.uint8)
    cleaned = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = cv2.dilate(cleaned, kernel, iterations=1)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = [_contour_to_detection(contour) for contour in contours if cv2.contourArea(contour) >= min_area]
    detections = sorted(detections, key=lambda detection: detection.area, reverse=True)

    annotated = _to_bgr(frame)
    for index, detection in enumerate(detections, start=1):
        cv2.rectangle(
            annotated,
            (detection.x, detection.y),
            (detection.x + detection.w, detection.y + detection.h),
            (0, 0, 255),
            2,
        )
        cv2.putText(
            annotated,
            f"Defect {index}",
            (detection.x, max(20, detection.y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

    return detections, annotated


def detections_to_json_payload(timestamp: str, frame_id: str, detections: list[Detection]) -> dict[str, Any]:
    """Build the JSON-serializable message published by the ROS detector node."""
    return {
        "timestamp": timestamp,
        "frame_id": frame_id,
        "defect_count": len(detections),
        "detections": [detection.to_dict() for detection in detections],
    }


def _to_grayscale(frame: np.ndarray) -> np.ndarray:
    if len(frame.shape) == 2:
        return frame
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def _to_bgr(frame: np.ndarray) -> np.ndarray:
    if len(frame.shape) == 2:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    return frame.copy()


def _odd_kernel_size(value: int) -> int:
    value = max(3, int(value))
    return value if value % 2 else value + 1


def _contour_to_detection(contour: np.ndarray) -> Detection:
    x, y, w, h = cv2.boundingRect(contour)
    area = float(cv2.contourArea(contour))
    score = min(1.0, area / max(1.0, float(w * h)))
    return Detection(x=int(x), y=int(y), w=int(w), h=int(h), area=round(area, 2), score=round(score, 3))
