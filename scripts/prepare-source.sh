#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source "$repo_root/versions.env"
source_dir=${1:?Usage: prepare-source.sh SOURCE_DIR}

if [[ -e "$source_dir" ]]; then
  printf 'Source directory already exists: %s\n' "$source_dir" >&2
  exit 1
fi

git init "$source_dir"
git -C "$source_dir" remote add upstream https://github.com/godotengine/godot.git
git -C "$source_dir" fetch --depth=1 upstream "$GODOT_COMMIT" "$DRAFT_COMMIT"
git -C "$source_dir" cat-file -e "$DRAFT_COMMIT^{commit}"
git -C "$source_dir" checkout --detach "$GODOT_COMMIT"
git -C "$source_dir" apply "$repo_root/patches/official-draft-forward-port.patch"
git -C "$source_dir" apply "$repo_root/patches/net10.patch"
git -C "$source_dir" apply "$repo_root/patches/threads.patch"

cat > "$source_dir/.godot-dotnet-web-source" <<EOF
godot_repository=https://github.com/godotengine/godot.git
godot_commit=$GODOT_COMMIT
draft_pull_request=https://github.com/godotengine/godot/pull/$DRAFT_PR
draft_commit=$DRAFT_COMMIT
target_framework=net10.0
thread_support=true
EOF

"$repo_root/scripts/validate-source.sh" "$source_dir"
