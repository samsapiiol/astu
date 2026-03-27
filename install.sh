#!/bin/bash

# ===============================
#  ASTU INSTALLER (minimal)
# ===============================

echo "[*] Installing ASTU..."

# Check if astu file exists in current directory
if [[ ! -f "astu" ]]; then
    echo "❌ Error: 'astu' script not found in current directory."
    echo "Place your ASTU script in the same folder and run install.sh again."
    exit 1
fi

# Copy ASTU to /usr/local/bin
echo "[*] Copying astu to /usr/local/bin..."
sudo cp astu /usr/local/bin/astu

# Make it executable
echo "[*] Setting permissions..."
sudo chmod +x /usr/local/bin/astu

# Verify installation
if command -v astu >/dev/null 2>&1; then
    echo "✅ ASTU installed successfully!"
    echo "Run it using:  astu"
else
    echo "❌ Installation failed. ASTU not found in PATH."
fi
