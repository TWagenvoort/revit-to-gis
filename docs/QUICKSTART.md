# Quick Start Guide - Revit to GIS Pipeline

## 🎯 5-Minute Setup

### 1. **Install Dependencies**
```bash
cd "c:\Users\Thijs W\Desktop\Revit to GIS"
pip install requests
```

### 2. **Run Example Pipeline**
```bash
cd scripts
python integration_pipeline.py
```

Expected output:
```
✅ Export successful!
📋 Report saved to: data/reports/pipeline_report_*.json
```

---

## 📊 Step-by-Step Workflow

### Option A: Automated Full Pipeline

```python
from pathlib import Path
from integration_pipeline import RevitGISIntegrationPipeline

# 1. Initialize pipeline
pipeline = RevitGISIntegrationPipeline()

# 2. Prepare Revit data (from your Revit API/add-in)
revit_data = {
    "file_path": "C:/Projects/Building.rvt",
    "project_name": "My Building",
    "epsg_code": "EPSG:32633",  # UTM 33N for Netherlands
    "walls": [
        {
            "id": "w1",
            "name": "North Wall",
            "length": 50.0,
            "curve_points": [[0, 0], [50, 0]]
        }
    ],
    "openings": [],
    "floors": []
}

# 3. Run full pipeline
report = pipeline.run_full_pipeline(revit_data)
pipeline.print_summary(report)
```

### Option B: Step-by-Step with GH Modifications

```python
# Step 1: Export from Revit
revit_export = pipeline.step_1_revit_export(revit_data)

# Step 2: Sync & version
gh_data = pipeline.step_2_sync_and_version(revit_export)

# Step 3: Export to Grasshopper
gh_input_file = pipeline.step_3_export_grasshopper(gh_data)
print(f"📁 Load this in Grasshopper: {gh_input_file}")

# [Now modify in Grasshopper...]

# Step 4: Import GH modifications
gh_modified = pipeline.step_4_import_grasshopper_modifications(
    Path("data/gh_outputs/your_modified.json")
)

# Step 5: Export to ArcGIS Online
success, agol_id = pipeline.step_5_export_arcgis_online(gh_modified)
```

---

## 🦗 Grasshopper Integration

### In Grasshopper Python Component:

```python
from pathlib import Path
import sys

# Add scripts to path
sys.path.append(r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperPipeline

# Load data from Revit
pipeline = GrassholperPipeline()
pipeline.load_and_analyze()

# [Modify geometry in GH...]

# Save for AGOL
pipeline.save_and_export()
```

### Or in IronPython:

```python
# IronPython in Grasshopper
from gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
data = helper.load_input_data()

# Process your geometry...

helper.save_output_data(data, "gh_output.json")
```

---

## 🗂️ File Structure After First Run

```
Revit to GIS/
├── scripts/
│   ├── merge_engine.py
│   ├── revit_gh_bridge.py
│   ├── agol_exporter.py
│   ├── integration_pipeline.py
│   ├── gh_helper.py
│   ├── config.py
│   └── __init__.py (create this)
└── data/
    ├── checkpoints/
    │   └── sync_checkpoint_*.json
    ├── revit_exports/
    │   └── revit_export_*.json
    ├── gh_inputs/
    │   └── gh_input_*.json
    ├── gh_outputs/
    │   └── gh_output_*.json
    ├── exports/
    │   └── agol_export_*.geojson
    ├── reports/
    │   └── pipeline_report_*.json
    └── .sync/
        └── metadata.json
```

---

## 🔑 Key Concepts

### 1. **Data Flow**
```
Revit Model
    ↓
Export walls/floors/openings
    ↓
Create JSON with unique IDs
    ↓
Grasshopper (modify geometry)
    ↓
Save modified JSON
    ↓
Convert to GeoJSON
    ↓
Upload to ArcGIS Online
```

