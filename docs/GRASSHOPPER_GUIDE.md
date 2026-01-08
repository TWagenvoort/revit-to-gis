# Grasshopper Integration Guide

## 🦗 3 Ways to Use in Grasshopper

### **Option 1: IronPython Component (Easiest)**
### **Option 2: Python 3 Component (Recommended)**  
### **Option 3: External Python Script**

---

## ⭐ OPTION 1: IronPython (Quick Start)

### **For Grasshopper with IronPython**

#### **Step 1: Open Grasshopper Python Component**
1. Open Grasshopper
2. Search for "Python" component
3. Double-click to edit

#### **Step 2: Add Import Path**

```python
# At top of script
import sys
sys.path.append(r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

# Now import our modules
from gh_helper import GrassholperPipeline, GrassholperDataHelper
```

#### **Step 3: Load Input Data from Revit**

```python
from gh_helper import GrassholperPipeline
from pathlib import Path

# Initialize
pipeline = GrassholperPipeline()

# Load data exported from Revit
data = pipeline.load_and_analyze()

# Get summary
summary = pipeline.helper.get_summary()
print("Loaded: {} objects".format(summary['total_objects']))

# Output to Grasshopper
output_data = data
```

#### **Step 4: Modify Geometry in Grasshopper**

```python
from gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
data = helper.load_input_data()

# Example: Scale all coordinates by 1.5x
for obj in data:
    geometry = obj.get("geometry", {})
    coords = geometry.get("coordinates", [])
    
    # Scale function
    def scale_coords(coords, factor):
        if isinstance(coords[0], (list, tuple)):
            return [scale_coords(c, factor) for c in coords]
        return [val * factor for val in coords]
    
    geometry["coordinates"] = scale_coords(coords, 1.5)
    obj["version"] = obj.get("version", 1) + 1

output_data = data
```

#### **Step 5: Save Modified Data**

```python
from gh_helper import GrassholperDataHelper
from pathlib import Path

helper = GrassholperDataHelper()
helper.current_data = input_data  # from previous component

# Save for ArcGIS export
filepath = helper.save_output_data(input_data)
print("Saved to: {}".format(filepath))
```

---

## ✨ OPTION 2: Python 3 Component (Recommended)

### **For Grasshopper 2.0+ with Native Python 3**

#### **Step 1: Install GH Python Plugin**
1. Open Grasshopper
2. Help → Install Python
3. Select Python 3.10+

#### **Step 2: Create Python Component**
1. Search for "Python" (the new native one)
2. Double-click to edit code

#### **Step 3: Setup Module Path**

```python
import sys
from pathlib import Path

# Add scripts path
scripts_path = r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts"
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Now import modules
from gh_helper import GrassholperPipeline
from merge_engine import SyncEngine
from agol_exporter import AGOLExporter
```

#### **Step 4: Complete GH Component Example**

```python
import sys
from pathlib import Path
import json

# Setup path
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperDataHelper, GrassholperPipeline

def load_revit_export():
    """Load data from Revit export"""
    pipeline = GrassholperPipeline()
    data = pipeline.load_and_analyze()
    return data

def modify_geometry(data):
    """Example: Round all coordinates to 2 decimals"""
    for obj in data:
        geom = obj.get("geometry", {})
        coords = geom.get("coordinates", [])
        
        def round_coords(coords, decimals=2):
            if isinstance(coords[0], (list, tuple)):
                return [round_coords(c, decimals) for c in coords]
            return [round(val, decimals) for val in coords]
        
        geom["coordinates"] = round_coords(coords)
        obj["timestamp"] = "2026-01-08"
    
    return data

def save_for_export(data):
    """Save modified data"""
    helper = GrassholperDataHelper()
    helper.current_data = data
    filepath = helper.save_output_data(data)
    return str(filepath)

# Main execution
if __name__ == "__main__":
    # Step 1: Load
    loaded_data = load_revit_export()
    
    # Step 2: Modify
    modified_data = modify_geometry(loaded_data)
    
    # Step 3: Save
    output_file = save_for_export(modified_data)
    
    # Outputs for Grasshopper
    objects_count = len(modified_data)
    output_path = output_file
    modified_objects = modified_data
```

---

## 🔧 OPTION 3: External Python Script (Advanced)

### **Run from Command Line / Schedule**

#### **Step 1: Create Standalone Script**

