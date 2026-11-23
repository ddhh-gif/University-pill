#!/usr/bin/env bash
# md2docx.sh — Convert .md to .docx with math + images preserved via pandoc
# Usage: ./md2docx.sh <input.md> [output.docx]
#        Drop an .md file onto this script from file manager

set -e

PANDOC="/home/zihan/miniconda3/envs/darkenpdf/bin/pandoc"

if [ -z "$1" ]; then
    echo "Usage: md2docx <input.md> [output.docx]"
    exit 1
fi

INPUT="$(realpath "$1")"
INPUT_DIR="$(dirname "$INPUT")"
INPUT_NAME="$(basename "$INPUT")"
OUTPUT="$(realpath "${2:-${INPUT%.md}.docx}")"

cd "$INPUT_DIR"

"$PANDOC" "$INPUT_NAME" \
    --from=markdown+tex_math_dollars+tex_math_single_backslash \
    --to=docx \
    --output="$OUTPUT" \
    --standalone \
    --resource-path=.

echo "Done: $OUTPUT"
