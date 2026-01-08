# GitHub Setup & Installation Guide

## 📦 Installation Options

### **Option 1: pip install (Recommended)**

```bash
pip install git+https://github.com/TWagenvoort/revit-to-gis.git
```

Then in Grasshopper:
```python
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
objects = helper.load_input_data()
```

---

### **Option 2: git clone (For Development)**

```bash
# Terminal
cd "C:\Users\Thijs W\Desktop"
git clone https://github.com/TWagenvoort/revit-to-gis.git
cd revit-to-gis

# Install in development mode
pip install -e .
```

Then use same import as Option 1.

---

### **Option 3: Direct Download (No git required)**

1. Go to: https://github.com/TWagenvoort/revit-to-gis
2. Click: **Code** → **Download ZIP**
3. Extract to: `C:\Users\Thijs W\Desktop\revit-to-gis`
4. In Grasshopper:

```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\revit-to-gis\scripts")

from gh_helper import GrassholperDataHelper
helper = GrassholperDataHelper()
```

---

## 🚀 Quick Start After Installation

### **Step 1: Verify Installation**

```bash
python -c "from revit_to_gis.scripts.gh_helper import GrassholperDataHelper; print('✅ Installed!')"
```

### **Step 2: In Grasshopper Python Component**

```python
# Option A: pip install method
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
objects = helper.load_input_data()
count = len(objects) if objects else 0
print("✅ Loaded {} objects".format(count))
```

### **Step 3: Complete Workflow**

```python
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper
from revit_to_gis.scripts.agol_exporter import AGOLExporter

# Load
helper = GrassholperDataHelper()
objects = helper.load_input_data()

# Modify (your custom code here)
for obj in objects:
    obj["version"] += 1

# Save
helper.save_output_data(objects)

# Export (optional)
# exporter = AGOLExporter()
# exporter.export_to_agol(objects, agol_username, agol_password)
```

---

## 📁 File Structure After Clone

```
revit-to-gis/
├── scripts/
│   ├── __init__.py
│   ├── gh_helper.py
│   ├── merge_engine.py
│   ├── revit_gh_bridge.py
│   ├── agol_exporter.py
│   ├── integration_pipeline.py
│   └── config.py
├── data/
│   ├── gh_inputs/
│   ├── gh_outputs/
│   ├── reports/
│   └── .sync/
├── README.md
├── setup.py
├── requirements.txt
├── .gitignore
└── *.md (guides)
```

---

## 🔧 Troubleshooting

### ❓ "ModuleNotFoundError: No module named 'revit_to_gis'"

**Solution:**
```bash
# Reinstall with pip
pip install git+https://github.com/TWagenvoort/revit-to-gis.git --force-reinstall

# Or use direct method in GH
import sys
sys.path.insert(0, r"<your-local-path>\revit-to-gis\scripts")
```

### ❓ "git is not recognized"

**Solution:**
1. Install Git from: https://git-scm.com/download/win
2. Restart terminal
3. Try again

### ❓ Permission denied on Windows

**Solution:**
```bash
# Run as Administrator
pip install git+https://github.com/TWagenvoort/revit-to-gis.git
```

---

## 📝 Updates

Once installed, keep it up to date:

```bash
# pip method
pip install --upgrade git+https://github.com/TWagenvoort/revit-to-gis.git

# git clone method
cd revit-to-gis
git pull
```

---

## 💡 Contributing

Found a bug? Want to improve it?

1. Fork the repo
2. Make changes
3. Create a Pull Request

---

## 📞 Support

Issues? Check:
- [README.md](README.md) - Full documentation
- [GH_CHEATSHEET.md](GH_CHEATSHEET.md) - Quick fixes
- GitHub Issues: https://github.com/TWagenvoort/revit-to-gis/issues
