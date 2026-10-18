#!/usr/bin/env python3
"""Validate that campaign_plan.json conforms to the marketing-campaign output Schema.

Usage:
    python3 validate_campaign_plan.py <path to campaign_plan.json>

Exit codes: 0 = pass; 1 = validation failed; 2 = usage or file error
"""
import json
import sys

REQUIRED_STR_FIELDS = [
    "campaign_name",
    "brand",
    "objective",
    "target_audience",
    "positioning",
]
REQUIRED_LIST_FIELDS = [
    "insights",
    "channels",
    "budget_table",
    "timeline",
    "kpis",
    "risks",
    "next_steps",
]
REQUIRED_OBJ_FIELDS = ["copy_package", "visual_package", "images"]
NON_EMPTY_LIST_FIELDS = ["insights", "channels", "risks", "next_steps"]
REQUIRED_IMAGE_KEYS = ["hero", "channel_banner"]
BUDGET_SUM_TOLERANCE = 0.01


def validate(data):
    """Return a list of errors; an empty list means the plan passes."""
    errors = []

    if not isinstance(data, dict):
        return ["The root node must be a JSON object"]

    for field in REQUIRED_STR_FIELDS:
        if field not in data:
            errors.append("Missing required field: %s" % field)
        elif not isinstance(data[field], str):
            errors.append("Wrong type: %s should be a string" % field)
        elif not data[field].strip():
            errors.append("Field must not be empty: %s" % field)

    for field in REQUIRED_LIST_FIELDS:
        if field not in data:
            errors.append("Missing required field: %s" % field)
        elif not isinstance(data[field], list):
            errors.append("Wrong type: %s should be an array" % field)
        elif field in NON_EMPTY_LIST_FIELDS and len(data[field]) == 0:
            errors.append("Array must not be empty: %s" % field)

    for field in REQUIRED_OBJ_FIELDS:
        if field not in data:
            errors.append("Missing required field: %s" % field)
        elif not isinstance(data[field], dict):
            errors.append("Wrong type: %s should be an object" % field)

    budget = data.get("budget_table")
    if isinstance(budget, list) and budget:
        ratio_sum = 0.0
        for i, item in enumerate(budget, 1):
            if not isinstance(item, dict):
                errors.append("budget_table[%d] should be an object" % i)
                continue
            if "ratio" not in item:
                errors.append("budget_table[%d] is missing the ratio field" % i)
                continue
            ratio = item["ratio"]
            if not isinstance(ratio, (int, float)) or isinstance(ratio, bool):
                errors.append("budget_table[%d].ratio should be a number" % i)
                continue
            ratio_sum += float(ratio)
        if abs(ratio_sum - 1.0) > BUDGET_SUM_TOLERANCE:
            errors.append(
                "budget_table ratios should sum to 100%%, currently %.1f%%" % (ratio_sum * 100)
            )

    images = data.get("images")
    if isinstance(images, dict):
        for key in REQUIRED_IMAGE_KEYS:
            if key not in images:
                errors.append("images is missing the required key: %s" % key)
            elif not isinstance(images[key], str) or not images[key].strip():
                errors.append("images.%s should be a non-empty string (a path or an {{IMAGE:%s}} placeholder)" % (key, key))

    return errors


def main(argv):
    if len(argv) != 2:
        print("Usage: python3 validate_campaign_plan.py <path to campaign_plan.json>")
        return 2

    path = argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: file not found: %s" % path)
        return 2
    except json.JSONDecodeError as e:
        print("Error: not valid JSON: %s (line %d, column %d)" % (e.msg, e.lineno, e.colno))
        return 1
    except OSError as e:
        print("Error: cannot read file: %s" % e)
        return 2

    errors = validate(data)
    if errors:
        print("Validation failed, %d issue(s):" % len(errors))
        for err in errors:
            print("  - %s" % err)
        return 1

    print("Validation passed: %s conforms to the campaign_plan Schema" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
