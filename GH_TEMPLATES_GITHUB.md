# Grasshopper Templates - Direct GitHub Loading

## ⭐ Template 0: Load from GitHub (New!)

Perfect als je geen pip install wil doen:

```python
"""Load Revit Data from GitHub"""
import urllib.request
import sys

# Download GitHub loader
url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
response = urllib.request.urlopen(url)
loader_code = response.read().decode('utf-8')

# Execute loader
exec(loader_code)

# Now load gh_helper
gh_helper = load_github_module_simple('gh_helper')

# Use it!
helper = gh_helper.GrassholperDataHelper()
objects = helper.load_input_data()
count = len(objects) if objects else 0

print("✅ Loaded {} objects from GitHub!".format(count))
```

**Output:**
- `objects` → All loaded geometry
- `count` → Number of objects

---

## Template 1: Simple Load (GitHub version)

```python
"""Option A: Via pip install"""
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
objects = helper.load_input_data()
count = len(objects) if objects else 0
print("✅ Loaded {} objects".format(count))

"""Option B: Via GitHub"""
import urllib.request
url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))
gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()
objects = helper.load_input_data()
```

---

## Template 2: Load + Modify (GitHub)

```python
import urllib.request

# Load from GitHub
url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()
objects = helper.load_input_data()

# Modify
for obj in objects:
    geom = obj.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    # Scale
    def scale_coords(c, factor):
        if isinstance(c[0], (list, tuple)):
            return [scale_coords(sub, factor) for sub in c]
        return [val * factor for val in c]
    
    geom["coordinates"] = scale_coords(coords, 2.0)

modified_objects = objects
```

---

## Template 3: Load + Save + Export (GitHub)

```python
import urllib.request

# Load loader from GitHub
loader_url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(loader_url).read().decode('utf-8'))

# Load all modules
gh_helper = load_github_module_simple('gh_helper')
agol_exporter = load_github_module_simple('agol_exporter')

# 1. Load
helper = gh_helper.GrassholperDataHelper()
objects = helper.load_input_data()
print("Loaded {} objects".format(len(objects)))

# 2. Modify
for obj in objects:
    obj["version"] = obj.get("version", 1) + 1

# 3. Save
output_path = helper.save_output_data(objects)
print("✅ Saved to {}".format(output_path))

# 4. Export (optional)
# exporter = agol_exporter.AGOLExporter()
# exporter.export_to_agol(objects, username, password)

results = {
    "count": len(objects),
    "file": str(output_path),
    "version_bumped": True
}
```

---

## Template 4: Merge & Conflict Resolution (GitHub)

```python
import urllib.request
import json

# Load from GitHub
url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

merge_engine = load_github_module_simple('merge_engine')

# Create resolver with Revit priority strategy
resolver = merge_engine.ConflictResolver(strategy="revit_priority")

# Load data
revit_data = [{"id": "1", "version": 2, "name": "Wall A"}]
gh_data = [{"id": "1", "version": 3, "name": "Wall A Modified"}]

# Merge with conflict resolution
merged = resolver.resolve(revit_data, gh_data)

output = {
    "merged_count": len(merged) if merged else 0,
    "strategy": "revit_priority"
}
```

---

## Template 5: Full Pipeline (GitHub)

```python
import urllib.request

# Load from GitHub (one-liner!)
exec(urllib.request.urlopen("https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py").read().decode('utf-8'))

# Load all modules
gh_helper = load_github_module_simple('gh_helper')
merge_engine = load_github_module_simple('merge_engine')
agol_exporter = load_github_module_simple('agol_exporter')

try:
    # Step 1: Load
    helper = gh_helper.GrassholperDataHelper()
    objects = helper.load_input_data()
    
    # Step 2: Version
    for obj in objects:
        obj["version"] = obj.get("version", 1) + 1
    
    # Step 3: Save
    output_path = helper.save_output_data(objects)
    
    # Step 4: Conflict check (demo)
    resolver = merge_engine.ConflictResolver()
    
    # Step 5: Export summary
    summary = {
        "loaded": len(objects),
        "saved_to": str(output_path),
        "versions_incremented": True,
        "ready_for_agol": True
    }
    
    output = summary
    
except Exception as e:
    output = {"error": str(e)}
```

---

## 📝 Comparison: pip vs GitHub

| Method | Setup | Usage | Speed |
|--------|-------|-------|-------|
| **pip install** | `pip install git+https://github.com/TWagenvoort/revit-to-gis.git` | `from revit_to_gis.scripts...` | Fast (cached) |
| **GitHub direct** | None (one-liner import) | `exec(urllib.request.urlopen(...))` | Slower (every run) |
| **Best for** | Production / repeated use | Quick testing / demos | Depends on use case |

---

## 🚀 Recommended: Hybrid Approach

```python
import sys

# Try pip first (fast if installed)
try:
    from revit_to_gis.scripts.gh_helper import GrassholperDataHelper
    print("Using pip-installed version")
    helper = GrassholperDataHelper()
    
except ImportError:
    # Fallback to GitHub
    print("Falling back to GitHub...")
    import urllib.request
    url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
    exec(urllib.request.urlopen(url).read().decode('utf-8'))
    
    gh_helper = load_github_module_simple('gh_helper')
    helper = gh_helper.GrassholperDataHelper()

# Now use helper
objects = helper.load_input_data()
```

This works with OR without pip install! 🎉

---

## 📖 More Info

- GitHub Loader: [scripts/github_loader.py](../scripts/github_loader.py)
- Package Docs: [README.md](../README.md)
- Repo: https://github.com/TWagenvoort/revit-to-gis
