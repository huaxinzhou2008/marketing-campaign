---
name: marketing-campaign
description: 营销活动（campaign）全流程方案生成：从 brief 出发，按多 Agent 架构并行推进研究、文案、视觉三条线，经营销经理评审退回后输出结构化 JSON，并按品牌模板渲染 Word 文档。当用户要求制定营销活动方案、新品上市或推广方案时使用；不处理单段文案改写和纯排版美化。
---

# 营销活动方案多 Agent 工作流

## 任务与产出

把用户的营销 brief 转化为可交付的品牌 Word 活动方案。固定产出三件：

1. `campaign_plan.json`：通过 schema 校验的结构化方案，是唯一允许进入 Word 的内容源；
2. Word 方案文档：封面、目录、品牌页眉页脚、图片占位、表格齐整；
3. 过程产物：`campaign_state.json` 与协作日志（留痕审计用）。

## 角色与工具映射

原架构面向 OpenAI Agents SDK，落到 WorkBuddy 时按下表对应，行为契约不变：

| 原架构角色 | 本环境承担者 | 说明 |
|---|---|---|
| Marketing Manager（编排 + 评审） | 主 Agent | 拆解 brief、派活、路由依赖请求、评审合并；不亲自写三段交付物 |
| Researcher / Writer / Image Designer | 子 Agent（Agent 工具并行调用） | 一条消息内并行 spawn，各自只写自己的交付文件 |
| 共享 campaign_state | 工作目录 `campaign_state.json` | 所有角色读写同一文件，不靠对话传话 |
| 协作消息队列 | state 内 `messages[]` + 日志文件 | collab_request 全部落盘 |
| MCP Server（web-search / crm / brand / knowledge / image-gen / docx-export） | 现有工具与技能 | WebSearch、知识库、ImageGen、tencent-docx 等；不要求自建 MCP Server，但保持"一个 Server 一类能力、每个 5–15 个工具"的边界 |
| mcp-docx-export | tencent-docx 技能 | 先过 tencent-docs-routing 再生成；模板要求见 references/docx-rendering.md |

## 核心不变量（红线，违反即失败）

1. 工作流不写进工具；工具只连接外部能力。
2. 并行由编排者控制；子 Agent 之间不直接互相调用，避免循环。
3. 双向交流只经共享 campaign_state 与协作消息，不经模型私下传话。
4. Word 只能由结构化 JSON 渲染，模型不直接自由排版。
5. 修订轮次上限 3（`max_revision_rounds`），到顶必须停止重试。
6. 图像先出"提示词 + 素材清单"，用户确认后才真正生成；未确认保留 `{{IMAGE:xxx}}` 占位。
7. 搜索、CRM、发布类外部工具需用户授权后才用。

## 工作流程

### Phase 0 · Brief 收集与校验

检查 brief 是否包含：产品/服务、活动目标、目标受众、预算或周期、品牌规范（可选）。缺失关键信息（前四项）时先问用户再开工，不要假设。用户只说一句话时，按 assets/brief.example.json 的结构补问。

### Phase 1 · 初始化共享状态

建工作目录，写入 `campaign_state.json`（schema 见 references/campaign-state.md），`status` 置 `researching`，`revision_round` 置 0。把 brief 原文存入 `brief` 字段。

### Phase 2 · 并行启动三个子 Agent

在一条消息里并行调用 Agent 工具 spawn 三个子 Agent，提示词各自自含（目标、输入文件路径、输出文件路径、输出格式、禁止事项）：

- **Researcher** → `research_summary.md`：行业、竞品、用户、渠道研究；结论标注来源或"假设"；可用 WebSearch 等工具。
- **Writer** → `copy_package.md`：定位、卖点、文案、内容日历、CTA；遵循品牌规范。
- **Image Designer** → `visual_package.md`：视觉方向（≥3）、素材清单、图片提示词；不调用生图工具，只交付提示词。

三者都只写文件不回传长文；主 Agent 读文件后把结果路径登记进 campaign_state。

### Phase 3 · 依赖请求路由

检查各子 Agent 产出的 `open_questions` 与 `messages[]` 里的 collab_request（如 Writer 向 Image Designer 要主视觉风格）。由主 Agent（Manager）判断：能等的等 Researcher 补数据；不能等的让 Writer / Designer 先出初版。路由结果写入 `messages[]`，`status` 转 `reviewing`。

### Phase 4 · 评审与退回

主 Agent 按评审清单逐项检查（清单见 references/campaign-state.md）：

- 不通过 → `status` 置 `revising`，`revision_round + 1`，只把问题最小的子任务退回对应角色，其余成果保留；
- `revision_round` 达到 `max_revision_rounds` 仍不通过 → 停止重试，带已知缺陷进入 Phase 5，并在最终交付说明中明确标注未解决项；
- 通过 → `status` 置 `finalizing`。

### Phase 5 · 结构化输出与校验

合并三段交付物为 `campaign_plan.json`（schema 见 references/output-schema.md），然后必须运行：

```bash
python3 scripts/validate_campaign_plan.py <campaign_plan.json 路径>
```

校验不通过时按报错补全，不许带着非法 JSON 进入渲染。

### Phase 6 · Word 渲染

先过 tencent-docs-routing 确定本地文档生成路径，再用 tencent-docx 生成。内容源只有 `campaign_plan.json`，模板与占位符要求见 references/docx-rendering.md。模型不直接排版。

### Phase 7 · 图像落地

默认保留 `{{IMAGE:hero}}`、`{{IMAGE:channel_banner}}` 占位并交付。用户明确要真实图片时：先展示图片提示词与素材清单 → 用户确认 → 才调用 ImageGen 生成并替换占位。

### Phase 8 · 交付

交付 Word 文档 + `campaign_plan.json`，并附一页过程说明：修订轮次、退回原因、未解决项、数据来源与假设。

## 停止条件

- brief 关键信息缺失且用户未补全：停在 Phase 0，列出还要什么。
- 修订到 3 轮仍不通过：停止重试，带缺陷标注交付或请用户决策。
- 用户中途改需求：回退到受影响阶段，重置对应状态，不叠加新旧状态。
- 无可用研究工具：降级为模型知识，所有结论标注"假设"，并在交付说明中披露。

## 近邻边界（不处理）

- 单段文案改写、润色、起标题：不走本流程。
- 已有方案只做排版美化：走 tencent-docx 的 beauty_only。
- 非营销类文档（研报、论文、合同等）：不走本 skill。

## 文件与读取条件

| 文件 | 何时读/运行 |
|---|---|
| references/campaign-state.md | Phase 1 初始化、Phase 3 路由、Phase 4 评审时 |
| references/output-schema.md | Phase 5 合并输出时 |
| references/docx-rendering.md | Phase 6 渲染时 |
| scripts/validate_campaign_plan.py | Phase 5 校验时必须运行 |
| assets/brief.example.json | brief 过于单薄时作为补问结构参考 |

## 风险与边界（源自架构第 9 章）

- 并行不等于无约束调用，最大修订轮数是硬闸。
- 图像生成必须先确认提示词，防止跑偏浪费。
- Word 模板样式提前锁定，否则不同环境排版漂移。
- 外部工具权限白名单，尤其是搜索、CRM、发布类。
