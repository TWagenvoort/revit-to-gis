# 🚀 Grasshopper Setup - GitHub Direct Loading (RECOMMENDED)

## ⚡ Fastest Way (No Installation!)

In Grasshopper Python Component, paste this:

```python
import urllib.request

# Load from GitHub (one-liner!)
exec(urllib.request.urlopen("https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py").read().decode('utf-8'))

# Now use it
gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()
objects = helper.load_input_data()

print("✅ Loaded {} objects from GitHub!".format(len(objects)))
```

**That's it!** No pip install, no file paths, nothing!

---

## 3️⃣ Setup Methods

### **Method 1: GitHub Direct (FASTEST - Recommended)**

```python
import urllib.request

# Load loader from GitHub
exec(urllib.request.urlopen("https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py").read().decode('utf-8'))

# Load module
gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()
objects = helper.load_input_data()
```

**Pros:** ✓ No setup needed ✓ Works anywhere ✓ Always latest version
**Cons:** ✗ Slower (downloads each run) ✗ Needs internet

---

### **Method 2: pip install**

**Terminal (one-time):**
```bash
pip install git+https://github.com/TWagenvoort/revit-to-gis.git
```

**Grasshopper:**
```python
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
objects = helper.load_input_data()
```

**Pros:** ✓ Fast (cached) ✓ Works offline
**Cons:** ✗ Setup required ✗ Need to update manually

---

### **Method 3: Local Path (Old Way)**

**For local development only:**

```python
import sys
sys.path.insert(0, r"C:\Users\Thijs W\Desktop\Revit to GIS\scripts")

from gh_helper import GrassholperDataHelper
helper = GrassholperDataHelper()
objects = helper.load_input_data()
```

---

## 📊 Comparison

| Feature | GitHub Direct | pip install | Local Path |
|---------|---|---|---|
| Setup | ⚡ None | ⏱️ 30 sec | ⏱️ 1 min |
| Speed | 🐢 Slow | 🚀 Fast | 🚀 Fast |
| Offline | ❌ No | ✅ Yes | ✅ Yes |
| Latest | ✅ Auto | ❌ Manual | ❌ Manual |
| **Recommended** | ✅ YES | ✅ YES | ⚠️ Dev only |

---

## 🎯 Recommended Setup for Teams

**For everyone (no setup required):**
```python
import urllib.request
exec(urllib.request.urlopen("https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py").read().decode('utf-8'))
gh_helper = load_github_module_simple('gh_helper')
# ... rest of code
```

**For power users (after pip install):**
```python
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper
# ... rest of code
```

---

## 📝 Complete 3-Component Pipeline (GitHub)

### **Component 1: Load from GitHub**

```python
import urllib.request

url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()
objects = helper.load_input_data()
count = len(objects) if objects else 0

print("✅ Loaded {} objects".format(count))
```

**Outputs:**
- `objects` → Geometry list
- `count` → Count

---

### **Component 2: Modify Geometry**

```python
# Receives: objects, scale_factor (from slider)

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

**Inputs:**
- `objects` ← From Component 1
- `scale_factor` ← Slider

**Outputs:**
- `modified_objects` → Scaled geometry

---

### **Component 3: Save & Export**

```python
import urllib.request

url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
exec(urllib.request.urlopen(url).read().decode('utf-8'))

gh_helper = load_github_module_simple('gh_helper')
helper = gh_helper.GrassholperDataHelper()

# Save
filepath = helper.save_output_data(objects)
output_file = str(filepath)

print("✅ Saved to {}".format(output_file))
```

**Inputs:**
- `objects` ← From Component 2

**Outputs:**
- `output_file` → File path string

---

## ✅ Quick Checklist

- [ ] Open Grasshopper
- [ ] Create Python component
- [ ] Paste GitHub direct loading code (Method 1 above)
- [ ] Add outputs: `objects`, `count`
- [ ] Press F5
- [ ] See "✅ Loaded X objects"
- [ ] Connect to next component
- [ ] Done! 🎉

---

## 📦 If You Prefer pip install

**Terminal:**
```bash
pip install git+https://github.com/TWagenvoort/revit-to-gis.git
```

**Then in Grasshopper:**
```python
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper
helper = GrassholperDataHelper()
objects = helper.load_input_data()
```

---

## 📚 More Templates

See [GH_TEMPLATES_GITHUB.md](GH_TEMPLATES_GITHUB.md) for:
- Load + modify + save
- Merge & conflict resolution
- Full pipeline examples
- Export to ArcGIS Online

---

## 🌐 GitHub Links

- **Repository**: https://github.com/TWagenvoort/revit-to-gis
- **Raw Scripts**: https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/
- **Issues**: https://github.com/TWagenvoort/revit-to-gis/issues

---

## 💡 Pro Tips

**Tip 1: Faster GitHub loading (cache locally)**
```python
import urllib.request
import os

cache_dir = os.path.expanduser("~\\AppData\\Local\\revit-gis")
os.makedirs(cache_dir, exist_ok=True)

cached_file = os.path.join(cache_dir, "github_loader.py")
if not os.path.exists(cached_file):
    url = "https://raw.githubusercontent.com/TWagenvoort/revit-to-gis/main/scripts/github_loader.py"
    with open(cached_file, 'w') as f:
        f.write(urllib.request.urlopen(url).read().decode('utf-8'))

with open(cached_file) as f:
    exec(f.read())
```

**Tip 2: Error handling**
```python
try:
    # Your code here
except Exception as e:
    print("Error: {}".format(str(e)))
    import traceback
    traceback.print_exc()
```

**Tip 3: See what's loading**
```python
# Add print statements
print("Step 1: Loading from GitHub...")
exec(urllib.request.urlopen(url).read().decode('utf-8'))
print("Step 2: Creating helper...")
gh_helper = load_github_module_simple('gh_helper')
print("Step 3: Initializing...")
helper = gh_helper.GrassholperDataHelper()
print("Step 4: Loading data...")
objects = helper.load_input_data()
print("✅ Done! Loaded {}".format(len(objects)))
```

---

**Ready to use? Start with Method 1 (GitHub Direct) - no setup needed!** 🚀
