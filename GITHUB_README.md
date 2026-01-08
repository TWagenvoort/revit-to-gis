# Revit to GIS - Bidirectional Sync Pipeline

> Connect Revit → Grasshopper → ArcGIS Online with automatic synchronization and conflict resolution

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## 🎯 What This Does

Automatically synchronize building data from **Revit** to **Grasshopper** to **ArcGIS Online** with:

- ✅ **Bidirectional Sync** - Changes in Revit or GH are tracked and merged
- ✅ **Conflict Resolution** - Multiple strategies to handle concurrent edits
- ✅ **Version Control** - Every change is timestamped and hashable
- ✅ **GIS Export** - Automatic GeoJSON conversion for ArcGIS Online
- ✅ **Grasshopper Native** - Works directly in Grasshopper Python components

## 🚀 Quick Start

### **1. Install (1 minute)**

```bash
pip install git+https://github.com/TWagenvoort/revit-to-gis.git
```

### **2. In Grasshopper (Python Component)**

```python
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
objects = helper.load_input_data()
print("✅ Loaded {} objects".format(len(objects)))
```

### **3. Modify & Save**

```python
# Modify your geometry here
for obj in objects:
    obj["version"] += 1

# Save
helper.save_output_data(objects)
```

### **4. Export to ArcGIS Online (Optional)**

```python
from revit_to_gis.scripts.agol_exporter import AGOLExporter

exporter = AGOLExporter()
exporter.export_to_agol(objects, username, password)
```

## 📦 Installation Methods

| Method | Command | For |
|--------|---------|-----|
| **pip** (Best) | `pip install git+https://github.com/TWagenvoort/revit-to-gis.git` | Most users |
| **git clone** | `git clone https://github.com/TWagenvoort/revit-to-gis.git` | Developers |
| **ZIP Download** | Download ZIP from GitHub | No Git installed |

👉 **[Detailed Setup Guide →](GITHUB_SETUP.md)**

## 📚 Documentation

- **[Getting Started](GITHUB_SETUP.md)** - Installation & first steps
- **[Grasshopper Guide](GRASSHOPPER_GUIDE.md)** - How to use in GH
- **[Architecture](ARCHITECTURE.md)** - System design & data flow
- **[API Reference](README.md)** - Complete function documentation
- **[Quick Cheatsheet](GH_CHEATSHEET.md)** - Common operations
- **[Workflow Diagrams](GH_WORKFLOW.md)** - Visual pipeline

## 🎓 Examples

### Load Revit Data
```python
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
buildings = helper.load_input_data()
print(buildings)  # List of geometry objects
```

### Modify Geometry
```python
for building in buildings:
    geom = building["geometry"]
    # Scale coordinates
    coords = geom["coordinates"]
    geom["coordinates"] = [[x * 2, y * 2] for x, y in coords]
```

### Handle Conflicts
```python
from revit_to_gis.scripts.merge_engine import ConflictResolver

resolver = ConflictResolver(strategy="revit_priority")
merged = resolver.resolve(revit_data, gh_data)
```

### Export to GeoJSON
```python
from revit_to_gis.scripts.agol_exporter import GeoJSONConverter

converter = GeoJSONConverter(epsg=32633)  # UTM 33N
geojson = converter.gh_to_geojson(buildings)
```

## 🔧 Core Features

### Version Tracking
Every object has:
- `version` - Incrementing number
- `timestamp` - ISO 8601 creation date
- `hash` - MD5 of content (change detection)

### Conflict Resolution Strategies
1. **last_write_wins** - Most recent edit wins
2. **revit_priority** - Revit always wins
3. **manual** - User decides

### Supported Elements
- Walls, Floors, Doors/Windows
- Columns, Beams, Ramps, Stairs
- Any custom element with geometry

### Coordinate Systems
- EPSG:32633 (UTM 33N - Netherlands default)
- EPSG:4326 (WGS84)
- EPSG:32632 (UTM 32N)
- EPSG:28992 (RD - Dutch)
- Custom via `config.py`

## 🏗️ Architecture

```
Revit
  ↓ [export_from_revit()]
  ↓ 
JSON files (data/gh_inputs/)
  ↓ [load_input_data()]
  ↓
Grasshopper
  ↓ [modify geometry]
  ↓
GH outputs (data/gh_outputs/)
  ↓ [merge_engine.sync()]
  ↓
Conflict Resolution
  ↓ [agol_exporter.export()]
  ↓
ArcGIS Online
```

## 📊 File Structure

```
revit-to-gis/
├── scripts/                 # Python modules
│   ├── gh_helper.py        # Grasshopper utilities
│   ├── merge_engine.py     # Sync & versioning
│   ├── agol_exporter.py    # GeoJSON & AGOL
│   ├── config.py           # Settings
│   └── ...
├── data/                    # Data directory (gitignored)
│   ├── gh_inputs/
│   ├── gh_outputs/
│   └── reports/
├── GITHUB_SETUP.md         # This guide
├── GRASSHOPPER_GUIDE.md    # GH integration
├── setup.py                # pip configuration
└── requirements.txt        # Dependencies
```

## 🤝 Contributing

Found a bug? Want to improve it?

1. **Fork** the repo
2. **Create** a feature branch (`git checkout -b feature/my-feature`)
3. **Commit** changes (`git commit -m 'Add feature'`)
4. **Push** to branch (`git push origin feature/my-feature`)
5. **Open** a Pull Request

## 📞 Support

- 📖 **Docs:** See documentation files in repo
- 🐛 **Issues:** [GitHub Issues](https://github.com/TWagenvoort/revit-to-gis/issues)
- 💬 **Questions:** Create an Issue with `[QUESTION]` prefix

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

**Made with ❤️ for AEC professionals**

[⬆ Back to top](#)
