#!/usr/bin/env bash
# update_knowledge_base.sh
# Pulls the latest pokemonAutoChess repo and regenerates the knowledge base.
# Usage: ./update_knowledge_base.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$SCRIPT_DIR/pokemonAutoChess"

echo "🔄 Updating pokemonAutoChess repo..."
if [ -d "$REPO_DIR" ]; then
    git -C "$REPO_DIR" pull --ff-only
else
    echo "❌ Repo not found at $REPO_DIR"
    echo "   Clone it first: git clone https://github.com/keldaanCommunity/pokemonAutoChess.git"
    exit 1
fi

echo ""
echo "🔄 Regenerating knowledge base..."
python3 "$SCRIPT_DIR/extract_game_data.py" \
    --repo-path "$REPO_DIR" \
    --output-path "$SCRIPT_DIR/pokebot/knowledge_base"

echo ""
echo "✅ Done! Restart the agent to pick up the new data."
