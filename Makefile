REPO_DIR   := pokemonAutoChess
REPO_URL   := https://github.com/keldaanCommunity/pokemonAutoChess.git
KB_DIR     := pokebot/knowledge_base
PYTHON     := uv run python

.PHONY: help setup extract update api discord clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────────────────────

setup: $(REPO_DIR) install ## Clone repo + install dependencies
	@echo "✅ Setup complete"

$(REPO_DIR):
	git clone $(REPO_URL)

install: ## Install Python dependencies
	cd pokebot && uv sync

# ── Knowledge Base ────────────────────────────────────────────────────────────

extract: ## Extract game data → knowledge base (without git pull)
	$(PYTHON) extract_game_data.py --repo-path $(REPO_DIR) --output-path $(KB_DIR)
	$(PYTHON) extract_item_descriptions.py

update: ## Pull latest repo + regenerate knowledge base
	@echo "🔄 Pulling latest pokemonAutoChess..."
	git -C $(REPO_DIR) pull --ff-only
	@echo ""
	@$(MAKE) extract
	@echo ""
	@echo "✅ Knowledge base updated and enriched with descriptions."

coverage: ## Analyze knowledge base data coverage
	$(PYTHON) pokebot/scratch/coverage_analysis.py

compare: ## Compare bot meta vs math logic. Usage: make compare PKM=CROCALOR
	PYTHONPATH=./pokebot $(PYTHON) scratch/compare_logic.py $(PKM)

# ── Run ───────────────────────────────────────────────────────────────────────

api: ## Run the FastAPI server (port 8000)
	cd pokebot && $(PYTHON) -m app.main

discord: ## Run the Discord bot
	cd pokebot && $(PYTHON) -m app.discord.bot

chat: ## Run an interactive console chat (CLI)
	cd pokebot && $(PYTHON) -m app.cli

# ── Maintenance ───────────────────────────────────────────────────────────────

clean: ## Remove generated knowledge base files
	rm -f $(KB_DIR)/pokemon.json $(KB_DIR)/items.json $(KB_DIR)/synergies.json $(KB_DIR)/knowledge_base.json
	@echo "🗑  Knowledge base cleaned"
