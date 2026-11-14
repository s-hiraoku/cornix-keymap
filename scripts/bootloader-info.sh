#!/usr/bin/env bash
# Read mounted UF2 bootloader information only; never copy firmware.
set -euo pipefail
shopt -s nullglob
found=0
for cornix_info in /Volumes/*/INFO_UF2.TXT; do
  [[ -f "$cornix_info" ]] || continue
  found=1
  printf '\n--- %s ---\n' "$cornix_info"
  cat "$cornix_info"
done
if [[ "$found" -eq 0 ]]; then
  printf '%s\n' 'UF2ドライブが見つかりません。片側をUSB接続し、リセットを2回押してから実行してください。' >&2
  exit 1
fi