```python
# File: C:\Users\Thijs W\Desktop\Revit to GIS\scripts\run_grasshopper_pipeline.py

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from gh_helper import GrassholperPipeline
from integration_pipeline import RevitGISIntegrationPipeline

def run_complete_pipeline():
    """Execute: Load Revit → Process → Export to AGOL"""
    
    print("=" * 60)
    print("GRASSHOPPER PIPELINE")
    print("=" * 60)
    
    # Initialize
    gh_pipeline = GrassholperPipeline()
    
    # Step 1: Load & analyze
    print("\n1️⃣  Loading Revit data...")
    analysis = gh_pipeline.load_and_analyze()
    
    if analysis.get("loaded_objects", 0) == 0:
        print("❌ No data found!")
        return
    
    # Step 2: Process
    print("\n2️⃣  Processing geometry...")
    processed = gh_pipeline.process_example()
    
    # Step 3: Save
    print("\n3️⃣  Saving for AGOL...")
    output_file = gh_pipeline.save_and_export()
    
    print("\n✅ Complete!")
    print(f"Output: {output_file}")
    
    return output_file

if __name__ == "__main__":
    run_complete_pipeline()
```

#### **Step 2: Call from Grasshopper Shell Component**

```python
import subprocess
import sys

# Run Python script
result = subprocess.run([
    sys.executable,
    r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts\run_grasshopper_pipeline.py"
], capture_output=True, text=True)

output = result.stdout
errors = result.stderr

print(output)
if errors:
    print("ERRORS:", errors)
```

---

## 🎯 Complete Grasshopper Workflow Example

### **All-in-One GH Component**

```python
"""
Complete Revit → GH → AGOL Pipeline in Grasshopper
Copy-paste into Python component
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# ============ SETUP ============
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

try:
    from gh_helper import GrassholperDataHelper, GrassholperPipeline
    from merge_engine import SyncEngine
except ImportError as e:
    print("ERROR: Could not import modules. Check path.")
    print(str(e))
    exit()

# ============ MAIN FUNCTIONS ============

def load_input():
    """Load data from Revit"""
    helper = GrassholperDataHelper()
    data = helper.load_input_data()
    return data

def process_geometry(data):
    """
    Process geometry
    Modify this function for your specific needs
    """
    
    for obj in data:
        # Example 1: Round coordinates
        geom = obj.get("geometry", {})
        coords = geom.get("coordinates", [])
        
        def round_coords(coords, decimals=2):
            if isinstance(coords[0], (list, tuple)):
                return [round_coords(c, decimals) for c in coords]
            return [round(val, decimals) for val in coords]
        
        geom["coordinates"] = round_coords(coords)
        
        # Example 2: Add/modify properties
        props = obj.get("properties", {})
        props["processed_date"] = datetime.now().isoformat()
        props["processed_in"] = "Grasshopper"
        
        # Example 3: Update version
        obj["version"] = obj.get("version", 1) + 1
    
    return data

def sync_with_engine(data):
    """Update sync engine with changes"""
    engine = SyncEngine()
    engine.import_from_grasshopper(data)
    return engine

def save_output(data):
    """Save for ArcGIS Online"""
    helper = GrassholperDataHelper()
    helper.current_data = data
    filepath = helper.save_output_data(data)
    return filepath

def generate_report(data):
    """Generate processing report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "objects_processed": len(data),
        "types": {},
        "properties_sample": data[0].get("properties", {}) if data else {}
    }
    
    for obj in data:
        obj_type = obj.get("type", "Unknown")
        report["types"][obj_type] = report["types"].get(obj_type, 0) + 1
    
    return report

# ============ EXECUTION ============

def main():
    print("🦗 Grasshopper Pipeline Started")
    
    # Load
    input_data = load_input()
    if not input_data:
        print("❌ No input data")
        return None, None, None
    
    print(f"✅ Loaded {len(input_data)} objects")
    
    # Process
    processed = process_geometry(input_data)
    print(f"✅ Processed {len(processed)} objects")
    
    # Sync
    engine = sync_with_engine(processed)
    print("✅ Updated sync engine")
    
    # Save
    output_file = save_output(processed)
    print(f"✅ Saved to {output_file}")
    
    # Report
    report = generate_report(processed)
    print(f"✅ Report: {report['objects_processed']} objects")
    
    return processed, str(output_file), report

# ============ OUTPUT ============

try:
    objects, filepath, report = main()
    output_objects = objects
    output_path = filepath
    output_report = json.dumps(report, indent=2)
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    output_objects = None
    output_path = None
    output_report = str(e)
```

---

## 📊 GH Component Inputs/Outputs

### **Recommended Inputs**
```
input_operation : (string) "load" / "process" / "save"
modify_factor : (number) Scale/modify factor
custom_properties : (dict) Additional properties to add
```

### **Recommended Outputs**
```
objects : (list) Processed geometry objects
filepath : (string) Output file path
summary : (dict) Processing summary
report : (string) JSON report
status : (string) "success" / "error"
```

---

## 🎛️ Grasshopper Component Setup

### **Step 1: Set Inputs**

```
Input 1: Toggle - Reload Data
Input 2: Slider - Scale Factor (0.5 to 2.0)
Input 3: Toggle - Include Properties
Input 4: Text - Custom ID Prefix
```

