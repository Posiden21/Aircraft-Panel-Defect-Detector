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
import numpy as np

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
    montage_pairs: list[tuple[Path, Path]] = []

    for index in range(args.count):
        frame_id = f"panel_{index:03d}"
        frame = generate_panel(args.seed + index)
        detections, annotated = detect_defects(frame, min_area=args.min_area)

        raw_path = raw_dir / f"{frame_id}.png"
        annotated_path = annotated_dir / f"{frame_id}_annotated.png"
        cv2.imwrite(str(raw_path), frame)
        cv2.imwrite(str(annotated_path), annotated)
        montage_pairs.append((raw_path, annotated_path))

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

    if montage_pairs:
        _write_montage(args.output_dir / "inspection_demo.png", montage_pairs[:3])

    print(f"Wrote demo images and metadata to {args.output_dir}")
    print(f"Detections: {len(all_rows)}")


def _write_montage(path: Path, pairs: list[tuple[Path, Path]]) -> None:
    panels = []
    for raw_path, annotated_path in pairs:
        raw = cv2.imread(str(raw_path))
        annotated = cv2.imread(str(annotated_path))
        raw = cv2.resize(raw, (420, 315))
        annotated = cv2.resize(annotated, (420, 315))
        row = cv2.hconcat([raw, annotated])
        panels.append(row)

    montage = cv2.vconcat(panels)
    header = np.full((70, montage.shape[1], 3), (30, 31, 34), dtype=np.uint8)
    cv2.putText(header, "Aircraft Panel Defect Detection Demo", (24, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (245, 245, 245), 2, cv2.LINE_AA)
    label_bar = np.full((36, montage.shape[1], 3), (44, 46, 50), dtype=np.uint8)
    cv2.putText(label_bar, "Raw inspection frame", (120, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1, cv2.LINE_AA)
    cv2.putText(label_bar, "Annotated detector output", (530, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1, cv2.LINE_AA)
    cv2.imwrite(str(path), cv2.vconcat([header, label_bar, montage]))


if __name__ == "__main__":
    main()
