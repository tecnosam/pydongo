#!/bin/bash
set -e

echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ ./*.egg-info

echo "🏗️  Building package..."
uv build

echo "✅ Checking built package with twine..."
uv run twine check dist/*

echo "📦 Testing wheel installation..."
WHEEL=$(ls dist/*.whl)
uv run --isolated --with "$WHEEL" python -c "
import pydongo
print(f'✅ Successfully imported pydongo version {pydongo.__version__}')
"

echo "📦 Testing source distribution installation..."
SDIST=$(ls dist/*.tar.gz)
uv run --isolated --with "$SDIST" python -c "
import pydongo
print(f'✅ Successfully imported pydongo from sdist')
"

echo "🎉 All build tests passed!"
