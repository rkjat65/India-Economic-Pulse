"""
AI Image Generator Integration - Testing Script
Run this to verify all components are properly installed and configured
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def test_dependencies():
    """Test if all required packages are installed"""
    print_header("Testing Dependencies")
    
    required_packages = {
        'streamlit': 'streamlit',
        'streamlit_option_menu': 'streamlit-option-menu',
        'anthropic': 'anthropic',
        'PIL': 'pillow',
        'pandas': 'pandas',
        'plotly': 'plotly',
        'numpy': 'numpy'
    }
    
    optional_packages = {
        'openai': 'openai'
    }
    
    all_good = True
    
    # Test required packages
    for module, package in required_packages.items():
        try:
            __import__(module)
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} NOT installed - REQUIRED")
            all_good = False
    
    # Test optional packages
    for module, package in optional_packages.items():
        try:
            __import__(module)
            print_success(f"{package} installed (optional)")
        except ImportError:
            print_warning(f"{package} not installed (optional for DALL-E support)")
    
    return all_good

def test_file_structure():
    """Test if all required files exist"""
    print_header("Testing File Structure")
    
    required_files = [
        'ai_image_generator.py',
        'app.py',
        'requirements.txt'
    ]
    
    recommended_files = [
        '.streamlit/secrets.toml',
        'data_fetcher.py',
        'views.py',
        'visualizations.py'
    ]
    
    all_good = True
    
    # Test required files
    for file in required_files:
        if os.path.exists(file):
            print_success(f"{file} exists")
        else:
            print_error(f"{file} NOT FOUND - REQUIRED")
            all_good = False
    
    # Test recommended files
    for file in recommended_files:
        if os.path.exists(file):
            print_success(f"{file} exists")
        else:
            print_warning(f"{file} not found (recommended)")
    
    return all_good

def test_imports():
    """Test if custom modules can be imported"""
    print_header("Testing Module Imports")
    
    all_good = True
    
    # Test ai_image_generator
    try:
        import ai_image_generator
        print_success("ai_image_generator module imports successfully")
        
        # Check for required functions
        functions = [
            'generate_economic_image',
            'create_prompt_suggestions',
            'render_image_generator_ui'
        ]
        
        for func in functions:
            if hasattr(ai_image_generator, func):
                print_success(f"  - {func}() found")
            else:
                print_error(f"  - {func}() NOT FOUND")
                all_good = False
                
    except ImportError as e:
        print_error(f"ai_image_generator import failed: {str(e)}")
        all_good = False
    
    return all_good

def test_secrets():
    """Test if API keys are configured"""
    print_header("Testing API Configuration")
    
    secrets_path = '.streamlit/secrets.toml'
    
    if not os.path.exists(secrets_path):
        print_error("secrets.toml not found")
        print_warning("Create .streamlit/secrets.toml with your API keys")
        return False
    
    # Try to load secrets
    try:
        import streamlit as st
        
        # Check for API keys
        has_anthropic = 'ANTHROPIC_API_KEY' in st.secrets
        has_openai = 'OPENAI_API_KEY' in st.secrets
        
        if has_anthropic:
            key = st.secrets['ANTHROPIC_API_KEY']
            if key and len(key) > 10:
                print_success("Anthropic API key configured")
            else:
                print_warning("Anthropic API key seems invalid")
        else:
            print_error("Anthropic API key not found in secrets")
        
        if has_openai:
            key = st.secrets['OPENAI_API_KEY']
            if key and len(key) > 10:
                print_success("OpenAI API key configured (optional)")
            else:
                print_warning("OpenAI API key seems invalid")
        else:
            print_warning("OpenAI API key not configured (optional)")
        
        return has_anthropic
        
    except Exception as e:
        print_error(f"Error reading secrets: {str(e)}")
        return False

def test_api_connection():
    """Test if API connection works"""
    print_header("Testing API Connection")
    
    try:
        import streamlit as st
        import anthropic
        
        api_key = st.secrets.get('ANTHROPIC_API_KEY', '')
        
        if not api_key:
            print_error("No API key configured - skipping connection test")
            return False
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Try a simple API call
        print("Testing Anthropic API connection...")
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'API test successful' if you can read this."
                }
            ]
        )
        
        response = message.content[0].text
        
        if "successful" in response.lower():
            print_success("Anthropic API connection working!")
            print(f"  Response: {response}")
            return True
        else:
            print_warning("API responded but unexpected response")
            print(f"  Response: {response}")
            return True
            
    except Exception as e:
        print_error(f"API connection failed: {str(e)}")
        return False

def test_ui_components():
    """Test if UI components are available"""
    print_header("Testing UI Components")
    
    try:
        import streamlit as st
        from streamlit_option_menu import option_menu
        
        print_success("Streamlit available")
        print_success("Option menu available")
        
        # Check version
        print(f"  Streamlit version: {st.__version__}")
        
        return True
        
    except Exception as e:
        print_error(f"UI components test failed: {str(e)}")
        return False

def test_app_integration():
    """Test if app.py has AI generator integration"""
    print_header("Testing App Integration")
    
    if not os.path.exists('app.py'):
        print_error("app.py not found")
        return False
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'ai_image_generator import': 'from ai_image_generator import' in content or 'import ai_image_generator' in content,
        'AI Image Generator menu': 'AI Image Generator' in content or 'Image Generator' in content,
        'render_image_generator_ui': 'render_image_generator_ui' in content
    }
    
    all_good = True
    for check, passed in checks.items():
        if passed:
            print_success(f"{check} found")
        else:
            print_warning(f"{check} not found - may need manual integration")
            all_good = False
    
    return all_good

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("  🧪 AI IMAGE GENERATOR - INTEGRATION TEST")
    print("="*60)
    
    results = {}
    
    # Run all tests
    results['Dependencies'] = test_dependencies()
    results['File Structure'] = test_file_structure()
    results['Module Imports'] = test_imports()
    results['API Configuration'] = test_secrets()
    results['UI Components'] = test_ui_components()
    results['App Integration'] = test_app_integration()
    
    # Optional: API connection test
    print("\n" + "-"*60)
    if input("Test API connection? (requires credits) [y/N]: ").lower() == 'y':
        results['API Connection'] = test_api_connection()
    else:
        print("⏭️  Skipping API connection test")
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test}")
    
    print("\n" + "-"*60)
    print(f"Results: {passed}/{total} tests passed")
    print("-"*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to deploy!")
        print("\nNext steps:")
        print("1. Commit and push to GitHub")
        print("2. Deploy to Streamlit Cloud")
        print("3. Add API keys to Streamlit Cloud secrets")
        print("4. Test in production")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before deploying.")
        print("\nRefer to:")
        print("- DEPLOYMENT_GUIDE.md for setup instructions")
        print("- QUICK_REFERENCE.md for troubleshooting")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        generate_test_report()
    except KeyboardInterrupt:
        print("\n\n⏸️  Testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)