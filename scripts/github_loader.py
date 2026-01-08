"""
GitHub Direct Loader - Load modules directly from GitHub without installation

Usage:
    from github_loader import load_module
    gh_helper = load_module('gh_helper')
    
    # Or
    SyncEngine = load_class('merge_engine', 'SyncEngine')
"""

import sys
import urllib.request
import importlib.util

# GitHub repository information
GITHUB_REPO = "TWagenvoort/revit-to-gis"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"

SCRIPTS_URL = f"{GITHUB_RAW_URL}/scripts"


def load_module_from_github(module_name):
    """
    Load a module directly from GitHub
    
    Args:
        module_name: Name of module file (without .py)
        
    Returns:
        Loaded module object
        
    Example:
        gh_helper = load_module_from_github('gh_helper')
        data = gh_helper.GrassholperDataHelper()
    """
    
    url = f"{SCRIPTS_URL}/{module_name}.py"
    
    try:
        print(f"Loading from GitHub: {url}")
        
        # IMPORTANT: Clear cached version to force fresh download
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # Download the file
        response = urllib.request.urlopen(url)
        code = response.read().decode('utf-8')
        
        # Create and execute module
        module = importlib.util.module_from_spec(
            importlib.util.spec_from_loader(module_name, loader=None)
        )
        module.__file__ = url
        exec(code, module.__dict__)
        
        sys.modules[module_name] = module
        
        print(f"✅ Loaded {module_name} from GitHub (fresh)")
        return module
        
    except Exception as e:
        print(f"❌ Error loading {module_name}: {e}")
        raise


def load_class_from_github(module_name, class_name):
    """
    Load a specific class from a GitHub module
    
    Args:
        module_name: Name of module file
        class_name: Name of class to load
        
    Returns:
        Class object
        
    Example:
        SyncEngine = load_class_from_github('merge_engine', 'SyncEngine')
    """
    
    module = load_module_from_github(module_name)
    return getattr(module, class_name)


def load_config_from_github():
    """
    Load config from GitHub
    
    Returns:
        config module
    """
    return load_module_from_github('config')


def load_all_from_github():
    """
    Load all modules from GitHub
    
    Returns:
        Dictionary with all modules
    """
    
    modules = {}
    module_names = [
        'gh_helper',
        'merge_engine',
        'revit_gh_bridge',
        'agol_exporter',
        'integration_pipeline',
        'config'
    ]
    
    for name in module_names:
        try:
            modules[name] = load_module_from_github(name)
            print(f"✅ {name}")
        except Exception as e:
            print(f"⚠️  {name}: {e}")
    
    return modules


# Simpler version using direct exec - FORCE FRESH DOWNLOAD
def load_github_module_simple(module_name):
    """
    Simplified loader using exec - ALWAYS downloads fresh from GitHub
    
    Usage:
        gh_helper = load_github_module_simple('gh_helper')
        helper = gh_helper.GrassholperDataHelper(data_dir=r"C:\path\to\data")
    """
    
    url = f"{SCRIPTS_URL}/{module_name}.py"
    
    try:
        print(f"⬇️  Loading {module_name} from GitHub (force fresh)...")
        
        # IMPORTANT: Clear any cached version to ensure fresh download
        if module_name in sys.modules:
            print(f"   Clearing cached {module_name}...")
            del sys.modules[module_name]
        
        # Download and execute - always fresh
        with urllib.request.urlopen(url) as response:
            code = response.read().decode('utf-8')
        
        print(f"   Downloaded {len(code)} bytes")
        
        # Create a module
        module = type(sys)('module')
        module.__name__ = module_name
        module.__file__ = url
        
        # Execute code in module namespace
        exec(code, module.__dict__)
        
        # Register in sys.modules (overwrites any cached version)
        sys.modules[module_name] = module
        
        print(f"✅ {module_name} loaded from GitHub (fresh)")
        return module
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Test
    print("Testing GitHub loader...")
    print(f"Repo: {GITHUB_REPO}")
    print(f"URL: {SCRIPTS_URL}\n")
    
    # Try loading
    try:
        gh_helper = load_github_module_simple('gh_helper')
        print("\n✅ Successfully loaded gh_helper from GitHub!")
    except Exception as e:
        print(f"\n❌ Failed to load: {e}")
