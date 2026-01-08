"""
Revit ↔ Grasshopper ↔ ArcGIS Online Sync Engine
Handles version tracking, conflict resolution, and data synchronization
"""

import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataObject:
    """Represents a single geometric object with versioning"""
    
    def __init__(self, obj_id: str, obj_type: str, properties: Dict[str, Any], 
                 geometry: Dict[str, Any], source: str = "unknown"):
        self.id = obj_id
        self.type = obj_type
        self.properties = properties
        self.geometry = geometry
        self.source = source
        self.version = 1
        self.timestamp = datetime.now().isoformat()
        self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute unique hash of object state"""
        data = json.dumps({
            "type": self.type,
            "properties": self.properties,
            "geometry": self.geometry
        }, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "properties": self.properties,
            "geometry": self.geometry,
            "version": self.version,
            "timestamp": self.timestamp,
            "hash": self.hash,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        obj = cls(
            obj_id=data["id"],
            obj_type=data["type"],
            properties=data.get("properties", {}),
            geometry=data.get("geometry", {}),
            source=data.get("source", "unknown")
        )
        obj.version = data.get("version", 1)
        obj.timestamp = data.get("timestamp", datetime.now().isoformat())
        obj.hash = data.get("hash", obj._compute_hash())
        return obj


class SyncMetadata:
    """Tracks synchronization state and history"""
    
    def __init__(self, metadata_file: Path):
        self.metadata_file = metadata_file
        self.data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                logger.warning(f"Failed to load metadata from {self.metadata_file}")
        
        return {
            "version": 1,
            "created": datetime.now().isoformat(),
            "objects": {},
            "sync_history": []
        }
    
    def save(self):
        """Persist metadata to disk"""
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        logger.info(f"Metadata saved to {self.metadata_file}")
    
    def register_object(self, obj: DataObject, revit_id: Optional[str] = None):
        """Register object with mapping info"""
        self.data["objects"][obj.id] = {
            "gh_guid": obj.id,
            "revit_id": revit_id or f"rev_{obj.id[:8]}",
            "type": obj.type,
            "version": obj.version,
            "timestamp": obj.timestamp,
            "hash": obj.hash,
            "source": obj.source
        }
    
    def get_object_meta(self, obj_id: str) -> Optional[Dict[str, Any]]:
        return self.data["objects"].get(obj_id)
    
    def add_sync_event(self, event_type: str, obj_id: str, source: str, 
                       target: str, status: str, details: str = ""):
        """Log synchronization event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "object_id": obj_id,
            "from": source,
            "to": target,
            "status": status,
            "details": details
        }
        self.data["sync_history"].append(event)
        logger.info(f"Sync event: {event_type} - {source}→{target} [{status}]")


class ConflictResolver:
    """Resolves conflicts when data changes in multiple sources"""
    
    def __init__(self):
        self.strategies = {
            "last_write_wins": self._last_write_wins,
            "revit_priority": self._revit_priority,
            "manual": self._manual_resolution
        }
    
    def detect_conflict(self, original: DataObject, revit_version: DataObject, 
                       gh_version: DataObject) -> Tuple[bool, str]:
        """Detect if conflict exists"""
        if revit_version.hash == gh_version.hash:
            return False, "no_conflict"
        
        if revit_version.hash == original.hash:
            return False, "only_gh_changed"
        
        if gh_version.hash == original.hash:
            return False, "only_revit_changed"
        
        return True, "both_changed"
    
    def resolve(self, original: DataObject, revit_version: DataObject, 
                gh_version: DataObject, strategy: str = "last_write_wins") -> DataObject:
        """Resolve conflict using specified strategy"""
        
        conflict_exists, conflict_type = self.detect_conflict(original, revit_version, gh_version)
        
        if not conflict_exists:
            if conflict_type == "only_gh_changed":
                return gh_version
            elif conflict_type == "only_revit_changed":
                return revit_version
            else:
                return original
        
        resolver = self.strategies.get(strategy, self._last_write_wins)
        return resolver(original, revit_version, gh_version)
    
    def _last_write_wins(self, original: DataObject, revit: DataObject, 
                         gh: DataObject) -> DataObject:
        """Most recent modification wins"""
        revit_time = datetime.fromisoformat(revit.timestamp)
        gh_time = datetime.fromisoformat(gh.timestamp)
        
        winner = revit if revit_time > gh_time else gh
        logger.warning(f"Conflict resolved using last_write_wins: {winner.source} wins")
        return winner
    
    def _revit_priority(self, original: DataObject, revit: DataObject, 
                        gh: DataObject) -> DataObject:
        """Revit changes always win"""
        logger.warning(f"Conflict resolved using revit_priority")
        return revit
    
    def _manual_resolution(self, original: DataObject, revit: DataObject, 
                           gh: DataObject) -> DataObject:
        """Returns both versions for user to decide"""
        logger.error(f"Manual resolution required for {original.id}")
        return None


