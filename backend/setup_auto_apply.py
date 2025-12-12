"""
Quick Setup Script for Intelligent Auto-Apply Agent
Run this to install all dependencies and verify setup
"""
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(result.stdout[:500])  # Print first 500 chars
        else:
            print(f"❌ {description} - FAILED")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   🤖 Intelligent Auto-Apply Agent - Setup Script 🤖     ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    steps = [
        ("pip install selenium", "Installing Selenium"),
        ("pip install webdriver-manager", "Installing WebDriver Manager"),
        ("python -c \"from selenium import webdriver; print('Selenium OK')\"", "Verifying Selenium"),
        ("python -c \"from webdriver_manager.chrome import ChromeDriverManager; print('WebDriver Manager OK')\"", "Verifying WebDriver Manager"),
    ]
    
    results = []
    for cmd, desc in steps:
        success = run_command(cmd, desc)
        results.append((desc, success))
    
    print(f"\n{'='*60}")
    print("📊 SETUP SUMMARY")
    print(f"{'='*60}")
    
    all_success = True
    for desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {desc}")
        if not success:
            all_success = False
    
    print(f"\n{'='*60}")
    if all_success:
        print("🎉 ALL CHECKS PASSED! You're ready to use the Intelligent Auto-Apply Agent!")
        print("\n📖 Next Steps:")
        print("1. Read INTELLIGENT_AUTO_APPLY_GUIDE.md for usage instructions")
        print("2. Update AutoApplyButton.tsx: set use_real_automation to true")
        print("3. Restart the backend server")
        print("4. Test with a real job URL!")
    else:
        print("⚠️  SOME CHECKS FAILED. Please fix the errors above.")
        print("\n🔧 Troubleshooting:")
        print("- Make sure you're in the backend directory")
        print("- Try: pip install --upgrade selenium webdriver-manager")
        print("- Check if Chrome browser is installed")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
