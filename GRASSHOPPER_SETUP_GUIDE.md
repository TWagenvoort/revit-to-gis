# 🦗 Grasshopper Setup Guide - Stap voor Stap

## ⚡ Ultra Quick (5 minuten)

**Volg deze 5 stappen:**

### **Stap 1: Open Grasshopper in Revit**
```
Revit → Manage → Grasshopper
```

### **Stap 2: Create Python Component**
- Double-click op canvas
- Search "Python"
- Click en plaats op canvas

### **Stap 3: Edit Script**
- Right-click component → "Edit Script"
- Delete all template code

### **Stap 4: Paste this code**

```python
import urllib.request

# Load from GitHub
url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

# Create helper
gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()

# Load data from Revit
objects = helper.load_input_data()
count = len(objects) if objects else 0

print("Loaded {} objects from Revit".format(count))
```

### **Stap 5: Add Outputs**
- Right-click component → "Manage output"
- Rename "out" to "objects"
- Add new output → "count"
- Press F5

**Done!** You should see: `Loaded X objects`

---

## 📖 Volledige Setup (15 minuten)

### **Deel 1: Voorbereiding**

#### Option A: GitHub Direct (Recommended - No installation)
- ✓ Works anywhere
- ✓ No setup
- ✓ Always latest

#### Option B: pip install (Fast - 30 seconds)
```bash
pip install git+https://github.com/TWagenvoort/revit-to-gis.git
```

#### Option C: Local (For development)
1. Clone: `git clone https://github.com/TWagenvoort/revit-to-gis.git`
2. Adjust paths in code

---

### **Deel 2: Create Pipeline Components**

#### **Component 1: Load Data**

```python
"""Component 1: Load Revit Data"""
import urllib.request

url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()

try:
    objects = helper.load_input_data()
    count = len(objects) if objects else 0
    status = "Loaded {} objects".format(count)
    print("[OK] " + status)
except Exception as e:
    objects = None
    count = 0
    status = "Error: {}".format(e)
    print("[ERROR] " + status)
```

**Outputs:**
- `objects` (list)
- `count` (int)
- `status` (string)

**Right-click → Manage output:**
```
+ Click to add output
Name: objects
Name: count  
Name: status
```

---

#### **Component 2: Modify Geometry**

**Inputs:**
- `objects` (from Component 1)
- `scale_factor` (slider: 0.5 to 2.0)
- `new_version` (toggle)

```python
"""Component 2: Modify Geometry"""

# Receive: objects, scale_factor, new_version

scale = scale_factor if 'scale_factor' in dir() else 1.0
bump_version = new_version if 'new_version' in dir() else False

modified_count = 0

for obj in objects:
    # Scale geometry
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    if coords:
        def scale_coords(c, f):
            if isinstance(c[0], (list, tuple)):
                return [scale_coords(sub, f) for sub in c]
            return [val * f for val in c]
        
        geom["coordinates"] = scale_coords(coords, scale)
        modified_count += 1
    
    # Bump version
    if bump_version:
        obj["version"] = obj.get("version", 1) + 1
        obj["timestamp"] = str(__import__('datetime').datetime.now().isoformat())

modified_objects = objects
info = "Modified: {}, Scale: {}, Version bump: {}".format(
    modified_count, scale, bump_version
)

print("[OK] " + info)
```

**Inputs (right-click):**
```
Inputs:
- objects (from Component 1)
- scale_factor (Number Slider, default 1.0)
- new_version (Toggle)
```

**Outputs:**
```
- modified_objects
- info
```

---

#### **Component 3: Validate & Merge**

**Inputs:**
- `objects` (from Component 2)
- `strategy` (text: "last_write_wins" or "manual")

```python
"""Component 3: Validate & Merge"""
import urllib.request

url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

merge_engine = load_github_module_simple('merge_engine')

# Create sync engine
sync = merge_engine.SyncEngine()

# Validate data
validated = []
errors = []

for obj in objects:
    try:
        # Check required fields
        if not obj.get("id"):
            errors.append("Missing ID in {}".format(obj))
            continue
        if not obj.get("geometry"):
            errors.append("Missing geometry in {}".format(obj.get("id")))
            continue
        
        validated.append(obj)
    except Exception as e:
        errors.append(str(e))

valid_count = len(validated)
error_count = len(errors)

status = "Valid: {}, Errors: {}".format(valid_count, error_count)
print("[OK] " + status)
```

**Outputs:**
```
- validated_objects
- error_count
- status
```

---

#### **Component 4: Save to File**

**Inputs:**
- `objects` (from Component 3)
- `auto_save` (toggle)

```python
"""Component 4: Save to File"""
import urllib.request

url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()

if auto_save or 'auto_save' not in dir():
    try:
        filepath = helper.save_output_data(objects)
        output_file = str(filepath)
        status = "Saved to: {}".format(output_file)
        print("[OK] " + status)
    except Exception as e:
        output_file = None
        status = "Error: {}".format(e)
        print("[ERROR] " + status)
else:
    output_file = None
    status = "Auto-save disabled"

save_count = len(objects)
```

**Outputs:**
```
- output_file
- save_count
- status
```

---

#### **Component 5: Export to ArcGIS Online**

**Inputs:**
- `objects` (from Component 4)
- `export_enabled` (toggle)
- `agol_username` (text)
- `agol_password` (text)

