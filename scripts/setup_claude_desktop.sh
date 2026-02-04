#!/bin/bash
# Setup script for 108 MCP servers in Claude Desktop

set -e

# Get the absolute path of the 108-core directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔮 Setting up 108 MCP servers for Claude Desktop"
echo "================================================"
echo "Project root: $PROJECT_ROOT"

# Detect OS and set config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    CONFIG_DIR="$APPDATA/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "Please manually configure your Claude Desktop settings"
    exit 1
fi

echo "Config location: $CONFIG_FILE"

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

# Backup existing config if present
if [ -f "$CONFIG_FILE" ]; then
    BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📦 Backing up existing config to: $BACKUP_FILE"
    cp "$CONFIG_FILE" "$BACKUP_FILE"
fi

# Generate the new config with correct paths
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "108-ephemeris": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "$PROJECT_ROOT",
        "python",
        "services/mcp/ephemeris_server.py"
      ],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT"
      }
    },
    "108-patterns": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "$PROJECT_ROOT",
        "python",
        "services/mcp/patterns_server.py"
      ],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT"
      }
    },
    "108-context": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "$PROJECT_ROOT",
        "python",
        "services/mcp/context_server.py"
      ],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT"
      }
    },
    "108-knowledge": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "$PROJECT_ROOT",
        "python",
        "services/mcp/knowledge_server.py"
      ],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT"
      }
    }
  }
}
EOF

echo ""
echo "✅ Configuration written to: $CONFIG_FILE"
echo ""
echo "🔄 Please restart Claude Desktop to load the new MCP servers"
echo ""
echo "After restart, you'll have access to these tools:"
echo "  📊 108-ephemeris  - Planetary positions, houses, nakshatras"
echo "  🔮 108-patterns   - Yoga detection, dosha analysis, strength"
echo "  ⏱️  108-context    - Dasha periods, transits, timing"
echo "  📚 108-knowledge  - Planet/nakshatra/rashi lookups"
