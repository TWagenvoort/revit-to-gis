"""
GRASSHOPPER READY-TO-USE TEMPLATES
Copy-paste directly into Grasshopper Python Component
"""

# ============================================================================
# TEMPLATE 1: SIMPLE LOAD & DISPLAY
# ============================================================================
# Grasshopper Python Component
# Input: [None]
# Output: objects, count, summary

import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperDataHelper

try:
    helper = GrassholperDataHelper()
    objects = helper.load_input_data()
    count = len(objects) if objects else 0
    summary = helper.get_summary()
    
    print("✅ Loaded {} objects".format(count))
    print("Types: {}".format(summary["types"]))
    
except Exception as e:
    print("❌ Error: {}".format(e))
    objects = None
    count = 0
    summary = {"error": str(e)}

# ============================================================================
# TEMPLATE 2: LOAD + SCALE GEOMETRY
# ============================================================================
# Inputs: objects (from Template 1), scale_factor (Slider 0.5-2.0)
# Output: processed_objects

import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperDataHelper

try:
    helper = GrassholperDataHelper()
    helper.current_data = objects if objects else []
    
    scale = scale_factor if 'scale_factor' in dir() else 1.0
    
    # Scale coordinates
    for obj in helper.current_data:
        geom = obj.get("geometry", {})
        coords = geom.get("coordinates", [])
        
        def scale_coords(c, factor):
            if isinstance(c[0], (list, tuple)):
                return [scale_coords(sub, factor) for sub in c]
            return [val * factor for val in c]
        
        geom["coordinates"] = scale_coords(coords, scale)
        obj["version"] = obj.get("version", 1) + 1
    
    processed_objects = helper.current_data
    print("✅ Scaled {} objects by {}x".format(len(processed_objects), scale))
    
except Exception as e:
    print("❌ Error: {}".format(e))
    processed_objects = objects

# ============================================================================
# TEMPLATE 3: FILTER BY TYPE
# ============================================================================
# Inputs: objects, filter_type (Text: "Wall", "Floor", etc)
# Output: filtered_objects

import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

try:
    filter_t = filter_type if 'filter_type' in dir() else "Wall"
    
    filtered_objects = [
        obj for obj in objects 
        if obj.get("type", "") == filter_t
    ]
    
    print("✅ Filtered {} objects of type '{}'".format(len(filtered_objects), filter_t))
    
except Exception as e:
    print("❌ Error: {}".format(e))
    filtered_objects = objects

# ============================================================================
# TEMPLATE 4: ADD CUSTOM PROPERTIES
# ============================================================================
# Inputs: objects, custom_id (Text: "MY_PROJECT")
# Output: objects_with_props

import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from datetime import datetime

try:
    custom_id = custom_id if 'custom_id' in dir() else "GH_PROJECT"
    
    objects_with_props = []
    
    for obj in objects:
        obj["properties"]["custom_id"] = custom_id
        obj["properties"]["modified_in_gh"] = True
        obj["properties"]["gh_timestamp"] = datetime.now().isoformat()
        obj["version"] = obj.get("version", 1) + 1
        
        objects_with_props.append(obj)
    
    print("✅ Added properties to {} objects".format(len(objects_with_props)))
    
except Exception as e:
    print("❌ Error: {}".format(e))
    objects_with_props = objects

# ============================================================================
# TEMPLATE 5: SAVE OUTPUT
# ============================================================================
# Inputs: processed_objects (from any template above)
# Output: output_file, success

import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperDataHelper
from pathlib import Path

try:
    helper = GrassholperDataHelper()
    helper.current_data = processed_objects
    
    filepath = helper.save_output_data(processed_objects)
    output_file = str(filepath)
    success = True
    
    print("✅ Saved to: {}".format(filepath))
    
except Exception as e:
    print("❌ Error: {}".format(e))
    output_file = str(e)
    success = False

# ============================================================================
# TEMPLATE 6: EXPORT TO ARCGIS ONLINE
# ============================================================================
# Inputs: processed_objects, agol_username (Text), agol_password (Text)
# Output: agol_id, success, message

import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from agol_exporter import AGOLExporter

try:
    # Get credentials from inputs
    user = agol_username if 'agol_username' in dir() else "demo_user"
    pwd = agol_password if 'agol_password' in dir() else "demo_pass"
    
    exporter = AGOLExporter(user, pwd)
    
    success, result = exporter.export_to_agol(
        processed_objects,
        service_title="GH Modified - {}".format(datetime.now().strftime("%Y%m%d"))
    )
    
    agol_id = result if success else None
    message = "✅ Success!" if success else "❌ Failed: {}".format(result)
    
    print(message)
    
except Exception as e:
    print("❌ Error: {}".format(e))
    agol_id = None
    success = False
    message = str(e)

# ============================================================================
# TEMPLATE 7: COMPLETE PIPELINE (ALL-IN-ONE)
# ============================================================================
# Input: [None - loads automatically]
# Output: final_objects, output_file, agol_id

import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperPipeline, GrassholperDataHelper
from agol_exporter import AGOLExporter
from pathlib import Path
from datetime import datetime