```python
"""Component 5: Export to ArcGIS Online"""
import urllib.request

url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

agol = load_github_module_simple('agol_exporter')

# Convert to GeoJSON
converter = agol.GeoJSONConverter(epsg=32633)  # UTM 33N for Netherlands

try:
    geojson = converter.gh_to_geojson(objects)
    feature_count = len(geojson.get("features", []))
    
    if export_enabled and 'agol_username' in dir() and agol_username:
        # Export to AGOL
        exporter = agol.AGOLExporter()
        result = exporter.export_to_agol(
            objects,
            agol_username,
            agol_password
        )
        status = "Exported {} features to ArcGIS Online".format(feature_count)
        print("[OK] " + status)
    else:
        status = "GeoJSON ready: {} features (export disabled)".format(feature_count)
        print("[OK] " + status)
    
    export_status = "OK"
    
except Exception as e:
    feature_count = 0
    status = "Error: {}".format(e)
    export_status = "FAILED"
    print("[ERROR] " + status)

geojson_ready = True
```

**Outputs:**
```
- feature_count
- status
- export_status
- geojson_ready
```

---

## 🎨 Canvas Setup Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ Grasshopper Canvas                                              │
│                                                                 │
│ [Load Data] ──→ [Modify] ──→ [Validate] ──→ [Save] ──→ [Export]│
│     │              │             │            │           │    │
│     ├─ objects     ├─ modified   ├─ valid    ├─ file     ├─ ok │
│     ├─ count       └─ info       └─ errors   └─ count    └─ status
│     └─ status                                                  │
│                                                                 │
│ [Slider] ──→ [Modify]                                          │
│ scale_factor                                                    │
│                                                                 │
│ [Toggle] ──→ [Modify]                                          │
│ bump_version                                                    │
│                                                                 │
│ [Text] ──→ [Export]                                            │
│ agol_username                                                   │
│ agol_password                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Step-by-Step Checklist

- [ ] Grasshopper is open
- [ ] Created Python component 1 (Load Data)
- [ ] Pasted code in component 1
- [ ] Added outputs: objects, count, status
- [ ] Pressed F5
- [ ] See "Loaded X objects" in console
- [ ] Created component 2 (Modify)
- [ ] Connected: objects → Component 2
- [ ] Added slider for scale_factor
- [ ] Created component 3 (Validate)
- [ ] Connected Component 2 → Component 3
- [ ] Created component 4 (Save)
- [ ] Connected Component 3 → Component 4
- [ ] Created component 5 (Export)
- [ ] Connected Component 4 → Component 5
- [ ] Toggle export_enabled
- [ ] All components run without errors
- [ ] Files save to data/gh_outputs/

---

## 🆘 Troubleshooting

### "ModuleNotFoundError"
```python
# Check internet connection
# Check GitHub is accessible
# Try restarting Grasshopper
```

### "No input files found"
```python
# Run Revit export FIRST
# Check data/gh_inputs/ folder exists
# Check gh_input_*.json files exist
```

### "Permission denied"
```python
# Check data/ folder permissions
# Run as Administrator
# Check files aren't open in other programs
```

### "Slow loading from GitHub"
```python
# This is normal (first run)
# Subsequent runs may be faster
# Consider pip install for production use
```

---

## 📊 Expected Output

**Console after running:**
```
[OK] Loaded 15 objects from Revit
[OK] Modified: 15, Scale: 1.5, Version bump: True
[OK] Valid: 15, Errors: 0
[OK] Saved to: C:\Users\...\data\gh_outputs\gh_output_20260108_120000.json
[OK] GeoJSON ready: 15 features (export disabled)
```

---

## 🌐 Data Flow

```
Revit
  ↓ (export)
  ↓
data/gh_inputs/gh_input_*.json
  ↓ (Component 1: load)
  ↓
Grasshopper (objects in memory)
  ↓ (Component 2: modify)
  ↓
Modified objects (in memory)
  ↓ (Component 3: validate)
  ↓
Valid objects (in memory)
  ↓ (Component 4: save)
  ↓
data/gh_outputs/gh_output_*.json
  ↓ (Component 5: export)
  ↓
ArcGIS Online Feature Service
```

---

## 💡 Pro Tips

**Tip 1: Save Canvas**
```
File → Save As → revit-gis-pipeline.gh
```

**Tip 2: Use Panels for Display**
```
Right-click output → Draw → Panel
Shows live data as it processes
```

**Tip 3: Use Number Sliders**
```
Connect slider to component input
Test different scale values
```

**Tip 4: Enable Debug Output**
```python
# Add in any component
print("[DEBUG] Variable value: {}".format(variable))
# Check Python Console: View → Python Console
```

---

## 📚 More Information

- **Quick Start**: GITHUB_QUICKSTART.md
- **API Docs**: README.md
- **Templates**: GH_TEMPLATES_GITHUB.md
- **Architecture**: ARCHITECTURE.md

---

## 🎉 You're Ready!

You now have a **complete bidirectional sync pipeline**:
- ✓ Load from Revit
- ✓ Modify in Grasshopper
- ✓ Validate & version
- ✓ Save locally
- ✓ Export to ArcGIS Online

**All from GitHub - no installation needed!**

---

**Questions? Check the docs or create an issue on GitHub:**
https://github.com/TWagenvoort/revit-to-gis/issues
