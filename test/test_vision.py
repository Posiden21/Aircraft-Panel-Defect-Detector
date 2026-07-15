from __future__ import annotations

import cv2
import numpy as np

from aircraft_panel_detector.vision import detect_defects, detections_to_json_payload


def test_blank_panel_has_no_defects() -> None:
    frame = np.full((240, 320, 3), 180, dtype=np.uint8)

    detections, annotated = detect_defects(frame, min_area=80)

    assert detections == []
    assert annotated.shape == frame.shape


def test_dark_scratch_is_detected() -> None:
    frame = np.full((240, 320, 3), 180, dtype=np.uint8)
    cv2.line(frame, (60, 120), (220, 130), (20, 20, 20), 4)

    detections, _ = detect_defects(frame, min_area=40)

    assert len(detections) >= 1
    largest = detections[0]
    assert largest.w > 100
    assert largest.area > 40


def test_metadata_payload_is_json_ready() -> None:
    frame = np.full((240, 320, 3), 180, dtype=np.uint8)
    cv2.circle(frame, (160, 120), 20, (20, 20, 20), -1)
    detections, _ = detect_defects(frame, min_area=40)

    payload = detections_to_json_payload("2026-07-14T00:00:00+00:00", "frame_001", detections)

    assert payload["frame_id"] == "frame_001"
    assert payload["defect_count"] == len(detections)
    assert set(payload["detections"][0]) == {"x", "y", "w", "h", "area", "score"}
