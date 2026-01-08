# Revit ↔ Grasshopper ↔ ArcGIS Online Integration Guide

## 🎯 Overview

Compleet systeem voor automatische synchronisatie van Revit-modellen via Grasshopper naar ArcGIS Online met volledige versie-tracking en conflict resolution.

**Pipeline:**
```
Revit → SyncEngine → Grasshopper → ArcGIS Online
```

---

## 📦 Componenten

### 1. **merge_engine.py** - Core Sync Engine
- **Doel**: Centraal versie- en conflict management
- **Features**:
  - Unieke object IDs met metadata
  - Version tracking (semantische versionering)
  - Conflict detection & resolution
  - Synchronisatie logging

**Klasses:**
- `DataObject`: Geometrie + properties + versie
- `SyncMetadata`: Metadata en sync-geschiedenis
- `ConflictResolver`: Conflict resolution strategieën
- `SyncEngine`: Hoofdmotor

---

### 2. **revit_gh_bridge.py** - Revit ↔ Grasshopper Connector
- **Doel**: Gegevensuitwisseling tussen Revit en Grasshopper
- **Features**:
  - Muren, deuren/ramen, vloeren export
  - GeoJSON/JSON conversie
  - Coördinaattransformatie support
  - Revit ID ↔ GH GUID mapping

**Klasses:**
- `RevitExporter`: Export van Revit-elementen
- `RevitImporter`: Import van GH-wijzigingen
- `RevitGHBridge`: Orchestrator

---

### 3. **agol_exporter.py** - Grasshopper ↔ ArcGIS Online
- **Doel**: Export naar ArcGIS Online Feature Services
- **Features**:
  - GeoJSON conversie
  - AGOL authentication
  - Feature Service creation
  - Batch upload
  - Fallback naar lokale GeoJSON/Shapefile

**Klasses:**
- `GeoJSONConverter`: Geometry → GeoJSON
- `AGOLAuthentication`: AGOL token management
- `AGOLUploader`: Feature Service management
- `AGOLExporter`: Orchestrator

---

### 4. **integration_pipeline.py** - Main Orchestrator
- **Doel**: Complete pipeline automation
- **Stappen**:
  1. Revit export
  2. Sync engine processing
  3. Grasshopper input generation
  4. Grasshopper modification import
  5. ArcGIS Online export

---

## 🔧 Installation

### Requirements
```bash
python >= 3.8
requests
```

### Setup
```bash
# Install Python packages
pip install requests

# Create data directories
mkdir -p data/checkpoints
mkdir -p data/gh_inputs
mkdir -p data/gh_outputs
mkdir -p data/exports
mkdir -p data/revit_exports
mkdir -p .sync
```

---

## 📋 Workflow

### Scenario 1: Automatische One-Way Sync (Revit → GH → AGOL)

```python
from integration_pipeline import RevitGISIntegrationPipeline

# Initialize
pipeline = RevitGISIntegrationPipeline(
    agol_username="your_agol_user",
    agol_password="your_agol_password"
)

# Revit export (simulated data)
revit_data = {
    "file_path": "C:/Projects/Building.rvt",
    "project_name": "My Building",
    "epsg_code": "EPSG:32633",
    "walls": [...],  # Revit wall data
    "openings": [...],  # Doors/windows
    "floors": [...]  # Floor data
}

# Run pipeline
report = pipeline.run_full_pipeline(revit_data)
pipeline.print_summary(report)
```

### Scenario 2: Bidirectionele Sync met GH Modifications

```python
from pathlib import Path

# Run pipeline met GH output file
report = pipeline.run_full_pipeline(
    revit_data,
    wait_for_gh_input=Path("data/gh_outputs/modified_data.json")
)
```

### Scenario 3: Handmatige Stap-voor-stap Verwerking

