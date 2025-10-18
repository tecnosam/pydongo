# Makefile for Python project CI/CD using uv + ci/ scripts

UV ?= uv

.PHONY: install lint format format-check typecheck test build clean \
        echo-version preview-version patch-pyproject \
        publish-testpypi publish-pypi tag

install:
	$(UV) sync --dev

lint:
	$(UV) run ruff check src

format:
	$(UV) run ruff format src

format-check:
	$(UV) run ruff format --check src

typecheck:
	$(UV) run mypy src

test:
	$(UV) run pytest -q

build:
	$(UV) build

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache .venv .__preview_version__
	@find . -name "__pycache__" -type d -exec rm -rf {} +

# --- Versioning helpers ---

echo-version:
	@$(UV) run python ci/python/echo_version.py

preview-version:
	@$(UV) run python ci/python/preview_version.py

patch-pyproject:
	@$(UV) run python ci/python/patch_pyproject.py

# --- Tagging ---

tag:
	@VERSION="$$( $(MAKE) -s echo-version )" bash ci/sh/tag.sh "$$VERSION"