### **Step 2: Add Visualization**

```python
# Visualize geometry in GH
from Rhino.Geometry import Point3d, Curve

visualize_points = []

for obj in objects:
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    if coords:
        if isinstance(coords[0], (list, tuple)):
            # LineString/Polygon
            points = [Point3d(c[0], c[1], c[2] if len(c) > 2 else 0) for c in coords[0]]
        else:
            # Point
            points = [Point3d(coords[0], coords[1], coords[2] if len(coords) > 2 else 0)]
        
        visualize_points.extend(points)

# Output to GH canvas
A = visualize_points
```

### **Step 3: Connect Downstream**

```
GH Component Output → File Export (Shapefile/GeoJSON)
                   → Vector Display
                   → Data Table
                   → AGOL Upload (next step)
```

---

## 🚀 Full Workflow in Grasshopper

### **Panel 1: Load Revit Data**
```
[Load Revit Button] → Python Component → Output: objects_list
```

### **Panel 2: Process/Modify**
```
objects_list → Python Component (modify_geometry) → modified_objects
```

### **Panel 3: Visualize**
```
modified_objects → Geometry Preview
               → Data Table (properties)
               → Statistics
```

### **Panel 4: Save & Export**
```
modified_objects → Python Component (save_output) → output_file
              → Python Component (export_to_agol) → agol_service_id
```

---

## 📝 Common GH Modifications

### **Modification 1: Scale All Geometries**

```python
from gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
data = helper.load_input_data()

scale_factor = 2.0  # Input from GH

for obj in data:
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    def scale_coords(c, factor):
        if isinstance(c[0], (list, tuple)):
            return [scale_coords(sub, factor) for sub in c]
        return [val * factor for val in c]
    
    geom["coordinates"] = scale_coords(coords, scale_factor)

output_data = data
```

### **Modification 2: Filter by Type**

```python
data = input_objects  # from previous component

# Keep only walls
filtered = [obj for obj in data if obj.get("type") == "Wall"]

output_data = filtered
```

### **Modification 3: Add Custom Properties**

```python
data = input_objects

for obj in data:
    obj["properties"]["custom_id"] = "GH_2026"
    obj["properties"]["modified_in_gh"] = True
    obj["properties"]["gh_date"] = "2026-01-08"

output_data = data
```

### **Modification 4: Transform Coordinates (Rotate)**

```python
import math

data = input_objects
angle_degrees = 45  # Input from GH

angle_radians = math.radians(angle_degrees)
cos_a = math.cos(angle_radians)
sin_a = math.sin(angle_radians)

def rotate_point(x, y, angle_rad):
    x_new = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    y_new = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    return [x_new, y_new]

for obj in data:
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    def rotate_coords(c):
        if isinstance(c[0], (list, tuple)):
            return [rotate_coords(sub) for sub in c]
        return rotate_point(c[0], c[1], angle_radians) + c[2:]
    
    geom["coordinates"] = rotate_coords(coords)

output_data = data
```

---

## 🔗 Integration with ArcGIS Online (Final Step)

### **From Grasshopper → AGOL**

```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from agol_exporter import AGOLExporter
from pathlib import Path

# Your modified data from GH
gh_data = input_objects  # from previous component

# Initialize exporter
exporter = AGOLExporter(
    agol_username="your_agol_username",
    agol_password="your_agol_password"
)

# Export to AGOL
success, result = exporter.export_to_agol(
    gh_data,
    service_title="My Building - GH Modified",
    service_description="Modified in Grasshopper"
)

if success:
    print("✅ Success! AGOL Service ID: {}".format(result))
    agol_service_id = result
else:
    print("❌ Error: {}".format(result))
    agol_service_id = None

output_success = success
output_service_id = agol_service_id
output_message = result
```

---

## 📦 Summary: 3 Approaches

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **IronPython** | Simple, integrated | Limited Python 3 | Quick scripts |
| **Python 3** | Modern, powerful | Needs GH 2.0+ | Production use |
| **External Script** | Full control, flexible | Complex setup | Automation |

---

## ⚡ Quick Copy-Paste Template

```python
# IronPython / Python 3 in Grasshopper
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperDataHelper

# LOAD
helper = GrassholperDataHelper()
data = helper.load_input_data()

# MODIFY (your custom code here)
for obj in data:
    obj["properties"]["processed"] = True
    obj["version"] = obj.get("version", 1) + 1

# SAVE
output_file = helper.save_output_data(data)

# OUTPUTS
output_objects = data
output_path = str(output_file)
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError" | Check path in `sys.path.append()` |
| "No input files found" | Run Revit export first |
| "Permission denied" | Check file permissions in data/ |
| IronPython won't import | Use Python 3 in GH 2.0+ |

---

**Ready? Copy a template above and paste into Grasshopper Python component!**