```python
# STAP 1: Revit export
revit_export = pipeline.step_1_revit_export(revit_data)

# STAP 2: Sync engine
gh_data = pipeline.step_2_sync_and_version(revit_export)

# STAP 3: GH input file
gh_file = pipeline.step_3_export_grasshopper(gh_data)
print(f"Load this in Grasshopper: {gh_file}")

# [GH Scripting & Modifications...]

# STAP 4: GH output import
gh_modified = pipeline.step_4_import_grasshopper_modifications(
    Path("data/gh_outputs/your_output.json")
)

# STAP 5: AGOL export
success, agol_id = pipeline.step_5_export_arcgis_online(gh_modified)
print(f"AGOL Service ID: {agol_id}")
```

---

## 🧠 Conflict Resolution

Wanneer beide Revit en GH hetzelfde object wijzigen:

### Strategieën:

1. **last_write_wins** (default)
   - Meest recente wijziging wint
   - Kijk timestamp
   ```python
   resolver.resolve(original, revit_version, gh_version, 
                   strategy="last_write_wins")
   ```

2. **revit_priority**
   - Revit wijzigingen hebben voorrang
   ```python
   resolver.resolve(..., strategy="revit_priority")
   ```

3. **manual**
   - Gebruiker kiest
   - Geeft beide versies terug
   ```python
   resolver.resolve(..., strategy="manual")
   ```

---

## 📊 Data Format

### Revit Export Format
```json
{
  "timestamp": "2026-01-08T10:30:00",
  "file_path": "Building.rvt",
  "epsg_code": "EPSG:32633",
  "elements": {
    "walls": [
      {
        "id": "wall_123",
        "revit_id": "12345",
        "type": "Wall",
        "properties": {
          "name": "North Wall",
          "length": 50.0,
          "material": "Brick"
        },
        "geometry": {
          "type": "LineString",
          "coordinates": [[0,0], [50,0]]
        }
      }
    ]
  }
}
```

### Grasshopper Exchange Format
```json
[
  {
    "id": "wall_123",
    "gh_guid": "wall_123",
    "type": "Wall",
    "version": 2,
    "timestamp": "2026-01-08T10:35:00",
    "properties": {
      "name": "North Wall - Modified",
      "length": 52.5,
      "material": "Brick"
    },
    "geometry": {
      "type": "LineString",
      "coordinates": [[0,0], [52.5,0]]
    }
  }
]
```

### GeoJSON Format (voor AGOL)
```json
{
  "type": "FeatureCollection",
  "crs": {
    "type": "name",
    "properties": {"name": "EPSG:32633"}
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[0,0], [52.5,0]]
      },
      "properties": {
        "id": "wall_123",
        "type": "Wall",
        "version": 2,
        "name": "North Wall - Modified"
      }
    }
  ]
}
```

---

## 📁 Bestandsstructuur

```
Revit to GIS/
├── scripts/
│   ├── merge_engine.py              # Sync engine
│   ├── revit_gh_bridge.py           # Revit ↔ GH
│   ├── agol_exporter.py             # GH ↔ AGOL
│   └── integration_pipeline.py      # Main orchestrator
├── data/
│   ├── checkpoints/                 # Sync snapshots
│   ├── revit_exports/               # Revit exports
│   ├── gh_inputs/                   # GH input files
│   ├── gh_outputs/                  # GH output files
│   ├── exports/                     # Final GIS exports
│   ├── reports/                     # Pipeline reports
│   └── .sync/
│       └── metadata.json            # Metadata & versioning
└── README.md
```

---

## 🔐 ArcGIS Online Setup

### Vereisten
1. AGOL account met admin rights
2. API token (automatisch gegenereerd)

### Authenticatie
```python
auth = AGOLAuthentication(
    username="your_username",
    password="your_password",
    portal_url="https://www.arcgisonline.com/sharing/rest"
)

if auth.authenticate():
    print("✅ Authenticated")
```

