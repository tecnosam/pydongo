# Makefile for Python project CI/CD using uv + ci/ scripts

UV ?= uv

.PHONY: install lint format format-check typecheck test build clean \
        echo-version preview-version patch-pyproject \
        publish-testpypi publish-pypi tag bump-patch bump-minor bump-major

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

bump-patch:
	$(UV) run bump2version patch

bump-minor:
	$(UV) run bump2version minor

bump-major:
	$(UV) run bump2version major

echo-version:
	@$(UV) run python ci/python/echo_version.py

preview-version:
	@$(UV) run python ci/python/preview_version.py

patch-pyproject:
	@$(UV) run python ci/python/patch_pyproject.py

# require env:
#   BASE_REF: git ref to compare against (default: origin/<PR base> or origin/main)
#   REQUIRED_LEVEL: patch | minor | major (default: patch)
#   PACKAGE_DIRS: space-separated dirs that trigger a bump when changed (default: "src")

check-version-bump:
	@BASE_REF="$${BASE_REF:-origin/$${GITHUB_BASE_REF:-main}}"; \
	REQUIRED_LEVEL="$${REQUIRED_LEVEL:-patch}"; \
	PACKAGE_DIRS="$${PACKAGE_DIRS:-src}"; \
	echo "Checking version bump vs $$BASE_REF (required: $$REQUIRED_LEVEL)"; \
	$(UV) run python ci/python/check_version_bump.py --base-ref "$$BASE_REF" --require-level "$$REQUIRED_LEVEL" --package-dirs "$$PACKAGE_DIRS"

# --- Tagging ---

tag:
	@VERSION="$$( $(MAKE) -s echo-version )" bash ci/sh/tag.sh "$$VERSION"
