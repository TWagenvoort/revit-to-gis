# Grasshopper Step-by-Step Setup (Illustrated)

## 🦗 Setup in 10 Minutes

### **Step 1️⃣: Open Grasshopper**

```
Revit → Manage → Grasshopper
         (Opens Grasshopper window)
```

### **Step 2️⃣: Create Python Component**

```
Grasshopper Canvas
    │
    ├─ Double-click to place component
    │
    └─ Search for: "Python"
            │
            └─ Click "Python" (or "IronPython" for older GH)
                   │
                   └─ Component appears on canvas
```

**Result:**
```
┌─────────────────────────────────┐
│  Python                         │
├─────────────────────────────────┤
│  x (No input)                   │
├─────────────────────────────────┤
│ out (Output)                    │
└─────────────────────────────────┘
```

---

### **Step 3️⃣: Open Script Editor**

```
Right-click on Python component
    │
    └─ Select "Edit Script"
        │
        └─ Python editor opens
```

You should see:
```python
"""Grasshopper Python Component"""
ghenv = gh_doc = ghdoc = None
ghenv.Component = None

import Rhino

def main():
    pass

if __name__ == "__main__":
    main()
```

---

### **Step 4️⃣: Add Module Path**

**Choose ONE option:**

**Option A: GitHub (Recommended)**
```python
"""Grasshopper Python Component - Load Revit Data"""

from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

try:
    helper = GrassholperDataHelper()
    objects = helper.load_input_data()
    count = len(objects) if objects else 0
    
    print("✅ Loaded {} objects".format(count))
    
except Exception as e:
    print("❌ Error: {}".format(e))
    objects = None
    count = 0
```

**Option B: Local Path**
```python
"""Grasshopper Python Component - Load Revit Data"""

import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperDataHelper

try:
    helper = GrassholperDataHelper()
    objects = helper.load_input_data()
    count = len(objects) if objects else 0
    
    print("✅ Loaded {} objects".format(count))
    
except Exception as e:
    print("❌ Error: {}".format(e))
    objects = None
    count = 0
```

> **Option A**: First do `pip install git+https://github.com/TWagenvoort/revit-to-gis.git`
> **Option B**: Use if repo cloned locally

---

### **Step 5️⃣: Set Output Port**

```
In the Python component:
1. Look at right side panel
2. Find "out" parameter
3. Click to expand outputs

Result:
   out (Object)  ← Single output
```

**Add multiple outputs:**
```
Right-click on "out"
    │
    └─ Add output (Type: Generic)
       │
       └─ Repeat 2-3x for multiple outputs
```

Rename outputs:
```
Right-click on output name
    │
    └─ Rename to: objects
    └─ Rename to: count  
    └─ Rename to: summary
```

---

### **Step 6️⃣: Connect Outputs**

```
Python Component
    │
    ├─ objects ──→ [Panel] (display)
    ├─ count ────→ [Number Slider]
    └─ summary ──→ [Panel] (display)
```

**How to connect:**
1. Click on output port (small circle on right)
2. Drag to input of next component
3. Release to connect

---

### **Step 7️⃣: Run & Test**

```
Canvas
    │
    ├─ Press F5 (Run solution)
    │
    └─ Component executes
        │
        ├─ Check Python console (bottom)
        │  Should see "✅ Loaded X objects"
        │
        └─ Check output panels
           Should show data
```

---

## 📋 Complete 3-Component Setup

### **Component Layout**

```
CANVAS LAYOUT:

┌──────────────────────────────────────────────────────┐
│ Grasshopper Window                                   │
│                                                      │
│  [INPUTS]        [PROCESS]          [OUTPUTS]       │
│                                                      │
│                ┌─────────────┐                      │
│                │ Load        │                      │
│                │ Python 1    │                      │
│                │ load_input()│      objects         │
│                └──────┬──────┘         │            │
│                       │              count          │
│                       │              summary        │
│                       │                             │
│                   OUTPUTS                           │
│                       │                             │
│                  [Panel1]  ← objects list           │
│                  [Panel2]  ← count number           │
│                  [Panel3]  ← summary JSON           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

### **Component 1: Load Input**

**Script:**
```python
# GitHub method (recommended)
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
objects = helper.load_input_data()
count = len(objects) if objects else 0
```

Or local path:
```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")
from gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
objects = helper.load_input_data()
count = len(objects) if objects else 0
```

**Outputs:**
- `objects` → List of geometry
- `count` → Integer
- `info` → String message

---

### **Component 2: Modify Geometry**

**Inputs:**
- `objects` ← From Component 1
- `scale_factor` ← Slider (0.5 to 2.0)

**Script:**
```python
# GitHub method
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

scale = scale_factor if 'scale_factor' in dir() else 1.0

for obj in objects:
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    def scale_coords(c, f):
        if isinstance(c[0], (list, tuple)):
            return [scale_coords(sub, f) for sub in c]
        return [val * f for val in c]
    
    geom["coordinates"] = scale_coords(coords, scale)
    obj["version"] = obj.get("version", 1) + 1

modified_objects = objects
```

Or local path:
```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

scale = scale_factor if 'scale_factor' in dir() else 1.0

