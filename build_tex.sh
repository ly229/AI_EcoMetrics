#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_TEX="${ROOT_DIR}/src/AI_ecometrics.tex"
OUT_DIR="${ROOT_DIR}/build"

TECTONIC_BIN="${TECTONIC_BIN:-}"
if [[ -z "${TECTONIC_BIN}" ]]; then
  if [[ -x "${ROOT_DIR}/tectonic" ]]; then
    TECTONIC_BIN="${ROOT_DIR}/tectonic"
  else
    TECTONIC_BIN="$(command -v tectonic || true)"
  fi
fi

if [[ -z "${TECTONIC_BIN}" ]]; then
  echo "error: tectonic not found. Set TECTONIC_BIN or place ./tectonic in the repo root." >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

TECTONIC_ARGS=(--outdir "${OUT_DIR}")
if [[ "${TECTONIC_ONLY_CACHED:-1}" != "0" ]]; then
  TECTONIC_ARGS+=(--only-cached)
fi

if [[ -n "${TECTONIC_BUNDLE:-}" ]]; then
  TECTONIC_ARGS+=(--bundle "${TECTONIC_BUNDLE}")
fi

exec "${TECTONIC_BIN}" "${TECTONIC_ARGS[@]}" "${INPUT_TEX}" "$@"
