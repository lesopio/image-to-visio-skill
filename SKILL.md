---
name: image-to-visio
description: "将用户提供的流程图、架构图、论文插图、关系图或截图重绘为 Microsoft Visio 可打开的 VSDX：文本/框/连接线/箭头等尽量全部矢量可编辑，只对书影、照片、扫描纹理等天然位图区域保留裁剪位图；最后强制导出 PDF、栅格化并与原图做像素级几何核对。适用于‘照图画 Visio’、‘图片转可编辑 Visio’、‘像素级复刻’、‘做 VSDX 并转 PDF 核对’等请求。"
---

# Primary Goal

从一张或多张参考图得到一个**真正可编辑、桌面版 Visio 可打开、视觉位置高度一致**的 `.vsdx`，并用 PDF 渲染结果验证**可编辑页本身**与原图的几何一致性。

系统指令和用户要求始终优先于本 Skill。

# Non-negotiable

- **禁止伪可编辑**：不能把整张原图作为一张大位图铺在“可编辑页”上就交付。
- 可编辑页中的标题、正文、矩形/圆角矩形、分组框、直线、虚线、点线、箭头、括号、连接关系等，默认都应为独立 Visio Shape。
- 只有书影、照片、扫描件、复杂纹理、印章等“不合理矢量化”的区域可保留为局部 `Foreign` 位图，并且必须按原位置裁剪嵌入。
- **PDF 像素核对必须核对可编辑页，不得核对原图覆盖页来“刷分”。** 默认两页结构时，核对第 2 页。
- 页面宽高比、对象坐标、边框粗细、虚实线型、字体层级、文字对齐和留白都属于复刻目标。
- 不以 RGB 完全逐像素一致作为硬性目标，因为 Visio/LibreOffice/PDF 渲染的字体抗锯齿会变化；以**尺寸一致 + 1 px 容差下的墨迹/边缘位置匹配**为主要验收。
- 不要仅凭 LibreOffice 能打开就声称“Microsoft Visio 一定兼容”。应从本 Skill 的已验证模板结构派生，并做 VSDX 结构预检；若用户实际 Visio 报错，以其报错为最终兼容性反馈。

# Default Deliverables

默认生成：

1. `*_Visio.vsdx`：可编辑 VSDX。默认两页：
   - 第 1 页：`像素核对版` / 参考页，可放原图整页覆盖，便于人工对照；
   - 第 2 页：`可编辑矢量版`，必须是真正的矢量重绘。
2. `*_核对.pdf`：VSDX 导出的 PDF。
3. `pixel_match_report.txt/json`：可编辑页与原图的像素几何匹配报告。
4. `side_by_side.png`、`diff_x4.png`：只用于 QA；用户未要求时可不主动展示。

如果用户明确只要单页 VSDX，可只保留可编辑页，但 QA 仍必须在单独导出的 PDF 上进行。

# Core Workflow

## 1. 读取参考图并建立像素坐标系

先记录原图：

- `W_px × H_px`
- 主要外框位置
- 列/行分区
- 关键基准线
- 文本层级
- 连接线端点
- 需要保留为位图的局部区域

优先用视觉理解直接读图；只有文字确实无法可靠辨认时才考虑 OCR，避免为了 OCR 反复调用高成本流程。

建议先形成一个 `layout_spec.json`，所有对象都用原图的**左上角像素坐标**描述。模板见 `templates/layout_spec.schema.json`。

## 2. 分类：哪些必须矢量，哪些允许位图

必须矢量化：

- 标题、编号、正文、标签
- 矩形、圆角矩形、边框、分隔线
- 实线、虚线、点线、箭头、括号/树状关系线
- 图例、流程框、说明区

允许局部位图：

- 古籍书影、照片
- 扫描页原貌
- 高密度印刷纹理
- 复杂非结构化图案

若一个位图区域中的文字本应让用户编辑，则不能整块保留，应把文字重绘出来。

## 3. 坐标映射

所有重绘对象先在像素坐标中定位，再统一转换到 Visio 页面坐标。

推荐选定目标 DPI，例如 100 DPI：

- 初始页面宽度 `W_in = W_px / DPI`
- 初始页面高度 `H_in = H_px / DPI`

Visio 以左下角为坐标原点；参考图以左上角为原点，因此：

- `x_visio = x_px / DPI`
- `y_visio = H_in - y_px / DPI`

矩形使用中心点、宽高转换。不要一边看图一边用英寸猜位置；所有视觉位置先落回像素坐标。

PDF 渲染后若恰好出现 1 px 的整页尺寸偏差，可按渲染器结果微调 PageWidth/PageHeight，再重新导出，不要通过缩放比较图来掩盖尺寸错误。

## 4. 用已验证 VSDX 包结构，而不是极简手搓包

优先从：

`templates/known_good_two_page_template.vsdx`

派生新文件。这个模板来自用户实际可打开的矢量版 VSDX 包结构。

需要保留/正确维护的关键部件至少包括：

- `[Content_Types].xml`
- `_rels/.rels`
- `visio/document.xml`
- `visio/_rels/document.xml.rels`
- `visio/windows.xml`
- `visio/pages/pages.xml`
- `visio/pages/_rels/pages.xml.rels`
- `visio/pages/pageN.xml`
- 页面对应 `.rels`
- `docProps/app.xml`
- `docProps/core.xml`
- 可选 `docProps/custom.xml`
- `visio/media/*`（仅存在局部位图时）

兼容性经验：

