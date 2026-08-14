"""Parser for info_label_rev2/*.txt annotation files."""
import re
from pathlib import Path
from typing import NamedTuple, List, Optional

from .config import DATASET_ROOT as _DEFAULT_DATASET_ROOT


class HeaderInfo(NamedTuple):
    """Parsed header line from info_label_rev2/*.txt."""
    tesseract_idx: str
    os2_64_idx: str
    cam_front_idx: str
    os1_128_idx: str
    cam_lrr_idx: str
    timestamp: float
    raw: str


class ObjectAnnotation(NamedTuple):
    """Parsed object annotation line."""
    sensor_identify: str
    tracking_id: int
    obj_class: str
    x: float
    y: float
    z: float
    theta: float
    length_half: float
    width_half: float
    height_half: float
    
    @property
    def length(self) -> float:
        return self.length_half * 2.0
    
    @property
    def width(self) -> float:
        return self.width_half * 2.0
    
    @property
    def height(self) -> float:
        return self.height_half * 2.0
    
    @property
    def distance_ego(self) -> float:
        import math
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


def parse_header(line: str) -> HeaderInfo:
    """Parse the header line.
    
    Example:
    * idx(tesseract_os2-64_cam-front_os1-128_cam-lrr)=00282_00250_00749_00250_00751, timestamp=1643292971.608162560
    """
    # Extract indices
    match = re.search(r'idx\([^)]+\)=([0-9_]+)', line)
    if not match:
        raise ValueError(f"Could not parse header indices from: {line}")
    
    indices_str = match.group(1)
    parts = indices_str.split('_')
    if len(parts) != 5:
        raise ValueError(f"Expected 5 indices, got {len(parts)}: {indices_str}")
    
    # Extract timestamp
    ts_match = re.search(r'timestamp=([0-9.]+)', line)
    timestamp = float(ts_match.group(1)) if ts_match else 0.0
    
    return HeaderInfo(
        tesseract_idx=parts[0],
        os2_64_idx=parts[1],
        cam_front_idx=parts[2],
        os1_128_idx=parts[3],
        cam_lrr_idx=parts[4],
        timestamp=timestamp,
        raw=line.strip()
    )


def parse_object_line(line: str) -> Optional[ObjectAnnotation]:
    """Parse one object annotation line.
    
    Example:
    *, R, 1, Sedan, 47.391, -2.104, -0.425, -0.340, 1.641, 0.807, 0.710
    """
    parts = line.strip().split(', ')
    if len(parts) < 11:
        return None
    
    return ObjectAnnotation(
        sensor_identify=parts[1],
        tracking_id=int(parts[2]),
        obj_class=parts[3],
        x=float(parts[4]),
        y=float(parts[5]),
        z=float(parts[6]),
        theta=float(parts[7]),
        length_half=float(parts[8]),
        width_half=float(parts[9]),
        height_half=float(parts[10])
    )


def parse_label_file(filepath: Path) -> tuple[HeaderInfo, List[ObjectAnnotation]]:
    """Parse a full info_label_rev2/*.txt file.
    
    Returns (header, list of objects).
    """
    header = None
    objects = []
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('* idx'):
                header = parse_header(line)
            elif line.startswith('*, '):
                obj = parse_object_line(line)
                if obj:
                    objects.append(obj)
    
    if header is None:
        raise ValueError(f"No header found in {filepath}")
    
    return header, objects


def get_sequence_label_files(sequence_id: str, dataset_root: Optional[Path] = None) -> List[Path]:
    """Get all label files for a sequence."""
    if dataset_root is None:
        dataset_root = _DEFAULT_DATASET_ROOT
    label_dir = dataset_root / "data" / sequence_id / "info_label_rev2"
    if not label_dir.exists():
        return []
    return sorted(label_dir.glob("*.txt"))


def parse_description_txt(sequence_id: str, dataset_root: Optional[Path] = None) -> dict:
    """Parse description.txt for a sequence.

    Returns dict with keys: location, time, weather
    """
    if dataset_root is None:
        dataset_root = _DEFAULT_DATASET_ROOT
    else:
        dataset_root = Path(dataset_root)
    desc_path = dataset_root / "data" / sequence_id / "description.txt"
    if not desc_path.exists():
        return {}

    with open(desc_path, 'r') as f:
        content = f.read().strip()

    parts = content.split(',')
    result = {}
    if len(parts) >= 1:
        result['location'] = parts[0].strip()
    if len(parts) >= 2:
        result['time'] = parts[1].strip()
    if len(parts) >= 3:
        result['weather'] = parts[2].strip()

    return result
