#!/usr/bin/env python3
"""校验 campaign_plan.json 是否符合 marketing-campaign 输出 Schema。

用法:
    python3 validate_campaign_plan.py <campaign_plan.json 路径>

退出码: 0 = 通过; 1 = 校验失败; 2 = 用法或文件错误
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
    """返回错误列表；空列表表示通过。"""
    errors = []

    if not isinstance(data, dict):
        return ["根节点必须是 JSON object"]

    for field in REQUIRED_STR_FIELDS:
        if field not in data:
            errors.append("缺少必需字段: %s" % field)
        elif not isinstance(data[field], str):
            errors.append("字段类型错误: %s 应为 string" % field)
        elif not data[field].strip():
            errors.append("字段不能为空: %s" % field)

    for field in REQUIRED_LIST_FIELDS:
        if field not in data:
            errors.append("缺少必需字段: %s" % field)
        elif not isinstance(data[field], list):
            errors.append("字段类型错误: %s 应为 array" % field)
        elif field in NON_EMPTY_LIST_FIELDS and len(data[field]) == 0:
            errors.append("数组不能为空: %s" % field)

    for field in REQUIRED_OBJ_FIELDS:
        if field not in data:
            errors.append("缺少必需字段: %s" % field)
        elif not isinstance(data[field], dict):
            errors.append("字段类型错误: %s 应为 object" % field)

    budget = data.get("budget_table")
    if isinstance(budget, list) and budget:
        ratio_sum = 0.0
        for i, item in enumerate(budget, 1):
            if not isinstance(item, dict):
                errors.append("budget_table[%d] 应为 object" % i)
                continue
            if "ratio" not in item:
                errors.append("budget_table[%d] 缺少 ratio 字段" % i)
                continue
            ratio = item["ratio"]
            if not isinstance(ratio, (int, float)) or isinstance(ratio, bool):
                errors.append("budget_table[%d].ratio 应为数字" % i)
                continue
            ratio_sum += float(ratio)
        if abs(ratio_sum - 1.0) > BUDGET_SUM_TOLERANCE:
            errors.append(
                "budget_table 占比合计应为 100%%, 当前为 %.1f%%" % (ratio_sum * 100)
            )

    images = data.get("images")
    if isinstance(images, dict):
        for key in REQUIRED_IMAGE_KEYS:
            if key not in images:
                errors.append("images 缺少必需键: %s" % key)
            elif not isinstance(images[key], str) or not images[key].strip():
                errors.append("images.%s 应为非空字符串（路径或 {{IMAGE:%s}} 占位）" % (key, key))

    return errors


def main(argv):
    if len(argv) != 2:
        print("用法: python3 validate_campaign_plan.py <campaign_plan.json 路径>")
        return 2

    path = argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("失败: 文件不存在: %s" % path)
        return 2
    except json.JSONDecodeError as e:
        print("失败: 不是合法 JSON: %s (行 %d 列 %d)" % (e.msg, e.lineno, e.colno))
        return 1
    except OSError as e:
        print("失败: 无法读取文件: %s" % e)
        return 2

    errors = validate(data)
    if errors:
        print("校验失败, 共 %d 个问题:" % len(errors))
        for err in errors:
            print("  - %s" % err)
        return 1

    print("校验通过: %s 符合 campaign_plan Schema" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