- `document.xml` 中保留完整 `DocumentSettings`、`Colors`、`FaceNames`、`StyleSheets`、`DocumentSheet`。
- 提供 `windows.xml`。
- 黑/白色优先使用颜色表索引 `0/1`，不要在大量 Cell 中混用不规范的颜色表达。
- 关系文件中的内部 `Target` 必须实际存在。
- 页面数量、`pages.xml`、`pages.xml.rels`、`docProps/app.xml` 的页面元数据应保持一致。
- `ForeignData` 的 `r:id` 必须能解析到对应 `visio/media/*`。

## 5. 形状组织

每个视觉对象应尽量成为独立 Shape，并给出可读的 `Name/NameU`，例如：

- `主标题`
- `章节编号`
- `A_分组框`
- `典籍_01_神农本草经`
- `关系_01`
- `资源整合流程_节点_01`

这样用户打开 Visio 后容易选择、修改、移动。

对于文本：

- 尽量使用常见中文字体，如 Microsoft YaHei / SimSun；
- 对齐方式、字号、粗体、换行必须单独设定；
- 不要依赖默认文本框内边距，必要时显式设置 `TxtPinX/TxtPinY/TxtWidth/TxtHeight`。

对于线条：

- 实线、虚线、点线用不同 `LinePattern`；
- 线宽独立控制；
- 连接线与对象边界的间距应按原图像素位置复刻，而不是“看起来差不多”。

## 6. VSDX 结构预检

完成后先运行：

```bash
python scripts/preflight_vsdx.py output.vsdx --editable-page 2
```

必须：

- ZIP CRC 正常；
- 所有 XML / `.rels` 可解析；
- 必要 OPC 部件存在；
- 所有内部关系目标存在；
- 页面关系正常；
- 可编辑页不能存在覆盖 >92% 页面面积的整页 `Foreign` 位图。

只要预检失败，就不要交付。

## 7. 强制 PDF 导出与可编辑页像素核对

如果环境中存在 `/home/oai/skills/pdfs/SKILL.md`，在处理 PDF 前先遵循该 PDF Skill 的 render → verify 要求。

可用一键 QA：

```bash
python scripts/export_and_verify.py source.png output.vsdx --page 2 --dpi 100 --outdir qa_out
```

它会：

1. 预检 VSDX；
2. 用 LibreOffice/soffice 导出 PDF；
3. 用 `pdftoppm` 只栅格化指定的**可编辑页**；
4. 调用 `verify_pixel_match.py` 与原图比较；
5. 输出 side-by-side、4×差异图和报告。

若 PDF 页渲染尺寸与原图不同，先修页面尺寸，不允许先 resize 后比较。

## 8. 验收分两级

**基础交付门槛（任何任务都必须满足）：**

- 页面像素宽高完全一致；
- PDF 核对的是可编辑页；
- 主要外框、分区、节点、连接关系与原图位置一致，没有明显错位；
- 局部位图不拉伸、不变形；
- 生成 side-by-side 和差异图并人工检查。

**严格“像素级一致”门槛（只有用户明确要求像素级一致时启用）：**

对黑白/低彩流程图可从以下目标起步：

- `source_ink_match_1px >= 99.5%`
- `render_ink_match_1px >= 98.0%`

调用示例：

```bash
python scripts/verify_pixel_match.py source.png rendered_editable_page.png \
  --src-min 0.995 --render-min 0.98 --outdir qa_out
```

这些阈值很严格，字体渲染、圆角、线宽和抗锯齿都会影响结果。若达不到，**不得声称已经像素级一致**；应继续迭代，或明确报告实际数值并说明当前只达到布局/结构一致。

`exact_rgb_pixel_ratio` 仅作参考，不作为硬门槛。若参考图存在大量灰阶/彩色渐变，应补充边缘图或结构区域比对，而不是盲目使用同一个灰度阈值。

## 9. 迭代顺序

像素核对不通过时，按以下顺序改：

1. 页面尺寸 / DPI
2. 外框与大分区坐标
3. 行列基准线、流程框尺寸
4. 字体字号、文本框宽高、换行
5. 线型与线宽
6. 局部图片裁剪与缩放
7. 抗锯齿造成的小范围 RGB 差异（最后再看）

最多进行少量有针对性的迭代，不要用无限试参替代坐标测量。

# Compatibility Rule Learned From the Approved Example

本 Skill 提供 `templates/known_good_two_page_template.vsdx` 作为已验证的两页 VSDX 包结构模板。后续任务若需要手工组装 VSDX，应优先复用其 OPC/Visio 文档结构，而不是从一个只有数个 XML 的最简 VSDX 开始。

模板只提供 **OPC / Visio 文档结构**，不提供任何特定任务的坐标与文本。新任务必须重新测量原图，不得沿用示例坐标或内容。

# Failure Recovery

如果用户反馈“Visio 无法打开”：

1. 不要争辩“LibreOffice 可以打开”。
2. 先运行 `preflight_vsdx.py`。
3. 对照 `known_good_two_page_template.vsdx` 检查：Content Types、root rels、document rels、windows、pages、docProps。
4. 检查页面关系、媒体关系、页面计数。
5. 尽量在已验证模板上重新封装现有 `pageN.xml`，而不是继续修最简包。
6. 若用户提供 Visio 的完整报错，按报错定位，并重新导出 PDF 验证视觉内容未被破坏。

# Delivery Wording

交付时简洁说明：

- 哪个文件是可编辑 VSDX；
- 哪个 PDF 用于核对；
- 核对的是第几页（必须明确是可编辑页）；
- 页面尺寸是否一致；
- 1 px 容差下两个方向的墨迹匹配率；
- 不把 RGB 抗锯齿差异夸成几何误差。

如果未在真实 Microsoft Visio 中打开过，不应写“已确认 Microsoft Visio 兼容”；应写“已通过 VSDX 结构预检和 PDF 导出验证；桌面 Visio 兼容性以实际打开为准”。
