#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source "$repo_root/versions.env"
source_dir=${1:?Usage: validate-source.sh SOURCE_DIR}

if [[ $(git -C "$source_dir" rev-parse HEAD) != "$GODOT_COMMIT" ]]; then
  printf 'Godot source HEAD does not match %s.\n' "$GODOT_COMMIT" >&2
  exit 1
fi

index_file=$(mktemp "${TMPDIR:-/tmp}/godot-dotnet-web-index.XXXXXX")
trap 'rm -f "$index_file"' EXIT
cp "$(git -C "$source_dir" rev-parse --path-format=absolute --git-path index)" "$index_file"
GIT_INDEX_FILE="$index_file" git -C "$source_dir" add -A
GIT_INDEX_FILE="$index_file" git -C "$source_dir" rm --cached --quiet .godot-dotnet-web-source
actual_tree=$(GIT_INDEX_FILE="$index_file" git -C "$source_dir" write-tree)

if [[ "$actual_tree" != "$PATCHED_TREE" ]]; then
  printf 'Patched tree mismatch.\nExpected: %s\nActual:   %s\n' "$PATCHED_TREE" "$actual_tree" >&2
  exit 1
fi

git -C "$source_dir" diff --check

