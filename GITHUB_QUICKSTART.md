# ⭐ GitHub Quick Start - Copy & Paste Ready!

## 🚀 Grasshopper - ONE-LINER Setup

Paste this in a **Grasshopper Python Component** and you're done:

```python
import urllib.request; exec(urllib.request.urlopen("https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py").read().decode('utf-8')); gh_helper = load_github_module_simple('gh_helper'); helper = gh_helper.GrassholperDataHelper(); objects = helper.load_input_data(); count = len(objects) if objects else 0; print("✅ Loaded {} objects".format(count))
```

Output: `objects`, `count`

---

## 📋 Better Formatted (Copy This Instead)

```python
import urllib.request

# Load from GitHub
url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

# Create helper
gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()

# Load data
objects = helper.load_input_data()
count = len(objects) if objects else 0

print("✅ Loaded {} objects from GitHub!".format(count))
```

**Right-click output → Rename to:** `objects`, `count`

---

## 🔄 Load + Modify + Save (Full Workflow)

```python
import urllib.request

# Load
url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()
objects = helper.load_input_data()

# Modify
for obj in objects:
    obj["version"] = obj.get("version", 1) + 1
    # Add your custom modifications here

# Save
filepath = helper.save_output_data(objects)

output_file = str(filepath)
object_count = len(objects)
success = True
```

**Outputs:** `output_file`, `object_count`, `success`

---

## 🌍 Export to ArcGIS Online (Optional)

```python
import urllib.request

# Load modules
url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

gh_helper = load_github_module_simple('gh_helper')
agol = load_github_module_simple('agol_exporter')

# Load data
helper = gh_helper.GrassholperDataHelper()
objects = helper.load_input_data()

# Convert to GeoJSON
converter = agol.GeoJSONConverter(epsg=32633)  # UTM 33N
geojson = converter.gh_to_geojson(objects)

# Export (needs credentials)
exporter = agol.AGOLExporter()
# result = exporter.export_to_agol(objects, 'your_username', 'your_password')

output = {
    "objects": len(objects),
    "geojson_ready": geojson is not None,
    "epsg": 32633
}
```

---

## 🎨 Full 3-Component Setup Diagram

```
[Load from GitHub] ──→ [Modify + Scale] ──→ [Save + Export]
      │                      │                    │
      ├─ objects ────────────┤                    │
      └─ count              └─ modified_objects ──┤
                                                   ├─ output_file
                                                   └─ success
```

---

## ✅ Test It Works

Paste in Grasshopper and check console for:

```
✅ Loaded X objects from GitHub!
```

If you see errors, check:
1. Grasshopper is connected to internet
2. Copy-paste is correct (no extra spaces)
3. Python 3 version (not IronPython 2)

---

## 📚 Full Documentation

- **GitHub Setup**: [GH_GITHUB_SETUP.md](GH_GITHUB_SETUP.md)
- **All Templates**: [GH_TEMPLATES_GITHUB.md](GH_TEMPLATES_GITHUB.md)
- **API Docs**: [README.md](README.md)
- **Repo**: https://github.com/TWagenvoort/revit-to-gis

---

## 🎁 What You Get

```
revit-to-gis on GitHub
├── scripts/
│   ├── gh_helper.py          ← Load/save data
│   ├── merge_engine.py       ← Versioning & conflicts
│   ├── agol_exporter.py      ← GeoJSON & ArcGIS
│   ├── github_loader.py      ← Load from GitHub ⭐
│   └── ...
├── data/                     ← Your files
│   ├── gh_inputs/            ← From Revit
│   └── gh_outputs/           ← Your modifications
└── All documentation & examples
```

Everything loads from GitHub - no installation needed! 🚀

---

## 🔗 All 3 Ways to Use

| Way | Code | Setup | Speed |
|-----|------|-------|-------|
| **GitHub Direct** | `exec(urllib.request.urlopen(...))` | ⚡ None | 🐢 Slow |
| **pip install** | `from revit_to_gis.scripts...` | ⏱️ 30s | 🚀 Fast |
| **Local** | `sys.path.insert(...scripts)` | ⏱️ Manual | 🚀 Fast |

**Recommended for teams:** GitHub Direct (no setup!)

---

**Made with ❤️ for AEC professionals - Ready to use!** 🎉
