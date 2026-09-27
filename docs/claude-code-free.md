# Claude Code with zero-priced OpenRouter models

This repository supports a manual Claude Code session in a GitHub Codespace. The installer and launcher do not start background workers, publish changes, or require a paid Anthropic account.

## One-time authorization

1. Open https://openrouter.ai/keys and create a free OpenRouter API key. Do not paste the key into an issue, PR, chat, tracked file, or workflow log.
2. Open https://github.com/settings/codespaces and create a personal Codespaces secret named `OPENROUTER_API_KEY`. Select both `ragunauth123456-maker/PrismBay` and `ragunauth123456-maker/ragunauthramsaroop-site` as authorized repositories. Restart any existing Codespace to receive the new secret.
3. Open this repository on GitHub and select **Code > Codespaces > Create codespace** for the branch containing this setup. Codespaces usage has an included monthly allowance for eligible personal accounts. Set a zero spending limit if you want to avoid overruns.
4. In the Codespaces terminal, install the official Claude Code CLI: `curl -fsSL https://claude.ai/install.sh | bash`. Restart the terminal if `claude` is not found.
5. Run `bash scripts/claude-free.sh --check`. This fetches the public model catalog, checks the selected model ID, zero input/output/request prices and tool support, and refuses to run if verification fails.
6. Run `bash scripts/claude-free.sh`. For read-only triage, ask the model to read `AGENTS.md` and report findings. Review all proposed file edits before accepting them. Create a branch and PR for code changes.

## Default model and free-only safeguards

Default: `nvidia/nemotron-3-super-120b-a12b:free`, a free OpenRouter model with advertised tool calling. To select a different current free model use `export CLAUDE_FREE_MODEL='provider/model:free'`, then rerun the preflight.
The launcher selects OpenRouter's Anthropic-compatible endpoint `https://openrouter.ai/api`, explicitly blanks `ANTHROPIC_API_KEY`, and sets all standard Claude Code task-model aliases to the validated free ID. It refuses direct `--model` overrides. A failed catalog lookup stops launch instead of silently switching to a paid model.
Free non-Anthropic models are **experimental** in Claude Code. Tool handling, prompts, context and agent loops are not guaranteed to match genuine Claude models. The default free OpenRouter tier currently has a 50-request-per-day limit. Longer agent tasks will exhaust the limit.

## Review and tests

Run `bash -n scripts/claude-free.sh` and `python3 -m unittest discover -s scripts -p 'test_claude_free_preflight.py'` for offline tests. Use `bash scripts/claude-free.sh --check` for the live public catalog check. Inside Claude Code, use `/status` and confirm `ANTHROPIC_AUTH_TOKEN` and the OpenRouter base URL. Verify model requests in https://openrouter.ai/activity .

Do not submit employer, banking, customer, supplier, private recruitment, or other confidential content to public free-model providers. The Codespaces secret is available inside the selected development environment, not stored in Git.

Sources: https://openrouter.ai/docs/guides/coding-agents/claude-code-integration , https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b:free , https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces .
