# GitHub Quick Reference for TWagenvoort/revit-to-gis

## 🚀 First Time Setup (5 minutes)

### **Step 1: Install Git (one-time)**
- Download: https://git-scm.com/download/win
- Install with defaults
- Restart VS Code or terminal

### **Step 2: Install Python Package**

```bash
pip install git+https://github.com/TWagenvoort/revit-to-gis.git
```

### **Step 3: Test in Grasshopper**

```python
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper
print("✅ Success!")
```

---

## 📦 Three Installation Methods

| Method | Command | Best For | Speed |
|--------|---------|----------|-------|
| **pip** | `pip install git+https://github.com/TWagenvoort/revit-to-gis.git` | Production use | Fast |
| **git clone** | `git clone https://github.com/TWagenvoort/revit-to-gis.git` | Development | Medium |
| **Download ZIP** | GitHub → Code → Download ZIP | No Git installed | Slow |

---

## 💡 Common Tasks

### **Update to Latest Version**
```bash
pip install --upgrade git+https://github.com/TWagenvoort/revit-to-gis.git
```

### **Use Latest Development Version**
```bash
pip install git+https://github.com/TWagenvoort/revit-to-gis.git@main --force-reinstall
```

### **Check What's Installed**
```bash
pip show revit-to-gis
```

### **Uninstall**
```bash
pip uninstall revit-to-gis
```

---

## 🔗 Repository Structure

```
github.com/TWagenvoort/revit-to-gis/
├── scripts/              ← All Python code
├── data/                 ← Data files (not in git)
├── README.md             ← Full documentation
├── setup.py              ← pip configuration
├── requirements.txt      ← Dependencies
├── GITHUB_SETUP.md       ← This file
└── *.md                  ← Various guides
```

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "git is not recognized" | Install from https://git-scm.com/download/win |
| "ModuleNotFoundError" | `pip install --force-reinstall git+https://github.com/TWagenvoort/revit-to-gis.git` |
| "Permission denied" | Run terminal as Administrator |
| "SSL error" | `pip install git+https://github.com/TWagenvoort/revit-to-gis.git --default-timeout=1000` |

---

## 🌐 GitHub URLs

- **Repository**: https://github.com/TWagenvoort/revit-to-gis
- **Issues**: https://github.com/TWagenvoort/revit-to-gis/issues
- **Releases**: https://github.com/TWagenvoort/revit-to-gis/releases

---

## 📝 In Grasshopper

```python
# Always use this import after pip install
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

# Everything else same as before
helper = GrassholperDataHelper()
data = helper.load_input_data()
```

Done! 🎉
