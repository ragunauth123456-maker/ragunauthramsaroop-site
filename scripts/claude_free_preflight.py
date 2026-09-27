#!/usr/bin/env python3
"""Public OpenRouter catalog check. No API key is read, printed, or transmitted."""
import json
import sys
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation

CATALOG_URL = "https://openrouter.ai/api/v1/models"


def validate_model(model_id, models):
    if not model_id.endswith(":free"):
        raise ValueError("Only explicit :free model IDs are allowed.")
    model = next((item for item in models if item.get("id") == model_id), None)
    if model is None:
        raise ValueError("Model is absent from OpenRouter's current public catalog.")
    pricing = model.get("pricing") or {}
    for field in ("prompt", "completion"):
        value = pricing.get(field)
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, TypeError):
            raise ValueError("Missing or invalid " + field + " price.") from None
        if not amount.is_finite() or amount != 0:
            raise ValueError(field + " pricing is not zero.")
    for field in ("request", "image"):
        if pricing.get(field) is not None:
            try:
                amount = Decimal(str(pricing[field]))
            except (InvalidOperation, TypeError):
                raise ValueError("Invalid " + field + " price.") from None
            if not amount.is_finite() or amount != 0:
                raise ValueError(field + " pricing is not zero.")
    parameters = model.get("supported_parameters")
    if isinstance(parameters, list) and "tools" not in parameters:
        raise ValueError("Model does not advertise tool support for Claude Code.")
    return model


def main():
    if len(sys.argv) != 2:
        print("Usage: claude_free_preflight.py provider/model:free", file=sys.stderr)
        return 2
    model_id = sys.argv[1]
    if not model_id.endswith(":free"):
        print("Refusing a model without an explicit :free suffix.", file=sys.stderr)
        return 2
    request = urllib.request.Request(
        CATALOG_URL, headers={"User-Agent": "claude-free-preflight/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            catalog = json.load(response)
        validate_model(model_id, catalog.get("data", []))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        print("Free-model verification failed; Claude Code was not started: " + str(exc), file=sys.stderr)
        return 1
    print("Verified zero-priced model with compatible advertised capabilities: " + model_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
