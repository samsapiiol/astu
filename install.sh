#!/bin/bash
# ASTU INSTALLER v2.0
#
# Installs:
#   astu       -> /usr/local/bin/astu
#   astu-gui.py -> /usr/local/bin/astu-gui  (if present, and python3-tk is available)
#
# Also checks for the main dependencies and tells you what's missing,
# instead of failing silently later.

set -o pipefail

echo "[*] Installing ASTU..."

# Check if astu file exists in current directory
if [[ ! -f "astu" ]]; then
    echo "❌ Error: 'astu' script not found in current directory."
    echo "Place your ASTU script in the same folder and run install.sh again."
    exit 1
fi

# --- Dependency check (warn only, don't fail) ---
echo "[*] Checking dependencies..."
missing=()
for cmd in nmcli iw ip curl ping nmap tcpdump; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "  ✅ $cmd"
    else
        echo "  ⚠️  $cmd missing"
        missing+=("$cmd")
    fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
    echo ""
    echo "Some tools are missing: ${missing[*]}"
    echo "You can install most of them with:"
    echo "  sudo apt update && sudo apt install network-manager wireless-tools iproute2 curl iputils-ping nmap tcpdump"
    echo "Continuing anyway — run 'astu check' after install for the full list."
    echo ""
fi

# --- Install CLI ---
echo "[*] Copying astu to /usr/local/bin..."
sudo cp astu /usr/local/bin/astu
echo "[*] Setting permissions..."
sudo chmod +x /usr/local/bin/astu

# --- Install GUI (if present) ---
if [[ -f "astu-gui.py" ]]; then
    echo "[*] Found astu-gui.py, installing GUI..."
    if python3 -c "import tkinter" 2>/dev/null; then
        sudo cp astu-gui.py /usr/local/bin/astu-gui
        sudo chmod +x /usr/local/bin/astu-gui
        echo "  ✅ GUI installed as 'astu-gui'"
    else
        echo "  ⚠️  python3-tk is not installed, skipping GUI."
        echo "     Install it with: sudo apt install python3-tk"
        echo "     Then re-run this installer."
    fi
fi

# --- Verify installation ---
if command -v astu >/dev/null 2>&1; then
    echo "✅ ASTU installed successfully!"
    echo "Run it using:  astu help"
    echo "Or check tools: astu check"
    if command -v astu-gui >/dev/null 2>&1; then
        echo "GUI:           astu-gui   (or: python3 astu-gui.py)"
    fi
else
    echo "❌ Installation failed. ASTU not found in PATH."
    exit 1
fi
