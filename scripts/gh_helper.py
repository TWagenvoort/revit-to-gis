"""
Grasshopper Integration Helper Script
Import/Export data from/to Grasshopper in Python
Can be used with IronPython in Grasshopper or as standalone script

Usage in Grasshopper:
    1. Import this module: import sys; sys.path.append(r'C:\path\to\scripts')
    2. Create GHHelper instance: helper = GHHelper()
    3. Load data: gh_data = helper.load_input_data()
    4. Process geometry...
    5. Save data: helper.save_output_data(modified_data)
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrassholperDataHelper:
    """Helper class for Grasshopper data I/O"""
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize helper
        
        Args:
            data_dir: Path to data directory. If None, assumes relative path.
                     Can also be a string like r"C:\Users\...\data"
        """
        if data_dir is None:
            # Try to find data directory relative to script location
            try:
                script_dir = Path(__file__).parent.parent
                data_dir = script_dir / "data"
            except:
                # Fallback for Grasshopper where __file__ might not work
                data_dir = Path.home() / "Desktop" / "Revit to GIS" / "data"
        elif isinstance(data_dir, str):
            data_dir = Path(data_dir)
        
        self.data_dir = Path(data_dir)
        self.gh_input_dir = self.data_dir / "gh_inputs"
        self.gh_output_dir = self.data_dir / "gh_outputs"
        
        # Create directories if needed
        try:
            self.gh_input_dir.mkdir(parents=True, exist_ok=True)
            self.gh_output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create directories: {e}")
            logger.warning(f"Data dir: {self.data_dir}")
        
        self.current_input_file = None
        self.current_data = []
    
    def load_input_data(self, filename: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load input data from Revit export
        
        Args:
            filename: Specific file to load. If None, loads latest.
        
        Returns:
            List of geometry objects
        """
        
        try:
            if filename:
                filepath = self.gh_input_dir / filename
            else:
                # Find latest input file
                input_files = list(self.gh_input_dir.glob("gh_input_*.json"))
                if not input_files:
                    logger.warning("No input files found in gh_inputs/")
                    return []
                
                filepath = max(input_files, key=lambda p: p.stat().st_mtime)
            
            if not filepath.exists():
                logger.error(f"Input file not found: {filepath}")
                return []
            
            with open(filepath, 'r') as f:
                self.current_data = json.load(f)
            
            self.current_input_file = filepath
            logger.info(f"✅ Loaded {len(self.current_data)} objects from {filepath.name}")
            
            return self.current_data
        
        except Exception as e:
            logger.error(f"Error loading input data: {e}")
            return []
    
    def save_output_data(self, modified_data: List[Dict[str, Any]], 
                        filename: Optional[str] = None) -> Path:
        """
        Save modified data for AGOL export
        
        Args:
            modified_data: List of modified geometry objects
            filename: Custom filename. If None, auto-generates.
        
        Returns:
            Path to saved file
        """
        
        try:
            if filename is None:
                filename = f"gh_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = self.gh_output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(modified_data, f, indent=2)
            
            logger.info(f"✅ Saved {len(modified_data)} modified objects to {filepath.name}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error saving output data: {e}")
            return None
    
    def get_object_by_id(self, obj_id: str) -> Optional[Dict[str, Any]]:
        """Get specific object by ID"""
        for obj in self.current_data:
            if obj.get("id") == obj_id:
                return obj
        return None
    
    def update_object(self, obj_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update object properties (while preserving geometry if not specified)
        
        Args:
            obj_id: Object ID to update
            updates: Dictionary of updates
        
        Returns:
            True if successful
        """
        
        obj = self.get_object_by_id(obj_id)
        if not obj:
            logger.warning(f"Object not found: {obj_id}")
            return False
        
        # Update properties
        if "properties" in updates:
            obj["properties"].update(updates["properties"])
        
        # Update geometry if provided
        if "geometry" in updates:
            obj["geometry"] = updates["geometry"]
        
        # Increment version
        obj["version"] = obj.get("version", 1) + 1
        obj["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Updated {obj_id} to version {obj['version']}")
        return True
    
    def add_new_object(self, obj_type: str, properties: Dict[str, Any],
                      geometry: Dict[str, Any], obj_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Add new object to data
        
        Args:
            obj_type: Type of object (Wall, Floor, etc.)
            properties: Object properties
            geometry: Geometry in GeoJSON format
            obj_id: Custom ID. If None, auto-generates.
        
        Returns:
            Created object
        """
        
        if obj_id is None:
            obj_id = f"gh_new_{len(self.current_data)}"
        
        new_obj = {
            "id": obj_id,
            "gh_guid": obj_id,
            "type": obj_type,
            "version": 1,
            "timestamp": datetime.now().isoformat(),
            "properties": properties,
            "geometry": geometry
        }
        
        self.current_data.append(new_obj)
        logger.info(f"Added new object: {obj_id}")
        
        return new_obj
    
    def delete_object(self, obj_id: str) -> bool:
        """Mark object as deleted (soft delete for audit trail)"""
        
        obj = self.get_object_by_id(obj_id)
        if not obj:
            logger.warning(f"Object not found: {obj_id}")
            return False
        
        obj["deleted"] = True
        obj["deleted_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Marked object as deleted: {obj_id}")
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of current data"""
        
        type_counts = {}
        for obj in self.current_data:
            obj_type = obj.get("type", "Unknown")
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        return {
            "total_objects": len(self.current_data),
            "types": type_counts,
            "input_file": str(self.current_input_file) if self.current_input_file else None,
            "last_modified": self.current_data[-1].get("timestamp") if self.current_data else None
        }
    
    def print_summary(self):
        """Print data summary to console"""
        summary = self.get_summary()
        
        print("\n" + "="*50)
        print("GRASSHOPPER DATA SUMMARY")
        print("="*50)
        print(f"Total objects: {summary['total_objects']}")
        print(f"Types: {summary['types']}")
        if summary['input_file']:
            print(f"Input file: {summary['input_file']}")
        print("="*50 + "\n")


class GrassholperGeometryHelper:
    """Helper for geometry manipulation in Grasshopper"""
    
    @staticmethod
    def linestring_to_points(coordinates: List[List[float]]) -> List[tuple]:
        """Convert LineString coordinates to point tuples"""
        return [tuple(coord) for coord in coordinates]
    
    @staticmethod
    def polygon_to_vertices(coordinates: List[List[List[float]]]) -> List[tuple]:
        """Convert Polygon coordinates to vertices"""
        if coordinates:
            return [tuple(coord) for coord in coordinates[0]]  # First ring (exterior)
        return []
    
    @staticmethod
    def point_to_tuple(coordinates: List[float]) -> tuple:
        """Convert Point coordinates to tuple"""
        return tuple(coordinates[:3]) if len(coordinates) >= 3 else tuple(coordinates) + (0,) * (3 - len(coordinates))
    
    @staticmethod
    def geometry_to_gh_curve(geometry: Dict[str, Any]):
        """
        Convert GeoJSON geometry to Grasshopper-compatible format
        
        This is a helper - actual conversion depends on Grasshopper rhinoscriptsyntax
        
        Returns coordinates as nested list of points
        """
        
        geom_type = geometry.get("type", "").lower()
        coords = geometry.get("coordinates", [])
        
        if geom_type == "point":
            return coords
        elif geom_type == "linestring":
            return coords
        elif geom_type == "polygon":
            return coords[0] if coords else []  # Exterior ring
        else:
            return []


class GrassholperPipeline:
    """Complete workflow for GH-based processing"""
    
    def __init__(self, data_dir: Path = None):
        self.helper = GrassholperDataHelper(data_dir)
        self.geom_helper = GrassholperGeometryHelper()
    
    def load_and_analyze(self) -> Dict[str, Any]:
        """Load data and provide analysis"""
        
        print("\n🚀 Loading Grasshopper input data...")
        data = self.helper.load_input_data()
        
        if not data:
            print("❌ No data to process")
            return {}
        
        self.helper.print_summary()
        
        # Analyze geometry types
        analysis = {
            "loaded_objects": len(data),
            "geometry_types": {},
            "properties_sample": data[0].get("properties", {}) if data else {}
        }
        
        for obj in data:
            geom_type = obj.get("geometry", {}).get("type", "Unknown")
            analysis["geometry_types"][geom_type] = analysis["geometry_types"].get(geom_type, 0) + 1
        
        print(f"\n📊 Geometry Analysis:")
        for geom_type, count in analysis["geometry_types"].items():
            print(f"  {geom_type}: {count}")
        
        return analysis
    
    def process_example(self) -> List[Dict[str, Any]]:
        """Example processing: Scale all features by 1.5x"""
        
        print("\n⚙️  Processing: Scaling coordinates by 1.5x...")
        
        self.helper.load_input_data()
        
        for obj in self.helper.current_data:
            geometry = obj.get("geometry", {})
            coords = geometry.get("coordinates", [])
            
            # Simple scaling example
            scaled_coords = self._scale_coordinates(coords, 1.5)
            geometry["coordinates"] = scaled_coords
            
            # Update version info
            obj["version"] = obj.get("version", 1) + 1
            obj["timestamp"] = datetime.now().isoformat()
        
        print(f"✅ Processed {len(self.helper.current_data)} objects")
        return self.helper.current_data
    
    @staticmethod
    def _scale_coordinates(coords: Any, scale_factor: float) -> Any:
        """Recursively scale coordinates"""
        if isinstance(coords[0], (list, tuple)):
            return [GrassholperPipeline._scale_coordinates(c, scale_factor) for c in coords]
        else:
            return [val * scale_factor for val in coords]
    
    def save_and_export(self):
        """Save processed data for AGOL export"""
        
        filepath = self.helper.save_output_data(self.helper.current_data)
        
        print(f"\n✅ Saved to: {filepath}")
        print(f"   Next step: Run integration_pipeline.py to export to AGOL")
        
        return filepath


if __name__ == "__main__":
    # Example standalone usage
    
    print("Grasshopper Integration Helper")
    print("================================\n")
    
    # Initialize
    pipeline = GrassholperPipeline()
    
    # Load and analyze
    analysis = pipeline.load_and_analyze()
    
    if analysis.get("loaded_objects", 0) > 0:
        # Process (example: scale)
        processed = pipeline.process_example()
        
        # Save
        pipeline.save_and_export()
    else:
        print("\n⚠️  No data found. Create gh_inputs/gh_input_*.json first.")
        print("   Run: python revit_gh_bridge.py")
