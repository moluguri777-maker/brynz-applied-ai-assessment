"""Unified output contract helpers."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "output.schema.json"

def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

def validate_output(data):
    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [{"path": ".".join(map(str, e.path)), "message": e.message} for e in errors]

def require_valid_output(data):
    errors = validate_output(data)
    if errors:
        raise ValueError("Unified output schema validation failed: " + json.dumps(errors))
    return True