### Feature Service Management
```python
uploader = AGOLUploader(auth)

# Create new service
service_id = uploader.create_feature_service(
    title="My Building Data",
    description="Auto-exported from Revit",
    tags=["revit", "grasshopper", "automated"]
)

# Upload data
uploader.upload_geojson(geojson_data, service_id)
```

---

## 📊 Metadata & Versioning

Alle objecten krijgen automatisch:
- **Unieke ID** (`id`)
- **Revit referentie** (`revit_id`)
- **GH GUID** (`gh_guid`)
- **Versienummer** (incrementeel)
- **Timestamp** (ISO 8601)
- **Content hash** (wijzigingen detectie)

### Metadata File
```json
{
  "version": 1,
  "created": "2026-01-08T10:30:00",
  "objects": {
    "wall_123": {
      "gh_guid": "wall_123",
      "revit_id": "12345",
      "type": "Wall",
      "version": 2,
      "timestamp": "2026-01-08T10:35:00",
      "hash": "a1b2c3d4..."
    }
  },
  "sync_history": [
    {
      "timestamp": "2026-01-08T10:30:00",
      "type": "import",
      "object_id": "wall_123",
      "from": "revit",
      "to": "local",
      "status": "success"
    }
  ]
}
```

---

## ⚠️ Bekende Beperkingen & Opmerkingen

### Coördinaatransformatie
- **Revit**: Werkt met projectcoördinaten (willekeurig origin)
- **GIS**: Gebruikt geografische coördinaten (lat/lng) of UTM
- **Oplossing**: `origin_point` en `epsg_code` in export instellen

### ID Management
- Object IDs moeten uniek zijn binnen project
- GH GUID wordt gekoppeld aan Revit ID
- Bij wijzigingen: versienummer verhogen, hash updaten

### Performance
- Max ~2000 features per batch naar AGOL (AGOL limiet)
- Grotere datasets: splits in batches

### Edge Cases
1. **Gelijktijdige wijzigingen**: Conflict resolver bepaalt winner
2. **Verwijderde objecten**: Version tracking voorkomt hervorming
3. **Nieuwe objecten**: GH kan nieuwe objecten toevoegen (ID auto-generate)

---

## 🧪 Testing

```python
# Test 1: Sync engine
engine = SyncEngine()
test_data = [...] 
gh_output = engine.sync_revit_to_gh(test_data)
assert len(gh_output) > 0

# Test 2: GeoJSON conversie
converter = GeoJSONConverter()
geojson = converter.gh_to_geojson(gh_data)
assert geojson["type"] == "FeatureCollection"

# Test 3: Full pipeline
pipeline = RevitGISIntegrationPipeline()
report = pipeline.run_full_pipeline(sample_revit)
assert report["status"] in ["success", "partial_success"]
```

---

## 📈 Toekomstuitbreidingen

- [ ] Bidirectionele updates (AGOL → Revit)
- [ ] Real-time file watcher triggers
- [ ] Revit add-in UI
- [ ] GH plugin voor UI
- [ ] WebSocket support voor live updates
- [ ] Database backend (PostGIS)
- [ ] Cloud storage (S3/Blob)

---

## 📞 Troubleshooting

| Probleem | Oorzaak | Oplossing |
|----------|---------|----------|
| AGOL authentication fails | Verkeerde credentials | Check username/password |
| GH file not found | File nog niet klaar | Verhoog timeout |
| Coördinaten kloppen niet | EPSG code verkeerd | Check coördinaatframe |
| Conflict niet opgelost | Strategy niet ingesteld | Set conflict strategy |
| Memory error (grote datasets) | Dataset te groot | Split in batches |

---

## 📝 Logging

Alle acties worden gelogd naar:
- **Console**: INFO level
- **Files**: `data/reports/` directory

Log levels:
- `INFO`: Normale operaties
- `WARNING`: Potentiële problemen
- `ERROR`: Mislukkingen

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Verbose output
```

---

## 📄 Licentie & Support

Contact: [Your contact info]

---

**Last updated**: January 8, 2026
