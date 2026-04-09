
run-api:
	uv run python -m src.main

run-cli:
	uv run python -m src.cli

eval-router:
	npx promptfoo eval -c promptfoo/router.yaml

eval-view:
	npx promptfoo view
