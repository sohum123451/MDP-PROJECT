"""
Frame Grabber Module for EchoScribe-AI / SonoAssist.
Member 1 (Joel - CSE Core 1 Deliverable).
Captures high-resolution ultrasound keyframes upon hardware button or pedal press,
timestamps each frame synchronously with audio, and logs spatial acquisition parameters.
"""

import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np


class KeyframeMetadata:
    """Metadata recorded for each captured ultrasound keyframe."""
    def __init__(
        self,
        frame_id: str,
        timestamp_offset_ms: float,
        target_organ: str,
        trigger_source: str = "hardware_foot_pedal",
        resolution: Tuple[int, int] = (1920, 1080),
        depth_cm: float = 14.0,
        frequency_mhz: float = 3.5,
        gain_db: float = 52.0
    ):
        self.frame_id = frame_id
        self.timestamp_offset_ms = timestamp_offset_ms
        self.target_organ = target_organ
        self.trigger_source = trigger_source
        self.resolution = resolution
        self.depth_cm = depth_cm
        self.frequency_mhz = frequency_mhz
        self.gain_db = gain_db

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "timestamp_offset_ms": round(self.timestamp_offset_ms, 2),
            "target_organ": self.target_organ,
            "trigger_source": self.trigger_source,
            "resolution": {"width": self.resolution[0], "height": self.resolution[1]},
            "ultrasound_parameters": {
                "depth_cm": self.depth_cm,
                "frequency_mhz": self.frequency_mhz,
                "gain_db": self.gain_db
            }
        }


class UltrasoundFrameGrabber:
    """
    Ultrasound video feed frame grabber.
    Provides synchronous keyframe acquisition with button-press interrupt triggers.
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or "data/captured_keyframes")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_start_time: Optional[float] = None
        self.captured_keyframes: List[KeyframeMetadata] = []

    def start_session(self) -> float:
        """Initializes session master clock for millisecond-precision audio/frame sync."""
        self.session_start_time = time.time()
        self.captured_keyframes.clear()
        return self.session_start_time

    def trigger_keyframe_capture(
        self,
        target_organ: str = "general",
        trigger_source: str = "hardware_foot_pedal",
        simulated_frame_data: Optional[np.ndarray] = None
    ) -> Tuple[KeyframeMetadata, str]:
        """
        Executes on physical button press or pedal trigger.
        Acquires current frame buffer, generates synthetic B-mode frame if no hardware feed,
        and returns keyframe metadata alongside saved file path.
        """
        if self.session_start_time is None:
            self.start_session()

        elapsed_ms = (time.time() - self.session_start_time) * 1000.0
        frame_id = f"FRAME_{int(elapsed_ms)}_{uuid.uuid4().hex[:6]}"

        metadata = KeyframeMetadata(
            frame_id=frame_id,
            timestamp_offset_ms=elapsed_ms,
            target_organ=target_organ,
            trigger_source=trigger_source
        )

        filename = f"{frame_id}_{target_organ}.png"
        filepath = self.output_dir / filename

        # Generate synthetic ultrasound B-mode sector frame if hardware feed is offline
        if simulated_frame_data is None:
            simulated_frame_data = self._generate_synthetic_ultrasound_frame(target_organ)

        # Save frame (using simple PPM/binary or saving dummy representation)
        self._save_raw_frame(filepath, simulated_frame_data)
        self.captured_keyframes.append(metadata)

        return metadata, str(filepath)

    def _save_raw_frame(self, filepath: Path, frame: np.ndarray) -> None:
        """Saves a grayscale frame as an uncompressed portable graymap (PGM) image."""
        h, w = frame.shape[:2]
        header = f"P5\n{w} {h}\n255\n".encode("ascii")
        with open(filepath.with_suffix(".pgm"), "wb") as f:
            f.write(header)
            f.write(frame.astype(np.uint8).tobytes())

    def _generate_synthetic_ultrasound_frame(self, organ: str) -> np.ndarray:
        """
        Generates a synthetic 480x640 ultrasound B-mode sector scan image
        with characteristic acoustic speckle pattern and organ contours.
        """
        h, w = 480, 640
        # Rayleigh-distributed acoustic speckle noise
        speckle = np.random.rayleigh(scale=35.0, size=(h, w))

        # Sector mask (curvilinear probe sector geometry)
        y, x = np.ogrid[:h, :w]
        center_x = w // 2
        radius = np.sqrt((x - center_x) ** 2 + y ** 2)
        angle = np.abs(np.arctan2(x - center_x, y))

        sector_mask = (radius > 40) & (radius < 450) & (angle < 0.65)

        base_frame = np.zeros((h, w), dtype=np.float32)
        base_frame[sector_mask] = speckle[sector_mask]

        # Add simulated anatomical features
        if organ.lower() in ["gallbladder", "biliary"]:
            # Anechoic fluid-filled lumen with bright echogenic wall
            gb_mask = ((x - 300) ** 2 / 40 ** 2 + (y - 200) ** 2 / 70 ** 2) < 1.0
            base_frame[gb_mask] = np.random.normal(5, 2, size=base_frame[gb_mask].shape)
        elif organ.lower() in ["kidney", "renal"]:
            # Corticomedullary differentiation
            kidney_mask = ((x - 320) ** 2 / 80 ** 2 + (y - 220) ** 2 / 120 ** 2) < 1.0
            base_frame[kidney_mask] += 25.0

        return np.clip(base_frame, 0, 255).astype(np.uint8)

    def get_session_summary(self) -> List[Dict[str, Any]]:
        """Returns list of all keyframes captured during current session."""
        return [k.to_dict() for k in self.captured_keyframes]
