# Revit ↔ GIS System Architecture

## 📐 System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   REVIT ↔ GRASSHOPPER ↔ ARCGIS                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                         REVIT (Input)                                │
│  • Walls                                                             │
│  • Floors                                                            │
│  • Doors/Windows                                                     │
│  • Columns, Beams, etc.                                              │
└────────────────┬─────────────────────────────────────────────────────┘
                 │
                 ↓
         ┌───────────────────┐
         │  RevitGHBridge    │
         │  (Data Export)    │
         └──────────┬────────┘
                    │
                    ↓
         ┌──────────────────────────────────────┐
         │      JSON Format (Unique IDs)        │
         │  - id: wall_001                      │
         │  - revit_id: 12345                   │
         │  - properties: {...}                 │
         │  - geometry: {...}                   │
         └──────────┬───────────────────────────┘
                    │
                    ↓
    ┌───────────────────────────────────────────────┐
    │         SYNC ENGINE (Core Logic)              │
    │                                               │
    │  ┌──────────────────────────────────────────┐ │
    │  │  DataObject (Versioning)                 │ │
    │  │  - version: 1, 2, 3...                   │ │
    │  │  - timestamp                             │ │
    │  │  - hash (change detection)               │ │
    │  └──────────────────────────────────────────┘ │
    │                                               │
    │  ┌──────────────────────────────────────────┐ │
    │  │  SyncMetadata (Tracking)                 │ │
    │  │  - Object mapping (Revit ↔ GH)          │ │
    │  │  - Sync history                          │ │
    │  │  - Conflict log                          │ │
    │  └──────────────────────────────────────────┘ │
    │                                               │
    │  ┌──────────────────────────────────────────┐ │
    │  │  ConflictResolver                        │ │
    │  │  - last_write_wins                       │ │
    │  │  - revit_priority                        │ │
    │  │  - manual resolution                     │ │
    │  └──────────────────────────────────────────┘ │
    └──────────┬────────────────────────────────────┘
               │
               ↓
        ┌──────────────────────┐
        │  GRASSHOPPER (GH)    │
        │                      │
        │  • Load input JSON   │
        │  • Modify geometry   │
        │  • Add properties    │
        │  • Save output JSON  │
        │                      │
        │  GrassholperHelper:  │
        │  - load_input_data() │
        │  - update_object()   │
        │  - save_output()     │
        └──────────┬───────────┘
                   │
                   ↓
        ┌──────────────────────┐
        │  Modified JSON Data  │
        │  (Same format but    │
        │   v2+ changes)       │
        └──────────┬───────────┘
                   │
                   ↓
  ┌──────────────────────────────────┐
  │  AGOLExporter (Export)           │
  │                                  │
  │  • GeoJSON conversion            │
  │  • Coordinate transform          │
  │  • AGOL authentication           │
  │  • Feature Service creation      │
  │  • Batch upload                  │
  └──────────┬───────────────────────┘
             │
             ↓
  ┌──────────────────────────────────┐
  │  ARCGIS ONLINE (Output)          │
  │                                  │
  │  Feature Service:                │
  │  • Walls layer                   │
  │  • Openings layer                │
  │  • Floors layer                  │
  │  • Attributes                    │
  │  • Public URL                    │
  └──────────────────────────────────┘
```

---

## 🔄 Data Flow with Versioning

```
TIME POINT 1 - INITIAL EXPORT
═════════════════════════════

Revit Model
    │
    └─→ RevitExporter.export_all()
         │
         └─→ [ objects... ]
              │
              └─→ JSON (version 1)
                   │
                   └─→ data/gh_inputs/gh_input_*.json


TIME POINT 2 - GRASSHOPPER MODIFICATIONS  
══════════════════════════════════════════

Load → gh_input_*.json
   │
   ├─ Wall_001 (v1) ──→ User modifies length ──→ Wall_001 (v2)
   ├─ Floor_001 (v1) ──→ No change ──────────→ Floor_001 (v1)
   └─ Door_001 (v1) ──→ User deletes ────────→ Door_001 (v2, deleted=true)
   │
   └─→ data/gh_outputs/gh_output_*.json


TIME POINT 3 - CONFLICT CHECK
══════════════════════════════

If Revit was modified simultaneously:

Original (v1):
┌──────────────────┐
│ Wall_001: length │
│ = 50             │
└──────────────────┘

                  ├─ Revit changed → 52
                  │
                  └─ GH changed → 48
                        │
                        ↓
              ⚠️ CONFLICT DETECTED!
              
              ConflictResolver:
              • Timestamp check (who's newest?)
              • Apply strategy
              • Resulting: 52 (revit_priority)


TIME POINT 4 - EXPORT TO AGOL
══════════════════════════════

Resolved objects (v2+)
    │
    └─→ GeoJSONConverter.gh_to_geojson()
         │
         └─→ GeoJSON FeatureCollection
              │
              └─→ AGOLExporter.export_to_agol()
                   │
                   ├─ Authenticate
                   ├─ Create Feature Service
                   ├─ Upload features
                   │
                   └─→ AGOL Service ID: "abc123xyz"
```

---

## 📊 Metadata & Tracking

```json
{
  "version": 1,
  "created": "2026-01-08T10:00:00",
  "objects": {
    "wall_001": {
      "gh_guid": "wall_001",
      "revit_id": "12345",
      "type": "Wall",
      "version": 2,
      "timestamp": "2026-01-08T10:35:00",
      "hash": "a1b2c3d4e5f6..."
    }
  },
  "sync_history": [
    {
      "timestamp": "2026-01-08T10:00:00",
      "type": "import",
      "object_id": "wall_001",
      "from": "revit",
      "to": "local",
      "status": "success"
    },
    {
      "timestamp": "2026-01-08T10:35:00", 
      "type": "update",
      "object_id": "wall_001",
      "from": "grasshopper",
      "to": "local",
      "status": "success"
    },
    {
      "timestamp": "2026-01-08T10:40:00",
      "type": "conflict",
      "object_id": "wall_001",
      "resolution": "last_write_wins",
      "status": "resolved"
    }
  ]
}
```

---

## 🔀 Conflict Resolution Logic

```python
def resolve_conflict(original, revit_version, gh_version, strategy):
    
    # STEP 1: Detect what changed
    if hash(revit_version) == hash(gh_version):
        return "Same modification → Use either"
    
    if hash(revit_version) == hash(original):
        return "Only GH changed → Use GH version"
    
    if hash(gh_version) == hash(original):
        return "Only Revit changed → Use Revit version"
    
    # STEP 2: Both changed differently → Apply strategy
    if strategy == "last_write_wins":
        if timestamp(revit_version) > timestamp(gh_version):
            return revit_version
        else:
            return gh_version
    
    elif strategy == "revit_priority":
        return revit_version
    
    elif strategy == "manual":
        return ask_user(revit_version, gh_version)
```

---

## 📂 Module Responsibilities

| Module | Input | Output | Key Responsibility |
|--------|-------|--------|-------------------|
| RevitGHBridge | Revit API data | JSON objects | Extract & format geometry |
| SyncEngine | JSON objects | Versioned objects | Track changes & conflicts |
| ConflictResolver | 2+ versions | 1 resolved version | Merge strategies |
| GrassholperHelper | JSON file | Modified JSON | Load/save for GH |
| GeoJSONConverter | JSON objects | GeoJSON | Standards compliance |
| AGOLExporter | GeoJSON | AGOL Service ID | Cloud upload & auth |
| Pipeline | Revit data | AGOL URL | Orchestrate all steps |

---

## 🎯 Integration Points

### 1. Revit Add-In → RevitGHBridge
```csharp
// C# in Revit Add-In
var wallData = ExtractRevitWalls(doc);
var exportData = new RevitExporter().export_walls(wallData);
```

### 2. Grasshopper → GrassholperHelper
```python
# Python in Grasshopper
from gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
data = helper.load_input_data()
# [Modify in GH...]
helper.save_output_data(data)
```

### 3. ArcGIS Online Integration
```python
# From Python
pipeline = RevitGISIntegrationPipeline(
    agol_username="...", 
    agol_password="..."
)
success, agol_id = pipeline.step_5_export_arcgis_online(gh_data)
```

---

## ⚡ Performance Considerations

| Bottleneck | Solution |
|-----------|----------|
| Large Revit models (1000+ elements) | Batch processing, filter by type |
| AGOL batch upload limit (2000 features) | Split into multiple uploads |
| Conflict resolution on big datasets | Index by timestamp, process in chunks |
| Network latency to AGOL | Local caching, async uploads |

---

## 🔐 Security Considerations

- **AGOL Credentials**: Store in environment variables or secrets manager
- **API Keys**: Never commit to version control
- **Data Validation**: Validate geometry before AGOL upload
- **Audit Trail**: Metadata tracks all changes for compliance

---

## 🚀 Extensibility

Easy to add:
- New element types (Roofs, Stairs, etc.)
- Custom coordinate systems
- Additional conflict strategies
- Post-processing hooks
- Database backend (PostgreSQL + PostGIS)
- Real-time file watchers