try:
    # STEP 1: Load
    pipeline = GrassholperPipeline()
    data = pipeline.load_and_analyze()
    
    if not data:
        raise Exception("No data loaded")
    
    # STEP 2: Process (examples - modify as needed)
    for obj in data:
        # Example: Round coordinates
        geom = obj.get("geometry", {})
        coords = geom.get("coordinates", [])
        
        def round_coords(c, decimals=2):
            if isinstance(c[0], (list, tuple)):
                return [round_coords(sub, decimals) for sub in c]
            return [round(val, decimals) for val in c]
        
        geom["coordinates"] = round_coords(coords)
        
        # Add custom properties
        obj["properties"]["gh_processed"] = True
        obj["properties"]["process_date"] = datetime.now().isoformat()
        obj["version"] = obj.get("version", 1) + 1
    
    # STEP 3: Save
    helper = GrassholperDataHelper()
    helper.current_data = data
    output_path = helper.save_output_data(data)
    
    # STEP 4: Export to AGOL (optional)
    agol_id = None
    try:
        exporter = AGOLExporter("username", "password")
        success, result = exporter.export_to_agol(data)
        if success:
            agol_id = result
    except:
        pass  # AGOL export failed, but that's OK
    
    final_objects = data
    output_file = str(output_path)
    
    print("✅ Pipeline complete!")
    print("   Objects: {}".format(len(final_objects)))
    print("   File: {}".format(output_file))
    if agol_id:
        print("   AGOL: {}".format(agol_id))
    
except Exception as e:
    print("❌ Error: {}".format(e))
    import traceback
    traceback.print_exc()
    final_objects = None
    output_file = None
    agol_id = None

# ============================================================================
# TEMPLATE 8: VISUALIZATION (Rhino Geometry)
# ============================================================================
# Inputs: processed_objects
# Output: points, curves, colors

import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

try:
    from Rhino.Geometry import Point3d, Line, Curve, PolylineCurve
    from System.Drawing import Color
    
    points = []
    curves = []
    colors = []
    
    # Color map for types
    color_map = {
        "Wall": Color.Red,
        "Floor": Color.Blue,
        "Door": Color.Green,
        "Window": Color.Yellow,
        "Column": Color.Magenta,
    }
    
    for obj in processed_objects:
        obj_type = obj.get("type", "Unknown")
        color = color_map.get(obj_type, Color.Gray)
        geom = obj.get("geometry", {})
        coords = geom.get("coordinates", [])
        
        if geom.get("type") == "Point":
            # Point
            pt = Point3d(coords[0], coords[1], coords[2] if len(coords) > 2 else 0)
            points.append(pt)
            colors.append(color)
        
        elif geom.get("type") == "LineString":
            # Line/Polyline
            pts = [Point3d(c[0], c[1], c[2] if len(c) > 2 else 0) for c in coords]
            if len(pts) > 1:
                curve = PolylineCurve(pts)
                curves.append(curve)
                colors.append(color)
            else:
                points.extend(pts)
                colors.append(color)
        
        elif geom.get("type") == "Polygon":
            # Polygon
            if coords:
                pts = [Point3d(c[0], c[1], c[2] if len(c) > 2 else 0) for c in coords[0]]
                if len(pts) > 1:
                    curve = PolylineCurve(pts)
                    curves.append(curve)
                    colors.append(color)
    
    print("✅ Visualization ready!")
    print("   Points: {}".format(len(points)))
    print("   Curves: {}".format(len(curves)))
    
except ImportError:
    print("⚠️  Rhino.Geometry not available (use in Grasshopper)")
    points = []
    curves = []
    colors = []
except Exception as e:
    print("❌ Error: {}".format(e))
    points = []
    curves = []
    colors = []

# ============================================================================
# TEMPLATE 9: DATA TABLE (Properties Display)
# ============================================================================
# Inputs: processed_objects
# Output: data_table

try:
    # Create table-like structure
    data_table = []
    
    for obj in processed_objects:
        row = {
            "ID": obj.get("id", "?"),
            "Type": obj.get("type", "?"),
            "Version": obj.get("version", 1),
            "Properties": str(obj.get("properties", {}))[:50] + "..."
        }
        data_table.append(row)
    
    # Display as text
    output = "ID | Type | Ver | Properties\n"
    output += "---|------|-----|----------\n"
    for row in data_table[:20]:  # First 20 rows
        output += "{} | {} | {} | {}\n".format(
            row["ID"][:15], 
            row["Type"], 
            row["Version"],
            row["Properties"][:30]
        )
    
    if len(data_table) > 20:
        output += "... and {} more rows".format(len(data_table) - 20)
    
    data_table = output
    print("✅ Data table generated")
    
except Exception as e:
    print("❌ Error: {}".format(e))
    data_table = str(e)

# ============================================================================
# TEMPLATE 10: ERROR HANDLING WRAPPER
# ============================================================================
# Wrap any template above with this

def safe_execute(func):
    """Execute function with error handling"""
    try:
        result = func()
        return result, True, "Success"
    except Exception as e:
        print("❌ Error: {}".format(e))
        import traceback
        error_detail = traceback.format_exc()
        return None, False, error_detail

# Usage:
# def my_process():
#     helper = GrassholperDataHelper()
#     return helper.load_input_data()
#
# result, success, message = safe_execute(my_process)

# ============================================================================
# TIPS & TRICKS
# ============================================================================

"""
QUICK TIPS:
1. Always add sys.path first
2. Import only what you need
3. Use try/except for debugging
4. Print progress statements
5. Output to multiple ports for flexibility
6. Use Slider/Toggle/Text for inputs
7. Connect Python components in sequence
8. Right-click Python component → Show output
9. Use "View" → "Python Editor" for better IDE
10. Press Ctrl+Shift+M to minimize console

COMMON ERRORS:
- "ModuleNotFoundError" → Check sys.path
- "FileNotFoundError" → Check data/ directory exists
- "KeyError" → Object doesn't have that property
- IronPython issues → Use Python 3 in GH 2.0+

DEBUGGING:
1. Print intermediate values
2. Check data/ folder for output files
3. Look in Python console for errors
4. Use print() statements liberally
5. Test each template separately first
"""
