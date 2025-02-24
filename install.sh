#!/bin/sh
# Using /bin/sh for maximum compatibility across different shells

# Print error message and exit
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Detect OS
detect_os() {
    if [ "$(uname)" = "Darwin" ]; then
        echo "macOS detected"
        # Check if Homebrew is installed (common Python package manager for macOS)
        if ! command -v brew >/dev/null 2>&1; then
            echo "Note: Homebrew not found. It's recommended for managing Python on macOS."
            echo "Visit https://brew.sh for installation instructions."
        fi
    elif [ "$(uname)" = "Linux" ]; then
        echo "Linux detected"
    else
        error_exit "Unsupported operating system"
    fi
}

# Check Python version
check_python() {
    if ! command -v python3 >/dev/null 2>&1; then
        error_exit "Python 3 not found. Please install Python 3.7 or higher"
    fi
    
    # Get Python version
    version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    echo "Python version $version found"
    
    # Compare versions (basic version check)
    if [ "$(echo "$version" | cut -d. -f1)" -lt 3 ] || 
       ([ "$(echo "$version" | cut -d. -f1)" -eq 3 ] && [ "$(echo "$version" | cut -d. -f2)" -lt 7 ]); then
        error_exit "Python 3.7 or higher is required"
    fi
}

# Check pip installation
check_pip() {
    if ! command -v pip3 >/dev/null 2>&1; then
        echo "pip3 not found. Attempting to install pip..."
        if [ "$(uname)" = "Darwin" ]; then
            # macOS pip install
            python3 -m ensurepip --upgrade || error_exit "Failed to install pip"
        else
            # Linux pip install
            if command -v apt-get >/dev/null 2>&1; then
                sudo apt-get update && sudo apt-get install -y python3-pip || error_exit "Failed to install pip"
            elif command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y python3-pip || error_exit "Failed to install pip"
            else
                error_exit "Could not install pip. Please install python3-pip manually."
            fi
        fi
    fi
}

# Main installation process
main() {
    echo "Starting NetConMon installation..."
    
    # Detect operating system
    detect_os
    
    # Check Python installation
    check_python
    
    # Check pip installation
    check_pip
    
    # Install Python requirements
    echo "Installing required Python packages..."
    pip3 install -r requirements.txt || error_exit "Failed to install required packages"
    
    # Check if the script is run with sudo/root on Linux
    if [ "$(uname)" = "Linux" ]; then
        if [ "$(id -u)" -ne 0 ]; then
            echo "Warning: NetConMon requires root privileges to monitor network connections."
            echo "Please run the program with sudo when using it."
        fi
    fi
    
    echo "\nInstallation completed successfully!"
    echo "\nTo run NetConMon:"
    if [ "$(uname)" = "Darwin" ]; then
        echo "Open Terminal and run: sudo python3 netconmongui.py"
    else
        echo "Open terminal and run: sudo python3 netconmongui.py"
    fi
}

# Run main installation
main