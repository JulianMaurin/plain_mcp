#!/bin/bash
# Plain.com MCP Server Installation Script

set -e

echo "🚀 Plain.com MCP Server Installation"
echo "===================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "📍 Python version: $python_version"

# Check if Python 3.9+ is available
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.9 or higher is required"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Plain.com API Configuration
PLAIN_API_KEY=your_plain_api_key_here

# Optional: Workspace ID (if required by your Plain.com setup)
PLAIN_WORKSPACE_ID=your_workspace_id_here
EOF
    echo "⚠️  Please edit .env file with your actual Plain.com API key"
fi

# Install the package in development mode
echo "🔧 Installing package in development mode..."
pip3 install -e .

# Run a simple test
echo "🧪 Testing installation..."
if python3 -c "from plain_mcp_server.server import PlainMCPServer; print('✅ Installation successful!')" 2>/dev/null; then
    echo "✅ Installation completed successfully!"
else
    echo "❌ Installation test failed"
    exit 1
fi

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Edit .env file with your Plain.com API key"
echo "2. Run the server: python -m plain_mcp_server.server"
echo "3. Configure your MCP client (see README.md)"
echo "4. Test with AI assistant prompts"
echo ""
echo "📚 For more information, see README.md"
