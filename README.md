# marketing-campaign

[English](#english) · [中文](#中文)

本仓库包含同一技能的两个语言版本，内容等价、各自独立安装：
This repo ships two language versions of the same skill — equivalent content, installed independently:

| 版本 / Version | Skill 名称 | 目录 | 触发语言 |
|---|---|---|---|
| English | `marketing-campaign-en` | `skills/marketing-campaign-en/` | English requests |
| 中文 | `marketing-campaign-zh` | `skills/marketing-campaign-zh/` | 中文请求 |

## 安装 / Install

```bash
# 两个版本都装（默认行为）/ Install both (default)
npx -y skills add huaxinzhou2008/marketing-campaign -g --all

# 只装英文版 / English only
npx -y skills add huaxinzhou2008/marketing-campaign -g -s marketing-campaign-en

# 只装中文版 / Chinese only
npx -y skills add huaxinzhou2008/marketing-campaign -g -s marketing-campaign-zh
```

两个版本都装也不会互相覆盖：技能名称不同（`-en` / `-zh`），按请求语言自动匹配对应版本。
Installing both is safe — the skill names differ (`-en` / `-zh`), so each request language matches its own version.

---

<a id="english"></a>

## English

### What problem it solves

- Sequential campaign generation where research, copy, and visuals wait on each other, with no quality gate;
- Workflow logic coupled to tools, so swapping a tool means rewriting the flow;
- Models typesetting Word directly, so styles drift across environments;
- Image generation without a confirmation step, so prompts go off-target and quota is wasted.

### How it works

| Phase | Action |
|---|---|
| Phase 0 | Collect and validate the brief; ask before doing when key info is missing |
| Phase 1 | Initialize the shared `campaign_state.json` |
| Phase 2 | Launch Researcher / Writer / Image Designer sub-agents in parallel |
| Phase 3 | Route dependency requests (collab_request) |
| Phase 4 | Marketing manager review; failing work is bounced back, capped at 3 revision rounds |
| Phase 5 | Merge into `campaign_plan.json` and run schema validation |
| Phase 6 | Render Word from the brand template |
| Phase 7 | Images start as prompts and asset lists; generate only after confirmation |
| Phase 8 | Deliver Word + JSON + process notes |

Core invariants: the workflow never lives inside a tool; parallelism is controlled by the orchestrator; bidirectional communication flows only through shared state; Word can only be rendered from structured JSON; revision rounds are hard-capped at 3.

### Usage

After installing, start like this:

> Use $marketing-campaign-en to turn my marketing brief into a deliverable Word campaign plan.

A brief must include at least: product/service, campaign goal, target audience, and budget or timeline; brand guidelines are optional. For structure, see `skills/marketing-campaign-en/assets/brief.example.json`.

### Repository structure

```text
skills/
├── marketing-campaign-en/          English version
│   ├── SKILL.md                    Main entry: workflow, red lines, stopping conditions
│   ├── agents/openai.yaml          UI metadata
│   ├── references/
│   │   ├── campaign-state.md       Shared state, collaboration messages, state machine, review checklist
│   │   ├── output-schema.md        campaign_plan.json field spec
│   │   └── docx-rendering.md       Word template and rendering flow
│   ├── scripts/
│   │   └── validate_campaign_plan.py  Mandatory schema validator before rendering
│   └── assets/
│       └── brief.example.json      Reference structure for brief follow-up questions
└── marketing-campaign-zh/          中文版（内容与英文版等价）
    ├── SKILL.md                    主入口：流程、红线、停止条件
    ├── agents/openai.yaml          UI 元数据
    ├── references/
    │   ├── campaign-state.md       共享状态、协作消息、状态机、评审清单
    │   ├── output-schema.md        campaign_plan.json 字段规范
    │   └── docx-rendering.md       Word 模板与渲染流程
    ├── scripts/
    │   └── validate_campaign_plan.py  渲染前 schema 强制校验器
    └── assets/
        └── brief.example.json      brief 补问结构参考
```

### Runtime requirements

- A client that supports Agent Skills (e.g. WorkBuddy)
- Python 3 (to run `scripts/validate_campaign_plan.py`)

### Boundaries

Not handled: single-paragraph copy rewriting and polishing, pure typesetting beautification of existing plans, non-marketing documents (research reports, papers, contracts, etc.).

### Privacy and permissions

- This repo publishes only the files needed to run the Skill — no local eval samples, expected answers, or run logs;
- Search, CRM, and publishing tools require user authorization before use;
- Image prompts and asset lists must be confirmed by the user before any image is generated.

---

<a id="中文"></a>

## 中文

### 它解决什么问题

- 营销方案单线顺序生成，研究、文案、视觉互相等待，质量不可控；
- 工作流与工具耦合，换一个工具就要改一套流程；
- 模型直接排版 Word，不同环境样式漂移；
- 图像生成缺少确认环节，提示词跑偏浪费配额。

### 工作方式

| 阶段 | 动作 |
|---|---|
| Phase 0 | Brief 收集与校验，关键信息缺失先问再做 |
| Phase 1 | 初始化共享 `campaign_state.json` |
| Phase 2 | 并行启动 Researcher / Writer / Image Designer 三个子 Agent |
| Phase 3 | 依赖请求（collab_request）路由 |
| Phase 4 | 营销经理评审，不通过退回，修订上限 3 轮 |
| Phase 5 | 合并为 `campaign_plan.json` 并过 schema 校验 |
| Phase 6 | 按品牌模板渲染 Word |
| Phase 7 | 图像先出提示词与素材清单，确认后才生成 |
| Phase 8 | 交付 Word + JSON + 过程说明 |

核心不变量：工作流不写进工具；并行由编排者控制；双向交流只经共享状态；Word 只能由结构化 JSON 渲染；修订轮次硬上限 3。

### 使用

安装后，可以这样开始：

> 使用 $marketing-campaign-zh 把我给出的营销 brief 做成可交付的 Word 活动方案。

Brief 至少包含：产品/服务、活动目标、目标受众、预算或周期；品牌规范可选。结构参考 `skills/marketing-campaign-zh/assets/brief.example.json`。

### 仓库结构

见上方 [English 小节](#english) 的仓库结构树：`skills/marketing-campaign-en/` 为英文版，`skills/marketing-campaign-zh/` 为中文版，两版文件一一对应。

### 运行依赖

- 支持 Agent Skills 的客户端（如 WorkBuddy）
- Python 3（运行 `scripts/validate_campaign_plan.py`）

### 边界

不处理：单段文案改写与润色、已有方案的纯排版美化、非营销类文档（研报、论文、合同等）。

### 隐私与权限

- 本仓库只发布运行 Skill 所需文件，不含本地评测样本、预期答案与运行记录；
- 搜索、CRM、发布类外部工具需用户授权后使用；
- 图像生成前必须经用户确认提示词与素材清单。