### 2. **Versioning**
- Every object gets a **unique ID** (`id`)
- **Version number** increments on changes
- **Timestamp** tracks when modified
- **Content hash** detects changes

### 3. **Conflict Resolution**
If Revit and GH both modify same object:
- **last_write_wins** (default): Most recent change wins
- **revit_priority**: Revit always wins  
- **manual**: User decides

```python
from merge_engine import ConflictResolver

resolver = ConflictResolver()
resolved_obj = resolver.resolve(
    original, revit_version, gh_version,
    strategy="last_write_wins"
)
```

---

## 🎯 Common Tasks

### Export Specific Element Types Only

```python
# Modify revit_data before pipeline
revit_data = {
    "walls": [...],
    "openings": [],  # Skip doors/windows
    "floors": [...]
}
```

### Use Different Coordinate System

```python
revit_data = {
    "epsg_code": "EPSG:4326",  # WGS84
    # or
    "epsg_code": "EPSG:28992",  # RD (Netherlands)
}
```

### Add Custom Properties to Objects

```python
# In Grasshopper, modify before saving
obj["properties"]["custom_field"] = "custom_value"
obj["properties"]["cost_estimate"] = 50000
```

### Export to Local GeoJSON (without AGOL)

```python
from agol_exporter import AGOLExporter
from pathlib import Path

exporter = AGOLExporter("dummy", "dummy")  # No AGOL needed
exporter.export_to_shapefile(gh_data, Path("exports/my_data"))
```

---

## ⚙️ ArcGIS Online Setup (Optional)

Only needed if uploading directly to AGOL:

```python
# 1. Get credentials
# https://www.arcgis.com → Sign in → Settings → Security

# 2. Set in pipeline
pipeline = RevitGISIntegrationPipeline(
    agol_username="your_username",
    agol_password="your_password"
)

# 3. Feature services auto-created in AGOL
```

---

## 🔍 Debugging

### View Pipeline Log
```python
report = pipeline.run_full_pipeline(revit_data)
print(report)  # Shows each step result
```

### Load Checkpoint
```python
from merge_engine import SyncEngine
from pathlib import Path

engine = SyncEngine()
engine.load_state(Path("data/checkpoints/sync_checkpoint_*.json"))

# Inspect objects
for obj in engine.list_objects():
    print(obj.id, obj.version, obj.timestamp)
```

### Check Metadata
```bash
# View sync history
cat "data/.sync/metadata.json" | python -m json.tool
```

---

## 📈 Next Steps

1. **Connect Revit Add-In**
   - Use Revit API to export element data
   - Call `step_1_revit_export()` with your data

2. **Create GH Script**
   - Load data with `GrassholperPipeline.load_and_analyze()`
   - Modify geometry
   - Save with `pipeline.save_and_export()`

3. **Automate AGOL Upload**
   - Add AGOL credentials
   - Pipeline uploads automatically
   - Check AGOL for new Feature Service

4. **Monitor & Maintain**
   - Check `data/reports/` for execution logs
   - Review metadata for version conflicts
   - Adjust conflict strategy if needed

---

## ❓ Troubleshooting

**Q: "No input files found"**
```
A: Run step_3_export_grasshopper() first to create gh_inputs/
```

**Q: AGOL authentication fails**
```
A: Check username/password at https://www.arcgis.com/sharing/rest
   Make sure account has API access
```

**Q: Coordinates don't match**
```
A: Verify epsg_code matches your Revit coordinate system
   Default is EPSG:32633 (UTM 33N)
```

**Q: "GH output file not found"**
```
A: Increase timeout or manually provide gh_output path
   wait_for_gh_input=Path("data/gh_outputs/my_file.json")
```

---

## 📞 Support Files

- **Full README**: See [README.md](../README.md)
- **API Docs**: See inline docstrings in `*.py` files
- **Examples**: Check `if __name__ == "__main__"` sections

---

**Ready to start? Run: `python integration_pipeline.py`**
