# 🦗 Grasshopper Cheatsheet - Copy-Paste Ready

## ⚡ 30-Second Setup

**Paste this in Grasshopper Python component:**

```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")
from gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
objects = helper.load_input_data()

print("✅ Loaded {} objects".format(len(objects)))

# Output
loaded_data = objects
```

**That's it!** ✅

---

## 📋 Common Operations

### **1️⃣ Load Data**
```python
from gh_helper import GrassholperDataHelper
helper = GrassholperDataHelper()
data = helper.load_input_data()
```

### **2️⃣ Scale All Geometries**
```python
for obj in data:
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    def scale(c, f):
        if isinstance(c[0], (list, tuple)):
            return [scale(s, f) for s in c]
        return [v * f for v in c]
    
    geom["coordinates"] = scale(coords, 1.5)
```

### **3️⃣ Filter by Type**
```python
walls_only = [o for o in data if o.get("type") == "Wall"]
```

### **4️⃣ Add Property**
```python
for obj in data:
    obj["properties"]["my_custom_field"] = "value"
    obj["version"] = obj.get("version", 1) + 1
```

### **5️⃣ Save Output**
```python
from gh_helper import GrassholperDataHelper
helper = GrassholperDataHelper()
helper.current_data = data
filepath = helper.save_output_data(data)
```

### **6️⃣ Export to AGOL**
```python
from agol_exporter import AGOLExporter
exporter = AGOLExporter("username", "password")
success, service_id = exporter.export_to_agol(data)
```

---

## 🎯 Ready-to-Use One-Liners

| Task | Code |
|------|------|
| Load latest | `GrassholperDataHelper().load_input_data()` |
| Count objects | `len(data)` |
| Get types | `[o.get("type") for o in data]` |
| Filter walls | `[o for o in data if o.get("type")=="Wall"]` |
| Get first object | `data[0]` |
| Get object by ID | `[o for o in data if o.get("id")=="wall_001"][0]` |
| Round coords | `[round(c, 2) for c in coords]` |
| Save data | `GrassholperDataHelper().save_output_data(data)` |
| Get summary | `GrassholperDataHelper().get_summary()` |
| Increment version | `obj["version"] = obj.get("version",1)+1` |

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| Import error | `sys.path.insert(0, r"C:\Users\...\scripts")` |
| No data | First run Revit export: `revit_gh_bridge.py` |
| Path wrong | Use raw string: `r"C:\..."` |
| Need IronPython? | Use Python 3 in GH 2.0+ instead |
| Output not showing? | Check `View → Python Console` |
| File not saving? | Check `data/` folder permissions |
| AGOL error? | Check username/password in AGOL |

---

## 📤 Input/Output Diagram

```
Input (from Revit)
    ↓
    └─→ gh_input_*.json
         ↓
    [Load in GH]
         ↓
    objects = [...]
         ↓
    [Modify in GH]
         ↓
    objects = [...(modified)...]
         ↓
    [Save in GH]
         ↓
    gh_output_*.json
         ↓
    [Export to AGOL]
         ↓
    AGOL Feature Service ✅
```

---

## 🎛️ Component Inputs/Outputs

### **Component 1: Load**
```
Input: None
Output: 
  • objects (list) ← Main data
  • count (int)
  • info (str)
```

### **Component 2: Process**
```
Input:
  • objects ← from Component 1
  • scale_factor (float)
Output:
  • processed (list)
  • preview (Rhino)
```

### **Component 3: Save**
```
Input:
  • objects ← from Component 2
  • agol_toggle (bool)
Output:
  • filepath (str)
  • agol_id (str)
  • success (bool)
```

---

## 🔗 Connect Like This

```
Load Comp     Process Comp     Save Comp
    │             │                │
    objects ──→ objects ──────────→ objects
                  │                 │
              preview ──────────┐   └→ filepath
                                │
                              [Panels]
                              
[Slider]─────────────────────→ Process Comp
[Toggle]─────────────────────→ Save Comp
```

---

## 📝 Complete Minimal Example

**Paste directly into Grasshopper Python:**

