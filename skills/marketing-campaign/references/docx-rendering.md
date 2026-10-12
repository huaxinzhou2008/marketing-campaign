# Word 渲染：模板要求与流程

Word 必须由结构化 JSON 经模板渲染，模型不直接排版。本环境用 tencent-docx 技能完成（先过 tencent-docs-routing 再生成）。

## 渲染流程

```
campaign_plan.json
  ↓ tencent-docs-routing 确定本地文档生成路径
  ↓ tencent-docx 生成（内容源仅限 campaign_plan.json）
  ↓ 填充封面、目录、正文、表格、图片占位、页眉页脚
  ↓ 输出 <campaign_name>.docx
```

## 模板要求（生成前确认或与用户确认）

- **封面**：活动名称、品牌、日期；
- **品牌页眉**：Logo + 品牌名；
- **品牌页脚**：保密标识 + 页码；
- **目录**：使用 Word 原生 Heading 样式，用户打开后按 F9 刷新；不在代码里硬生成页码；
- **图片占位**：`{{IMAGE:hero}}`、`{{IMAGE:channel_banner}}`，未确认生成前保留为占位文本；
- **表格样式**：预算表、时间表、KPI 表三张，样式提前锁定，避免不同环境排版漂移。

## 技术实现要点（对应架构第 6 章）

- 用 python-docx 或 docxtpl 做模板渲染；本环境统一走 tencent-docx，保持同一原则；
- 页眉页脚通过 section.header / section.footer 写入；
- 图片占位通过遍历段落和 run 替换；
- 模型只输出 JSON，不直接操作 Word。

## 常见失败与处置

| 失败 | 处置 |
|---|---|
| JSON 校验未过 | 回 Phase 5 修补，不进入渲染 |
| 用户无品牌规范 | 页眉页脚退化为活动名 + 页码，交付说明中注明 |
| 用户只要 PDF/其他格式 | 仍先产 docx，再按用户指定格式转换 |
| 图片未确认 | 保留占位文本，不调用生图工具 |
