#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source "$repo_root/versions.env"
source_dir=${1:?Usage: build.sh SOURCE_DIR OUTPUT_DIR}
output_dir=${2:?Usage: build.sh SOURCE_DIR OUTPUT_DIR}
image=${IMAGE:-godot-dotnet-web-templates-builder:4.7.2-net10}

"$repo_root/scripts/validate-source.sh" "$source_dir"
mkdir -p "$output_dir"
source_dir=$(cd -- "$source_dir" && pwd)
output_dir=$(cd -- "$output_dir" && pwd)
docker build --platform linux/amd64 --tag "$image" "$repo_root"
docker run --rm --platform linux/amd64 \
  --volume "$source_dir:/godot" \
  --volume "$repo_root:/workspace:ro" \
  --volume "$output_dir:/output" \
  --env JOBS="${JOBS:-8}" \
  --env RELEASE_TAG="$RELEASE_TAG" \
  "$image" /workspace/scripts/build-in-container.sh