```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperDataHelper

# Load
helper = GrassholperDataHelper()
data = helper.load_input_data()

# Modify
for obj in data:
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    def scale(c, f):
        if isinstance(c[0], (list, tuple)):
            return [scale(s, f) for s in c]
        return [v * f for v in c]
    
    geom["coordinates"] = scale(coords, 1.5)
    obj["version"] = obj.get("version", 1) + 1

# Save
helper.current_data = data
filepath = helper.save_output_data(data)

# Outputs
output_objects = data
output_path = str(filepath)
output_count = len(data)
```

---

## 🎨 Visual Map (Ctrl+C ready!)

```
START HERE:
Revit Model
    ↓ (export)
gh_input_*.json
    ↓ (load)
[Load Component] ← Paste Template 1
    ↓
objects
    ↓ (modify)
[Process Component] ← Paste Template 2
    ↓
modified_objects
    ↓ (save)
[Save Component] ← Paste Template 5/6
    ↓
gh_output_*.json  ✅
AGOL Service      ✅
```

---

## ⚙️ Configuration

```python
# Default paths (auto-detected)
from gh_helper import GrassholperDataHelper
helper = GrassholperDataHelper()

# Custom data directory
from pathlib import Path
helper = GrassholperDataHelper(Path("C:/custom/path"))

# Load specific file
data = helper.load_input_data("specific_file.json")

# Change AGOL endpoint
from agol_exporter import AGOLAuthentication
auth = AGOLAuthentication(
    username="user",
    password="pass",
    portal_url="https://custom.arcgisonline.com/sharing/rest"
)
```

---

## 🆘 Error Messages Explained

| Error | Means | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: gh_helper` | Path wrong | Add sys.path correctly |
| `FileNotFoundError: gh_input` | No Revit export | Run Revit export first |
| `KeyError: 'geometry'` | Object malformed | Check data structure |
| `Permission denied` | Can't write file | Check folder permissions |
| `ConnectionError` | AGOL unreachable | Check internet/credentials |

---

## 📊 Data Structure

```json
{
  "id": "wall_001",
  "type": "Wall",
  "version": 2,
  "timestamp": "2026-01-08T10:30:00",
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
```

---

## 🚀 Power User Tips

1. **Batch process:** Loop through all objects
2. **Conditional logic:** `if obj.get("type") == "Wall": ...`
3. **Custom properties:** `obj["properties"]["custom"] = value`
4. **Version tracking:** Always `obj["version"] += 1`
5. **Error handling:** Use `try/except` blocks
6. **Debugging:** Add `print()` statements
7. **Testing:** Test each component separately
8. **Performance:** Cache large lists
9. **Organization:** Comment your modifications
10. **Documentation:** Note changes in properties

---

## 🎓 Learning Resources

| Resource | Location |
|----------|----------|
| Full guide | [GRASSHOPPER_GUIDE.md](GRASSHOPPER_GUIDE.md) |
| 10 Templates | [GH_TEMPLATES.py](GH_TEMPLATES.py) |
| Setup steps | [GH_SETUP_ILLUSTRATED.md](GH_SETUP_ILLUSTRATED.md) |
| Data flow | [GH_WORKFLOW.md](GH_WORKFLOW.md) |
| API docs | [README.md](README.md) |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |

---

## ✅ Checklist: Works When You See ✅

- ✅ Python console shows "✅ Loaded X objects"
- ✅ Output panel shows geometry list
- ✅ File saved in `data/gh_outputs/`
- ✅ Object versions incremented
- ✅ No error messages in console
- ✅ AGOL (optional) shows Feature Service created

---

## 🎯 From Start to Finish (5 minutes)

```
1. Open Grasshopper (1 min)
2. Create Python component (1 min)
3. Paste Template 1 code (1 min)
4. Change path to your system (1 min)
5. Click "Run" (1 min)
6. See ✅ in console = SUCCESS! 🎉
```

---

**Need more? See [INDEX.md](INDEX.md) for full docs**

Created: January 8, 2026
Status: Ready to use ✅
