#!/bin/bash
# Installation script for AI Context CLI Tool

set -e

echo "Installing AI Context CLI Tool..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
python3 -m pip install --user -r requirements.txt

# Install the tool
echo "Installing aicontext CLI tool..."
python3 -m pip install --user -e .

echo "Installation complete!"
echo ""
echo "Usage examples:"
echo "  aicontext --list-commands     # See available commands"
echo "  aicontext architecture        # Show architecture section"
echo "  aicontext --full             # Show all context"
echo "  aicontext --help             # Show help"
echo ""
echo "The tool will automatically discover commands from .aicontext files in your project."