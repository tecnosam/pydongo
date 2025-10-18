#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: tag.sh <version>"; exit 2
fi

TAG="v${VERSION}"
echo "Ensuring tag ${TAG} exists..."

if git ls-remote --exit-code --tags origin "refs/tags/${TAG}" >/dev/null 2>&1; then
  echo "Tag ${TAG} already exists."
  exit 0
fi

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git tag -a "${TAG}" -m "Release ${TAG}"
git push origin "${TAG}"
