"""
Revit to Grasshopper Connector
Exports Revit geometry and properties for Grasshopper processing
Can be run as IronPython in Revit or standalone Python with RevitAPI
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class RevitExporter:
    """Exports Revit elements to JSON format for Grasshopper"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent.parent / "data" / "revit_exports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_walls(self, revit_elements: List[Any]) -> List[Dict[str, Any]]:
        """Extract walls from Revit"""
        walls = []
        
        for elem in revit_elements:
            try:
                wall = {
                    "id": f"wall_{str(uuid.uuid4())[:8]}",
                    "revit_id": elem.get("id"),
                    "type": "Wall",
                    "properties": {
                        "name": elem.get("name", "Unknown Wall"),
                        "length": elem.get("length"),
                        "height": elem.get("height"),
                        "material": elem.get("material", "Default"),
                        "level": elem.get("level")
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": elem.get("curve_points", [])
                    }
                }
                walls.append(wall)
            except Exception as e:
                print(f"Error exporting wall: {e}")
        
        return walls
    
    def export_doors_windows(self, revit_elements: List[Any]) -> List[Dict[str, Any]]:
        """Extract openings (doors/windows) from Revit"""
        openings = []
        
        for elem in revit_elements:
            try:
                opening = {
                    "id": f"opening_{str(uuid.uuid4())[:8]}",
                    "revit_id": elem.get("id"),
                    "type": elem.get("element_type", "Opening"),
                    "properties": {
                        "name": elem.get("name"),
                        "width": elem.get("width"),
                        "height": elem.get("height"),
                        "family_type": elem.get("family_type")
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": elem.get("position", [0, 0])
                    }
                }
                openings.append(opening)
            except Exception as e:
                print(f"Error exporting opening: {e}")
        
        return openings
    
    def export_floors(self, revit_elements: List[Any]) -> List[Dict[str, Any]]:
        """Extract floors from Revit"""
        floors = []
        
        for elem in revit_elements:
            try:
                floor = {
                    "id": f"floor_{str(uuid.uuid4())[:8]}",
                    "revit_id": elem.get("id"),
                    "type": "Floor",
                    "properties": {
                        "name": elem.get("name"),
                        "level": elem.get("level"),
                        "thickness": elem.get("thickness"),
                        "material": elem.get("material")
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": elem.get("boundary_points", [])
                    }
                }
                floors.append(floor)
            except Exception as e:
                print(f"Error exporting floor: {e}")
        
        return floors
    
    def export_all(self, revit_document: Dict[str, Any]) -> Dict[str, Any]:
        """Complete export of all relevant Revit elements"""
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "revit_file": revit_document.get("file_path"),
            "project_name": revit_document.get("project_name"),
            "coordinate_system": {
                "epsg": revit_document.get("epsg_code", "EPSG:32633"),  # Default to UTM 33N
                "origin": revit_document.get("origin_point", [0, 0, 0])
            },
            "elements": {
                "walls": self.export_walls(revit_document.get("walls", [])),
                "openings": self.export_doors_windows(revit_document.get("openings", [])),
                "floors": self.export_floors(revit_document.get("floors", []))
            }
        }
        
        return export_data
    
    def save_export(self, data: Dict[str, Any], filename: str = None) -> Path:
        """Save exported data to JSON file"""
        if filename is None:
            filename = f"revit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Export saved to: {filepath}")
        return filepath


class RevitImporter:
    """Imports modified GH data back into Revit format"""
    
    def __init__(self):
        pass
    
    def prepare_for_revit(self, gh_modified_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert GH output to Revit-compatible format"""
        
        revit_updates = {
            "timestamp": datetime.now().isoformat(),
            "updates": []
        }
        
        for obj in gh_modified_data:
            update = {
                "revit_id": obj.get("revit_id"),
                "type": obj.get("type"),
                "geometry": obj.get("geometry"),
                "properties": obj.get("properties"),
                "operation": "update"
            }
            revit_updates["updates"].append(update)
        
        return revit_updates


class RevitGHBridge:
    """Orchestrates full Revit ↔ GH cycle"""
    
    def __init__(self, workspace_dir: Path = None):
        self.workspace_dir = workspace_dir or Path(__file__).parent.parent
        self.exporter = RevitExporter()
        self.importer = RevitImporter()
        
        self.data_dir = self.workspace_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def export_from_revit(self, revit_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Export from Revit, save to disk, return data"""
        print("📤 Exporting from Revit...")
        
        export_data = self.exporter.export_all(revit_doc)
        export_path = self.exporter.save_export(export_data)
        
        # Also save a "current" snapshot for conflict detection
        snapshot_path = self.data_dir / "revit_snapshot.json"
        with open(snapshot_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Exported {len(export_data['elements']['walls'])} walls, "
              f"{len(export_data['elements']['openings'])} openings, "
              f"{len(export_data['elements']['floors'])} floors")
        
        return export_data
    
    def import_from_grasshopper(self, gh_data_path: Path) -> Dict[str, Any]:
        """Load GH modifications and prepare for Revit"""
        print("📥 Importing from Grasshopper...")
        
        with open(gh_data_path, 'r') as f:
            gh_data = json.load(f)
        
        revit_updates = self.importer.prepare_for_revit(gh_data)
        
        # Save for audit trail
        audit_path = self.data_dir / f"gh_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(audit_path, 'w') as f:
            json.dump(revit_updates, f, indent=2)
        
        print(f"✅ Imported {len(revit_updates['updates'])} modifications from GH")
        
        return revit_updates


if __name__ == "__main__":
    # Example: Simulate Revit export
    sample_revit_doc = {
        "file_path": "C:/Projects/MyBuilding.rvt",
        "project_name": "My Building Project",
        "epsg_code": "EPSG:32633",
        "origin_point": [0, 0, 0],
        "walls": [
            {
                "id": "12345",
                "name": "Exterior Wall North",
                "length": 50.0,
                "height": 3.5,
                "material": "Brick",
                "level": "Level 1",
                "curve_points": [[0, 0], [50, 0]]
            }
        ],
        "openings": [
            {
                "id": "54321",
                "name": "Main Door",
                "element_type": "Door",
                "width": 1.0,
                "height": 2.2,
                "family_type": "Single-Flush",
                "position": [10, 0]
            }
        ],
        "floors": [
            {
                "id": "99999",
                "name": "Floor 1",
                "level": "Level 1",
                "thickness": 0.3,
                "material": "Concrete",
                "boundary_points": [[0, 0], [50, 0], [50, 30], [0, 30], [0, 0]]
            }
        ]
    }
    
    bridge = RevitGHBridge()
    exported = bridge.export_from_revit(sample_revit_doc)
    print(json.dumps(exported, indent=2)[:500] + "...")
