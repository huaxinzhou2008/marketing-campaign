# campaign_state：共享状态、协作消息与评审清单

所有角色通过工作目录下的 `campaign_state.json` 交换信息。任何角色不得绕过该文件直接调用另一个角色。

## 1. 状态 Schema

```json
{
  "status": "researching | writing | designing | reviewing | revising | finalizing",
  "brief": {},
  "research_summary": null,
  "copy_package": null,
  "visual_package": null,
  "open_questions": [],
  "revision_round": 0,
  "max_revision_rounds": 3,
  "messages": []
}
```

| 字段 | 规则 |
|---|---|
| `status` | 状态机唯一真源；只有主 Agent（Manager）允许改写 |
| `brief` | 用户原始需求，Phase 0 定稿后不再改动 |
| `research_summary` / `copy_package` / `visual_package` | 三角色交付物路径或内容摘要；子 Agent 只写自己那栏 |
| `open_questions` | 待路由的依赖问题；Manager 路由后清空该条并写入 `messages[]` |
| `revision_round` / `max_revision_rounds` | 修订计数与硬上限 3；Manager 独占修改 |
| `messages` | 协作消息流水，只增不改 |

## 2. 状态机

```
researching ──┬──> writing ──┐
              ├──> designing ─┤
              │               ├──> reviewing ──通过──> finalizing
              └───────────────┘        │
                                       └──不通过──> revising ──> reviewing（revision_round + 1）
```

- `revising` 只退回问题最小的子任务，未退回角色的成果保留。
- `revision_round` 达到 `max_revision_rounds` 后禁止再进入 `revising`，必须带缺陷进入 `finalizing` 并在交付说明中标注。

## 3. 协作消息（collab_request）

```json
{
  "from": "writer",
  "to": "image_designer",
  "type": "request",
  "content": "请基于'高性价比家用投影仪'定位提供3种视觉方向。",
  "status": "pending"
}
```

- `type`：request / response / decision。
- `status`：pending → routed → resolved；由 Manager 推进。
- 每次路由都写日志（时间、from、to、决策理由），便于审计和重试。

## 4. 三角色交付物最低要求

**Researcher → `research_summary.md`**
- 行业趋势、竞品动作、用户洞察、渠道数据四节；
- 每条结论标注来源（URL/工具/知识库）或显式写"假设"；
- 输出 `open_questions`：需要其他角色或用户确认的问题。

**Writer → `copy_package.md`**
- 定位声明、核心卖点（≤5）、主文案、渠道文案变体、内容日历、CTA；
- 遵循品牌规范（语气、禁用词、口吻）；
- 标注哪些卖点依赖 Researcher 结论。

**Image Designer → `visual_package.md`**
- ≥3 个视觉方向，每个含：方向名、风格描述、适用渠道、图片提示词（中英文各一）；
- 素材清单（需要用户提供的 Logo/产品图/实拍）；
- 禁止在此阶段调用生图工具。

## 5. 评审清单（Manager 逐项打勾）

研究线：
- [ ] 结论有来源或"假设"标注
- [ ] 竞品覆盖 ≥3 家
- [ ] 与 brief 的活动目标直接相关

文案线：
- [ ] 定位一句话能说清
- [ ] 卖点有研究结论或明确假设支撑
- [ ] CTA 具体可执行
- [ ] 语气符合品牌规范

视觉线：
- [ ] 方向 ≥3 且互不重复
- [ ] 提示词可执行（主体、风格、构图、比例齐全）
- [ ] 视觉方向与文案定位一致

整体：
- [ ] 预算、时间线、KPI 三者自洽
- [ ] 无未路由的 collab_request

任一项不过 → 退回对应角色，重试前先更新 `campaign_state.json`。
