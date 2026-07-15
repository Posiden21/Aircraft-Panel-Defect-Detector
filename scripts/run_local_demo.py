#!/usr/bin/env python3
"""Run the defect detector on generated images without ROS 2."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from aircraft_panel_detector.vision import detect_defects, detections_to_json_payload
from generate_synthetic_panels import generate_panel


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample panels and run local OpenCV defect detection.")
    parser.add_argument("--output-dir", type=Path, default=Path("docs/assets/demo"))
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--min-area", type=int, default=80)
    args = parser.parse_args()

    raw_dir = args.output_dir / "raw"
    annotated_dir = args.output_dir / "annotated"
    raw_dir.mkdir(parents=True, exist_ok=True)
    annotated_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, object]] = []
    payloads = []

    for index in range(args.count):
        frame_id = f"panel_{index:03d}"
        frame = generate_panel(args.seed + index)
        detections, annotated = detect_defects(frame, min_area=args.min_area)

        raw_path = raw_dir / f"{frame_id}.png"
        annotated_path = annotated_dir / f"{frame_id}_annotated.png"
        cv2.imwrite(str(raw_path), frame)
        cv2.imwrite(str(annotated_path), annotated)

        payload = detections_to_json_payload(
            datetime.now(timezone.utc).isoformat(),
            frame_id,
            detections,
        )
        payload["raw_image"] = str(raw_path)
        payload["annotated_image"] = str(annotated_path)
        payloads.append(payload)

        for defect_id, detection in enumerate(detections, start=1):
            all_rows.append(
                {
                    "frame_id": frame_id,
                    "defect_id": defect_id,
                    "x": detection.x,
                    "y": detection.y,
                    "w": detection.w,
                    "h": detection.h,
                    "area": detection.area,
                    "score": detection.score,
                    "annotated_image": str(annotated_path),
                }
            )

    metadata_path = args.output_dir / "detections.json"
    metadata_path.write_text(json.dumps(payloads, indent=2), encoding="utf-8")

    csv_path = args.output_dir / "detections.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["frame_id", "defect_id", "x", "y", "w", "h", "area", "score", "annotated_image"],
        )
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Wrote demo images and metadata to {args.output_dir}")
    print(f"Detections: {len(all_rows)}")


if __name__ == "__main__":
    main()
