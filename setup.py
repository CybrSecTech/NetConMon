import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)

def install_requirements():
    """Install required Python packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Successfully installed Python dependencies")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def check_tkinter():
    """Check if Tkinter is properly installed"""
    try:
        import tkinter
        print("Tkinter is properly installed")
    except ImportError:
        print("Tkinter is not installed. Installing tkinter...")
        if sys.platform.startswith('linux'):
            # For Debian/Ubuntu
            try:
                subprocess.check_call(["sudo", "apt-get", "install", "python3-tk"])
            except:
                # For RHEL/CentOS/Fedora
                try:
                    subprocess.check_call(["sudo", "dnf", "install", "python3-tkinter"])
                except:
                    print("Could not install tkinter. Please install it manually:")
                    print("Debian/Ubuntu: sudo apt-get install python3-tk")
                    print("RHEL/CentOS/Fedora: sudo dnf install python3-tkinter")
                    sys.exit(1)
        elif sys.platform.startswith('darwin'):
            print("On macOS, tkinter should be included with Python.")
            print("If it's missing, try reinstalling Python from python.org")
            sys.exit(1)
        elif sys.platform.startswith('win'):
            print("On Windows, tkinter should be included with Python.")
            print("If it's missing, try reinstalling Python and check 'tcl/tk and IDLE' during installation")
            sys.exit(1)

def create_directories():
    """Create necessary directories"""
    try:
        # Create backups directory
        Path('backups').mkdir(exist_ok=True)
        print("Created backups directory")
    except Exception as e:
        print(f"Error creating directories: {e}")
        sys.exit(1)

def check_permissions():
    """Check if the script has necessary permissions"""
    if sys.platform.startswith('win'):
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Warning: This program requires administrator privileges to monitor network connections")
            print("Please run the program as administrator when using it")
    else:
        if os.geteuid() != 0:
            print("Warning: This program requires root privileges to monitor network connections")
            print("Please run the program with sudo when using it")

def main():
    print("Starting installation process...")
    
    # Check Python version
    check_python_version()
    
    # Install required packages
    install_requirements()
    
    # Check Tkinter installation
    check_tkinter()
    
    # Create necessary directories
    create_directories()
    
    # Check permissions
    check_permissions()
    
    print("\nInstallation completed successfully!")
    print("\nTo run the program:")
    if sys.platform.startswith('win'):
        print("1. Right-click on netconmongui.py and select 'Run as administrator'")
    else:
        print("1. Open terminal in the program directory")
        print("2. Run: sudo python3 netconmongui.py")

if __name__ == "__main__":
    main()
