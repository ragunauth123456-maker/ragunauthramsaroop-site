#!/usr/bin/env bash
# Start Claude Code only after checking OpenRouter's public model catalog.
# Place OPENROUTER_API_KEY in GitHub Codespaces secrets, never in this repository.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="${CLAUDE_FREE_MODEL:-nvidia/nemotron-3-super-120b-a12b:free}"

case "$MODEL" in
  *:free) ;;
  *) echo "Refusing non-free model: $MODEL" >&2; exit 2 ;;
esac

if [[ "${1:-}" == "--check" ]]; then
  python3 "$SCRIPT_DIR/claude_free_preflight.py" "$MODEL"
  exit
fi

# A model override passed to Claude after this launcher would bypass the cost guard.
for arg in "$@"; do
  case "$arg" in
    --model|--model=*|-m)
      echo "Set CLAUDE_FREE_MODEL instead of overriding --model." >&2
      exit 2
      ;;
  esac
done

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "OPENROUTER_API_KEY is missing. Add it in GitHub Settings > Codespaces secrets." >&2
  exit 2
fi
if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code is not installed. Follow docs/claude-code-free.md." >&2
  exit 127
fi

# Reject missing, priced, unsupported, or unverifiable models before sending code.
python3 "$SCRIPT_DIR/claude_free_preflight.py" "$MODEL"

export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"
export ANTHROPIC_API_KEY=""
export ANTHROPIC_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_FABLE_MODEL="$MODEL"
export CLAUDE_CODE_SUBAGENT_MODEL="$MODEL"
export CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1

exec claude --model "$MODEL" "$@"
