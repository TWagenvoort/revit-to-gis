# 🚀 GitHub Setup Checklist - TWagenvoort/revit-to-gis

## ✅ Wat ik heb voorbereid

Alle bestanden zijn klaar om naar GitHub te pushen:

- ✓ `setup.py` - pip installatie configuratie
- ✓ `requirements.txt` - Dependencies (requests, pyproj)
- ✓ `.gitignore` - Sluit data files uit (geen gigantic uploads)
- ✓ `LICENSE` - MIT licentie
- ✓ `MANIFEST.in` - Include files voor package
- ✓ `.github/workflows/tests.yml` - Automatic testing
- ✓ `GITHUB_SETUP.md` - Installatie gids
- ✓ `GITHUB_README.md` - Repository homepage
- ✓ Alle scripts/ files - Python modules

---

## 📋 Stappen om te doen (Jij)

### **Stap 1: Repository Aanmaken op GitHub**

1. Ga naar: https://github.com/new
2. Repository name: `revit-to-gis`
3. Description: "Bidirectional sync: Revit → Grasshopper → ArcGIS Online"
4. Public ✓
5. Do NOT initialize with README (we hebben al een)
6. Click "Create repository"

### **Stap 2: Initialize Local Git**

Open PowerShell in: `C:\Users\Thijs W\Desktop\Revit to GIS`

```powershell
cd "C:\Users\Thijs W\Desktop\Revit to GIS"
git init
git add .
git commit -m "Initial commit: Revit-GIS pipeline with GH integration"
git branch -M main
git remote add origin https://github.com/TWagenvoort/revit-to-gis.git
git push -u origin main
```

### **Stap 3: Verify on GitHub**

1. Ga naar: https://github.com/TWagenvoort/revit-to-gis
2. Check dat alle files zichtbaar zijn
3. Check dat README zichtbaar is
4. Test pip install:

```bash
pip install git+https://github.com/TWagenvoort/revit-to-gis.git
```

---

## 🔑 Voordat je git push doen:

### **Heb je Git geinstalleerd?**

```powershell
git --version
```

Moet output geven. Zo niet: https://git-scm.com/download/win installeren.

### **Heb je GitHub account?**

- ✓ Account: https://github.com/TWagenvoort (je username)
- ✓ Email ingesteld
- ✓ SSH key of HTTPS ingesteld

**Makkelijkste:** HTTPS gebruiken (geen keys nodig).

### **Git credentials onthouden?**

```powershell
git config --global user.name "Thijs Wagenvoort"
git config --global user.email "jouwemail@example.com"
```

---

## 📦 Na Push - Wat gebruikers kunnen doen

### **Option 1: pip install**
```bash
pip install git+https://github.com/TWagenvoort/revit-to-gis.git
```

### **Option 2: git clone**
```bash
git clone https://github.com/TWagenvoort/revit-to-gis.git
cd revit-to-gis
pip install -e .
```

### **Option 3: Download ZIP**
- GitHub → Code → Download ZIP

---

## 🎯 Grasshopper Usage After GitHub

```python
# Installer eerst
# pip install git+https://github.com/TWagenvoort/revit-to-gis.git

# Dan in Grasshopper Python component
from revit_to_gis.scripts.gh_helper import GrassholperDataHelper

helper = GrassholperDataHelper()
objects = helper.load_input_data()
print("✅ Loaded {} objects".format(len(objects)))
```

---

## ⚠️ Belangrijk

### **Data folder niet commiten**
`.gitignore` sluit uit:
- `data/gh_inputs/*.json`
- `data/gh_outputs/*.json`
- `data/.sync/*`

Dit is gewenst (niet alle data uploaden).

### **Setup.py aanpassingen**

In `setup.py` staat:
```python
author_email="",  # ← Vul je email in (optioneel)
```

Kan je aanpassen maar niet nodig.

### **Toekomstige updates**

Wanneer je wijzigingen maakt:

```powershell
git add .
git commit -m "Update: description of change"
git push
```

Pip-gebruikers kunnen updaten met:
```bash
pip install --upgrade git+https://github.com/TWagenvoort/revit-to-gis.git
```

---

## 🆘 Hulp Nodig?

| Probleem | Oplossing |
|----------|-----------|
| "git not found" | https://git-scm.com/download/win installeren |
| "fatal: not a git repository" | `git init` in je folder |
| "remote origin already exists" | `git remote remove origin` dan opnieuw |
| "fatal: Authentication failed" | HTTPS gebruiken (geen SSH nodig) |
| "Permission denied" | PowerShell als Admin runnen |

---

## ✨ Summary

Je hebt nu:

1. ✅ Alle GitHub setup files
2. ✅ Python package configuratie (setup.py)
3. ✅ Automated testing workflow
4. ✅ Proper documentation
5. ✅ pip installable package

**Enige wat jij moet doen:**
1. Repository aanmaken op GitHub
2. Git init + push (zie Stap 1-3 hierboven)

Dan kan iedereen installeren via pip! 🎉

