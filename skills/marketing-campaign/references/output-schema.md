# campaign_plan.json：最终输出 Schema

营销经理（主 Agent）合并三段交付物后产出的唯一结构化方案，也是 Word 渲染的唯一内容源。

## Schema

```json
{
  "campaign_name": "",
  "brand": "",
  "objective": "",
  "target_audience": "",
  "insights": [],
  "positioning": "",
  "channels": [],
  "copy_package": {},
  "visual_package": {},
  "budget_table": [],
  "timeline": [],
  "kpis": [],
  "risks": [],
  "next_steps": [],
  "images": {
    "hero": "path/to/hero.png",
    "channel_banner": "path/to/banner.png"
  }
}
```

## 字段说明

| 字段 | 类型 | 要求 |
|---|---|---|
| `campaign_name` | string | 活动名称，不超过 20 字 |
| `brand` | string | 品牌名；无品牌时填"未指定" |
| `objective` | string | 活动目标，一句话 |
| `target_audience` | string | 目标受众描述 |
| `insights` | array\<string\> | 关键洞察，3–7 条；来自 research_summary |
| `positioning` | string | 定位声明，一句话 |
| `channels` | array\<string\> | 投放渠道列表 |
| `copy_package` | object | 文案包：主文案、渠道变体、CTA、内容日历 |
| `visual_package` | object | 视觉包：方向列表、提示词、素材清单 |
| `budget_table` | array\<object\> | 预算表：项目、金额、占比；合计须等于 100% |
| `timeline` | array\<object\> | 时间表：阶段、起止、负责角色 |
| `kpis` | array\<object\> | KPI：指标、目标值、衡量方式 |
| `risks` | array\<string\> | 风险与对策，2–5 条 |
| `next_steps` | array\<string\> | 下一步行动，可执行 |
| `images` | object | 图片路径映射；未生成真实图片时保留 `{{IMAGE:hero}}` 形式的占位字符串 |

## 校验

合并完成后必须运行：

```bash
python3 scripts/validate_campaign_plan.py <campaign_plan.json 路径>
```

校验项：必需字段齐全、类型正确、`insights`/`channels`/`risks`/`next_steps` 非空、`budget_table` 占比合计约 100%、`images` 含 `hero` 与 `channel_banner` 两个键。

校验不通过时按报错修补，禁止跳过校验直接渲染 Word。