class SyncEngine:
    """Main synchronization engine"""
    
    def __init__(self, workspace_dir: Path = None):
        self.workspace_dir = workspace_dir or Path(__file__).parent.parent / "data"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata = SyncMetadata(self.workspace_dir / ".sync" / "metadata.json")
        self.conflict_resolver = ConflictResolver()
        self.objects: Dict[str, DataObject] = {}
    
    def import_from_revit(self, revit_data: List[Dict[str, Any]]) -> List[DataObject]:
        """Import geometry/data from Revit"""
        imported = []
        
        for item in revit_data:
            obj_id = item.get("id", str(uuid.uuid4()))
            obj = DataObject(
                obj_id=obj_id,
                obj_type=item.get("type", "Unknown"),
                properties=item.get("properties", {}),
                geometry=item.get("geometry", {}),
                source="revit"
            )
            
            self.objects[obj_id] = obj
            self.metadata.register_object(obj, revit_id=item.get("revit_id"))
            self.metadata.add_sync_event(
                "import", obj_id, "revit", "local", "success"
            )
            imported.append(obj)
        
        self.metadata.save()
        return imported
    
    def export_to_grasshopper(self) -> List[Dict[str, Any]]:
        """Export objects for Grasshopper consumption"""
        gh_format = []
        
        for obj_id, obj in self.objects.items():
            meta = self.metadata.get_object_meta(obj_id)
            gh_format.append({
                "id": obj.id,
                "gh_guid": meta.get("gh_guid") if meta else obj.id,
                "type": obj.type,
                "properties": obj.properties,
                "geometry": obj.geometry,
                "version": obj.version,
                "timestamp": obj.timestamp
            })
        
        return gh_format
    
    def import_from_grasshopper(self, gh_data: List[Dict[str, Any]]):
        """Receive modified data from Grasshopper"""
        for item in gh_data:
            obj_id = item.get("id")
            
            if obj_id not in self.objects:
                # New object from GH
                obj = DataObject(
                    obj_id=obj_id,
                    obj_type=item.get("type", "Unknown"),
                    properties=item.get("properties", {}),
                    geometry=item.get("geometry", {}),
                    source="grasshopper"
                )
                self.objects[obj_id] = obj
                self.metadata.add_sync_event(
                    "create", obj_id, "grasshopper", "local", "success"
                )
            else:
                # Update existing object
                old_obj = self.objects[obj_id]
                new_obj = DataObject.from_dict(item)
                new_obj.source = "grasshopper"
                new_obj.version = old_obj.version + 1
                
                self.objects[obj_id] = new_obj
                self.metadata.add_sync_event(
                    "update", obj_id, "grasshopper", "local", "success"
                )
        
        self.metadata.save()
    
    def sync_revit_to_gh(self, revit_data: List[Dict[str, Any]]):
        """Full sync: Revit → Local → Grasshopper"""
        logger.info("Starting Revit→GH sync...")
        
        # Step 1: Import from Revit
        self.import_from_revit(revit_data)
        
        # Step 2: Check for conflicts
        conflicts = self._check_conflicts()
        if conflicts:
            logger.warning(f"Found {len(conflicts)} conflicts, resolving...")
            self._resolve_conflicts(conflicts)
        
        # Step 3: Export to GH
        gh_data = self.export_to_grasshopper()
        
        logger.info(f"Sync complete. Exported {len(gh_data)} objects to GH")
        return gh_data
    
    def _check_conflicts(self) -> List[Tuple[str, str]]:
        """Check for concurrent modifications"""
        conflicts = []
        # Placeholder - implement based on actual conflict detection logic
        return conflicts
    
    def _resolve_conflicts(self, conflicts: List[Tuple[str, str]], 
                          strategy: str = "last_write_wins"):
        """Resolve detected conflicts"""
        for obj_id, conflict_type in conflicts:
            logger.warning(f"Resolving conflict in {obj_id}: {conflict_type}")
    
    def get_object(self, obj_id: str) -> Optional[DataObject]:
        return self.objects.get(obj_id)
    
    def list_objects(self) -> List[DataObject]:
        return list(self.objects.values())
    
    def save_state(self, filepath: Path):
        """Save all objects to file"""
        data = {
            "objects": [obj.to_dict() for obj in self.objects.values()],
            "metadata": self.metadata.data
        }
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"State saved to {filepath}")
    
    def load_state(self, filepath: Path):
        """Load objects from file"""
        if not filepath.exists():
            logger.warning(f"State file not found: {filepath}")
            return
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for obj_data in data.get("objects", []):
            obj = DataObject.from_dict(obj_data)
            self.objects[obj.id] = obj
        
        logger.info(f"State loaded from {filepath}")


if __name__ == "__main__":
    # Example usage
    engine = SyncEngine()
    
    # Example Revit data
    revit_data = [
        {
            "id": "obj_001",
            "type": "Wall",
            "revit_id": "12345",
            "properties": {"length": 10.5, "material": "Concrete"},
            "geometry": {"type": "LineString", "coordinates": [[0, 0], [10.5, 0]]}
        }
    ]
    
    # Sync from Revit to GH
    gh_data = engine.sync_revit_to_gh(revit_data)
    print("GH Data:", json.dumps(gh_data, indent=2))
