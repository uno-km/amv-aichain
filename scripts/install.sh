#!/bin/bash
# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
# ==============================================================================
# amv-aichain One-Touch Zero-State Bootstrap Script for Android Termux
# ==============================================================================
# Usage:
#   curl -sSL https://raw.githubusercontent.com/uno-km/amv-aichain/main/scripts/install.sh | bash
# ==============================================================================

set -e

echo "=============================================================================="
echo "[BOOTSTRAP] amv-aichain One-Touch Sovereign Installation"
echo "=============================================================================="

# 1. Update Termux Packages and core toolchain
echo "[*] Step 1/3: Provisioning system packages and runtimes..."
if command -v pkg >/dev/null 2>&1; then
    pkg update -y
    pkg install -y python nodejs-lts termux-api ffmpeg git clang cmake libjpeg-turbo libpng
else
    echo "[*] Host OS environment detected. Proceeding with pip installation."
fi

# 2. Install amv-aichain (and optional ecosystem)
echo "[*] Step 2/3: Installing amv-aichain package..."
python3 -m pip install --upgrade amv-aichain

if [ "$1" == "--all" ] || [ "$1" == "all" ] || [ "$1" == "--ecosystem" ]; then
    echo "[*] Installing complete AMEVA Multimodal Ecosystem (bitnet, stt, diffusion, playwright, train, tts, vision)..."
    amv-aichain install --all
fi

# 3. Environment verification
echo "[*] Step 3/3: Running one-touch verification..."
amv-aichain setup

echo "=============================================================================="
echo "[OK] amv-aichain successfully installed and ready!"
echo "- Install Ecosystem    : amv-aichain install --all"
echo "- Install TTS Only     : amv-aichain install tts"
echo "- Install Vision Only  : amv-aichain install vision"
echo "- Pull model           : amv-aichain pull qwen-2.5-1.5b"
echo "- Start Web Dashboard  : amv-aichain serve --port 8080"
echo "- Documentation        : https://uno-km.vercel.app/lib/aichain/"
echo "=============================================================================="