for obj in objects:
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    def scale_coords(c, f):
        if isinstance(c[0], (list, tuple)):
            return [scale_coords(sub, f) for sub in c]
        return [val * f for val in c]
    
    geom["coordinates"] = scale_coords(coords, scale)
    obj["version"] = obj.get("version", 1) + 1

modified_objects = objects
```

**Outputs:**
- `modified_objects` → Processed geometry

---

### **Component 3: Save & Export**

**Inputs:**
- `objects` ← From Component 2
- `export_agol` ← Toggle

**Script:**
```python
# GitHub method
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
helper.current_data = objects

# Save to file
filepath = helper.save_output_data(objects)
output_file = str(filepath)

print("✅ Saved to {}".format(output_file))
```

Or local path:
```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
helper.current_data = objects

# Save to file
filepath = helper.save_output_data(objects)
output_file = str(filepath)

print("✅ Saved to {}".format(output_file))
```

**Outputs:**
- `output_file` → File path string
- `success` → True/False

---

## 🎨 Visual Setup on Canvas

```
Step 1: Place components
═══════════════════════════════

    [Empty Canvas]
         │ Double-click to place "Python"
         ↓
    [Py1] [Py2] [Py3]


Step 2: Connect them
═══════════════════════════════

    [Load Py] ──→ [Process Py] ──→ [Save Py]
         │            │                │
         └─→ [Panel]   │                └─→ [Panel]
                       └─→ [Panel]


Step 3: Add inputs (sliders, toggles, etc)
═══════════════════════════════════════════

    [Reload]─┐
             ├→ [Load Py]  ──→ [Process Py] ──→ [Save Py]
             │   │              │
    [Scale]─┤→ ─┘              │
             │                  │
    [AgolOn]┴────────────────→ [Save Py]
                              │
                    ┌─────────┴─────────┬────────────┐
                    ↓                   ↓            ↓
                [File Path]      [AGOL ID]    [Success?]
```

---

## 🔧 Debugging Checklist

### ❓ "ModuleNotFoundError: No module named 'gh_helper'"

**Solution:**
```
1. Check path: C:\Users\Thijs W\Desktop\Revit to GIS\scripts
2. Verify gh_helper.py exists in that folder
3. Copy full path and paste in sys.path.insert()
4. Use raw string: r"C:\..."
```

### ❓ "No input files found"

**Solution:**
```
1. Run Revit export FIRST
   → Creates data/gh_inputs/gh_input_*.json
2. Check: data/ folder exists
3. Check: gh_input_*.json file exists
4. Reload component (F5)
```

### ❓ "Permission denied" on save

**Solution:**
```
1. Check data/ folder permissions
2. Verify write access to folder
3. Close any open JSON files
4. Try saving to different location
```

### ❓ Nothing happens when I run

**Solution:**
```
1. Check Python console (View → Python Console)
2. Look for error messages
3. Add print() statements:
   print("Started")
   print("Loaded: {}".format(objects))
4. Check that paths are correct
```

---

## 📊 Test Your Setup

### **Test 1: Load**
```python
# Copy into Python component
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")
from gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
data = helper.load_input_data()
test_result = "✅ Loaded {} objects".format(len(data))
```

**Expected Output:** `✅ Loaded X objects` (X > 0)

### **Test 2: Modify**
```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

# Test scaling
for obj in objects:
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    # Just checking structure
    test_result = "✅ {} has {} coordinates".format(
        obj.get("id"),
        len(coords) if coords else 0
    )
```

**Expected Output:** `✅ [object_id] has X coordinates`

### **Test 3: Save**
```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")
from gh_helper import GrassholperDataHelper
from pathlib import Path

helper = GrassholperDataHelper()
helper.current_data = objects

# Check if data folder exists
data_dir = Path(r"C:\Users\Thijs W\Desktop\Revit to GIS\data")
test_result = "✅ Data dir exists: {}".format(data_dir.exists())
```

**Expected Output:** `✅ Data dir exists: True`

---

## ✅ Final Checklist

- [ ] Grasshopper is open
- [ ] Created 3 Python components
- [ ] Added `sys.path` to each
- [ ] Imported `gh_helper` successfully
- [ ] Component 1 runs without errors
- [ ] Component 2 connects to Component 1
- [ ] Component 3 connects to Component 2
- [ ] Outputs show correct data
- [ ] Files save to `data/gh_outputs/`
- [ ] No error messages in console

---

## 🎉 You're Ready!

Now you can:
1. ✅ Load Revit data in GH
2. ✅ Modify geometry
3. ✅ Save for ArcGIS Online
4. ✅ Full bidirectional sync

**Next:** Export to ArcGIS Online using AGOL credentials!

---

## 📚 Additional Resources

- **GitHub Setup:** [GITHUB_SETUP.md](GITHUB_SETUP.md) ← Start here for GitHub install
- **Full Guide:** [GRASSHOPPER_GUIDE.md](GRASSHOPPER_GUIDE.md)
- **Templates:** [GH_TEMPLATES.py](GH_TEMPLATES.py)
- **Workflow:** [GH_WORKFLOW.md](GH_WORKFLOW.md)
- **Code Examples:** [scripts/gh_helper.py](scripts/gh_helper.py)
- **Repository:** https://github.com/TWagenvoort/revit-to-gis
