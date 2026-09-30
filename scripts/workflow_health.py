from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

DEPRECATED = {
    "actions/checkout@v4": "actions/checkout@v5",
    "actions/setup-python@v5": "actions/setup-python@v6",
    "actions/setup-node@v4": "actions/setup-node@v5",
    "actions/upload-artifact@v4": "actions/upload-artifact@v6",
}

errors = []
checked = 0
for path in sorted(WORKFLOWS.glob("*.y*ml")):
    checked += 1
    text = path.read_text(encoding="utf-8", errors="replace")
    for old, replacement in DEPRECATED.items():
        if old in text:
            errors.append(f"{path.relative_to(ROOT)} uses deprecated {old}; use {replacement}")
    if "ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION" in text:
        errors.append(f"{path.relative_to(ROOT)} opts into an insecure deprecated Node runtime")
    for ref in re.findall(r"uses:\s*(actions/(?:checkout|setup-python|setup-node|upload-artifact)@v\d+)", text):
        if ref.endswith(("@v1", "@v2", "@v3")):
            errors.append(f"{path.relative_to(ROOT)} uses obsolete action {ref}")

if errors:
    for error in errors:
        print("FAIL", error)
    raise SystemExit(1)

print(f"PASS {checked} workflows use supported GitHub-hosted action runtimes")
