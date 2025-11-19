"""
Dependency Version Checker for India Economic Pulse Dashboard
Checks installed versions, compatibility, and generates requirements.txt
"""

import sys
import subprocess
import importlib
import pkg_resources
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def check_python_version():
    """Check Python version"""
    print_header("PYTHON VERSION")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    print(f"Full Version: {sys.version}")
    
    if version.major == 3 and version.minor >= 9:
        print("✅ Python version is compatible (3.9+)")
    else:
        print("⚠️  Warning: Python 3.9+ recommended")
    
    return f"{version.major}.{version.minor}.{version.micro}"

def get_installed_version(package_name):
    """Get installed version of a package"""
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return None

def check_module_import(module_name, import_as=None):
    """Try to import a module and return success status"""
    try:
        if import_as:
            exec(f"import {module_name} as {import_as}")
        else:
            importlib.import_module(module_name)
        return True, "✅ Imported successfully"
    except ImportError as e:
        return False, f"❌ Import failed: {str(e)}"
    except Exception as e:
        return False, f"⚠️  Error: {str(e)}"

def check_all_dependencies():
    """Check all project dependencies"""
    print_header("CHECKING ALL DEPENDENCIES")
    
    # Define all dependencies used in the project
    dependencies = {
        'streamlit': {
            'package': 'streamlit',
            'import': 'streamlit',
            'recommended': '1.31.0',
            'min_version': '1.25.0'
        },
        'pandas': {
            'package': 'pandas',
            'import': 'pandas',
            'recommended': '2.2.0',
            'min_version': '2.0.0'
        },
        'plotly': {
            'package': 'plotly',
            'import': 'plotly',
            'recommended': '5.18.0',
            'min_version': '5.0.0'
        },
        'plotly.graph_objects': {
            'package': 'plotly',
            'import': 'plotly.graph_objects',
            'recommended': '5.18.0',
            'min_version': '5.0.0'
        },
        'plotly.express': {
            'package': 'plotly',
            'import': 'plotly.express',
            'recommended': '5.18.0',
            'min_version': '5.0.0'
        },
        'numpy': {
            'package': 'numpy',
            'import': 'numpy',
            'recommended': '1.26.3',
            'min_version': '1.24.0'
        },
        'openpyxl': {
            'package': 'openpyxl',
            'import': 'openpyxl',
            'recommended': '3.1.2',
            'min_version': '3.0.0'
        },
        'pathlib': {
            'package': 'pathlib',
            'import': 'pathlib',
            'recommended': 'Built-in',
            'min_version': 'Built-in'
        },
        'warnings': {
            'package': 'warnings',
            'import': 'warnings',
            'recommended': 'Built-in',
            'min_version': 'Built-in'
        },
        'datetime': {
            'package': 'datetime',
            'import': 'datetime',
            'recommended': 'Built-in',
            'min_version': 'Built-in'
        },
        'io': {
            'package': 'io',
            'import': 'io',
            'recommended': 'Built-in',
            'min_version': 'Built-in'
        }
    }
    
    results = []
    issues = []
    
    for name, info in dependencies.items():
        print(f"\nChecking: {name}")
        print("-" * 50)
        
        # Get installed version
        installed = get_installed_version(info['package'])
        
        if installed:
            print(f"📦 Package: {info['package']}")
            print(f"✅ Installed Version: {installed}")
            print(f"💡 Recommended: {info['recommended']}")
            
            # Try to import
            success, message = check_module_import(info['import'])
            print(f"   {message}")
            
            result = {
                'name': name,
                'package': info['package'],
                'installed': installed,
                'recommended': info['recommended'],
                'import_success': success
            }
            
            if not success:
                issues.append(f"{name}: Import failed")
                
        elif info['recommended'] == 'Built-in':
            print(f"📦 Package: {info['package']}")
            print(f"✅ Built-in module (part of Python standard library)")
            
            # Try to import
            success, message = check_module_import(info['import'])
            print(f"   {message}")
            
            result = {
                'name': name,
                'package': info['package'],
                'installed': 'Built-in',
                'recommended': 'Built-in',
                'import_success': success
            }
        else:
            print(f"❌ NOT INSTALLED: {info['package']}")
            print(f"   Install with: pip install {info['package']}")
            
            result = {
                'name': name,
                'package': info['package'],
                'installed': None,
                'recommended': info['recommended'],
                'import_success': False
            }
            
            issues.append(f"{name}: Not installed")
        
        results.append(result)
    
    return results, issues

def check_streamlit_imports():
    """Check specific Streamlit Cloud compatibility"""
    print_header("STREAMLIT CLOUD COMPATIBILITY CHECK")
    
    streamlit_checks = [
        ('streamlit', 'st'),
        ('streamlit.runtime.scriptrunner', None),
        ('streamlit.delta_generator', None),
    ]
    
    for module, alias in streamlit_checks:
        success, message = check_module_import(module, alias)
        print(f"{module}: {message}")

def generate_requirements_txt(results):
    """Generate requirements.txt from installed versions"""
    print_header("GENERATING requirements.txt")
    
    requirements = []
    
    for result in results:
        if result['installed'] and result['installed'] != 'Built-in':
            # Only add non-built-in packages
            if result['package'] not in [r.split('==')[0] for r in requirements]:
                requirements.append(f"{result['package']}=={result['installed']}")
    
    # Remove duplicates
    requirements = sorted(list(set(requirements)))
    
    print("Generated requirements.txt:")
    print("-" * 50)
    for req in requirements:
        print(req)
    
    # Save to file
    req_file = Path('requirements_generated.txt')
    with open(req_file, 'w') as f:
        f.write('\n'.join(requirements))
    
    print(f"\n✅ Saved to: {req_file}")
    
    return requirements

def check_critical_imports():
    """Test critical imports from project files"""
    print_header("TESTING PROJECT-SPECIFIC IMPORTS")
    
    critical_imports = [
        "from plotly.subplots import make_subplots",
        "import plotly.graph_objects as go",
        "import plotly.express as px",
        "from io import BytesIO",
        "from datetime import datetime",
        "from pathlib import Path",
    ]
    
    for import_stmt in critical_imports:
        try:
            exec(import_stmt)
            print(f"✅ {import_stmt}")
        except Exception as e:
            print(f"❌ {import_stmt}")
            print(f"   Error: {e}")

def list_all_installed_packages():
    """List all installed packages"""
    print_header("ALL INSTALLED PACKAGES")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"Error listing packages: {e}")

def check_conflicting_versions():
    """Check for known version conflicts"""
    print_header("CHECKING FOR VERSION CONFLICTS")
    
    # Check if numpy version is compatible with pandas
    numpy_ver = get_installed_version('numpy')
    pandas_ver = get_installed_version('pandas')
    
    print(f"NumPy: {numpy_ver}")
    print(f"Pandas: {pandas_ver}")
    
    if numpy_ver and pandas_ver:
        numpy_major = int(numpy_ver.split('.')[0])
        if numpy_major >= 2:
            print("⚠️  NumPy 2.x detected - may have compatibility issues with some packages")
            print("   Recommended: Use NumPy 1.26.x for maximum compatibility")
        else:
            print("✅ NumPy version compatible")

def run_full_check():
    """Run complete dependency check"""
    print("\n" + "🔍" * 35)
    print("  INDIA ECONOMIC PULSE - DEPENDENCY CHECKER")
    print("🔍" * 35)
    
    # Check Python version
    python_ver = check_python_version()
    
    # Check all dependencies
    results, issues = check_all_dependencies()
    
    # Check Streamlit compatibility
    check_streamlit_imports()
    
    # Test critical imports
    check_critical_imports()
    
    # Check for conflicts
    check_conflicting_versions()
    
    # Generate requirements.txt
    requirements = generate_requirements_txt(results)
    
    # Summary
    print_header("SUMMARY")
    
    total = len(results)
    successful = sum(1 for r in results if r['import_success'])
    
    print(f"Total Dependencies Checked: {total}")
    print(f"Successfully Imported: {successful}")
    print(f"Issues Found: {len(issues)}")
    
    if issues:
        print("\n⚠️  ISSUES DETECTED:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ ALL DEPENDENCIES OK!")
    
    # Recommendations
    print_header("RECOMMENDATIONS")
    
    if issues:
        print("Run these commands to fix issues:")
        print()
        for result in results:
            if not result['import_success'] and result['recommended'] != 'Built-in':
                print(f"pip install {result['package']}=={result['recommended']}")
    else:
        print("✅ Your environment is ready for deployment!")
        print()
        print("Next steps:")
        print("1. Copy requirements_generated.txt to requirements.txt")
        print("2. Test locally: streamlit run app.py")
        print("3. Push to GitHub")
        print("4. Deploy to Streamlit Cloud")
    
    # Optional: List all packages
    user_input = input("\n📋 List all installed packages? (y/n): ")
    if user_input.lower() == 'y':
        list_all_installed_packages()

if __name__ == "__main__":
    run_full_check()