"""
Configuration and constants for Revit-GIS integration
"""

from pathlib import Path
from enum import Enum

# Directory structure
WORKSPACE_ROOT = Path(__file__).parent.parent
DATA_DIR = WORKSPACE_ROOT / "data"
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"

# Create directories if they don't exist
CHECKPOINT_DIR = DATA_DIR / "checkpoints"
REVIT_EXPORT_DIR = DATA_DIR / "revit_exports"
GH_INPUT_DIR = DATA_DIR / "gh_inputs"
GH_OUTPUT_DIR = DATA_DIR / "gh_outputs"
EXPORT_DIR = DATA_DIR / "exports"
REPORT_DIR = DATA_DIR / "reports"
SYNC_DIR = DATA_DIR / ".sync"

for dir_path in [CHECKPOINT_DIR, REVIT_EXPORT_DIR, GH_INPUT_DIR, 
                  GH_OUTPUT_DIR, EXPORT_DIR, REPORT_DIR, SYNC_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Metadata
METADATA_FILE = SYNC_DIR / "metadata.json"

# Coordinate systems
class CoordinateSystem(Enum):
    """Supported coordinate systems"""
    UTM_33N = "EPSG:32633"  # Dutch standard
    UTM_32N = "EPSG:32632"
    WGS84 = "EPSG:4326"
    RD = "EPSG:28992"  # Rijksdriehoeksmeting (Netherlands)

DEFAULT_EPSG = CoordinateSystem.UTM_33N.value

# AGOL Configuration
AGOL_CONFIG = {
    "portal_url": "https://www.arcgisonline.com/sharing/rest",
    "max_batch_size": 1000,  # Max features per request
    "timeout": 30,  # Request timeout in seconds
}

# Sync configuration
SYNC_CONFIG = {
    "conflict_strategy": "last_write_wins",  # Options: last_write_wins, revit_priority, manual
    "enable_versioning": True,
    "enable_checkpoints": True,
    "checkpoint_interval": 100,  # Save checkpoint every N objects
}

# Timeout settings
TIMEOUT_CONFIG = {
    "gh_wait_timeout": 300,  # Max 5 minutes wait for GH output
    "agol_request_timeout": 30,
    "revit_export_timeout": 60,
}

# Logging
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}

# Supported element types
SUPPORTED_ELEMENTS = [
    "Wall",
    "Floor", 
    "Roof",
    "Door",
    "Window",
    "Column",
    "Beam",
    "Ramp",
    "Stairs"
]

# GeoJSON property mapping
GH_TO_AGOL_PROPERTY_MAP = {
    "name": "name",
    "type": "element_type",
    "version": "version",
    "timestamp": "last_modified",
    "id": "gh_id",
    "revit_id": "revit_element_id"
}
