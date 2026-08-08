# image-to-visio-skill

把流程图、架构图、论文插图、关系图、信息图或截图，重绘为 **Microsoft Visio 可打开、真正可编辑的 `.vsdx`**，并通过 **VSDX → PDF → PNG** 做几何/像素级 QA。

> 核心原则：不能把整张原图贴进 Visio 冒充“可编辑版”。标题、正文、框、线、箭头、流程节点、表格和关系网络应尽量全部重建为独立 Visio Shape；只有书影、照片、扫描纹理等天然位图区可保留为局部图片。

## 给 Agent / Coding Agent

如果你是 AI Agent、Coding Agent、CLI Agent 或自动化工作流，请先读取根目录的 [`SKILL.md`](./SKILL.md)，并把它当作本仓库的**主执行规范**。

当用户表达以下意图时，优先使用本 Skill：

- “把这张图转成 Visio”
- “照这个图画一个可编辑 Visio”
- “图片转可编辑 VSDX”
- “像素级复刻这个流程图 / 架构图 / 论文插图”
- “最后导出 PDF 核对是否一致”

Agent 执行时必须遵守以下约束：

1. **不要把整张源图直接铺在可编辑页上冒充矢量结果。**
2. 标题、正文、表格、矩形、圆角框、箭头、虚线、连接关系等，应尽量重建成独立 Visio Shape。
3. 只有照片、扫描书影、复杂纹理等天然栅格内容允许保留为局部位图。
4. 优先从 `templates/known_good_two_page_template.vsdx` 派生，避免手搓极简 VSDX 导致 Microsoft Visio 无法打开。
5. 完成后必须先运行结构预检，再执行 **VSDX → PDF → PNG** 的 QA。
6. 像素核对必须比较**真正的可编辑页**，不能拿“原图覆盖页”做匹配结果。
7. 如果用户明确要求“像素级一致”，优先按原图像素坐标建立布局，再统一映射到 Visio 页面坐标，不要凭英寸目测摆放。

推荐 Agent 最小执行链：

```text
读取参考图
  ↓
分析布局 / 建立像素坐标
  ↓
分类：矢量对象 vs 局部位图
  ↓
从 known-good VSDX 模板派生
  ↓
生成真正可编辑的 Visio Shape
  ↓
preflight_vsdx.py
  ↓
VSDX → PDF → PNG
  ↓
verify_pixel_match.py
  ↓
修正坐标 / 字体 / 线条
  ↓
交付 VSDX + PDF + QA 结果
```

Agent 的默认交付物应至少包含：

- 可编辑 `.vsdx`
- 导出的核对 `.pdf`
- 像素/几何匹配报告
- 必要时的 side-by-side 与差异图

详细的坐标映射、VSDX 兼容性要求、Shape 组织方式、QA 阈值和故障恢复规则，都写在 [`SKILL.md`](./SKILL.md) 中。**不要只读 README 就直接生成 VSDX。**

## 适用场景

- 图片 / 截图转可编辑 Visio
- 论文流程图、架构图、知识图谱重绘
- 按原图高一致性复刻 VSDX
- 生成 Visio 后自动导出 PDF 做渲染核对
- 检查“可编辑页”是否偷偷铺了整页位图

## 仓库结构

```text
image-to-visio-skill/
├─ SKILL.md
├─ README.md
├─ LICENSE
├─ .gitignore
├─ scripts/
│  ├─ preflight_vsdx.py
│  ├─ verify_pixel_match.py
│  └─ export_and_verify.py
├─ templates/
│  ├─ known_good_two_page_template.vsdx
│  └─ layout_spec.schema.json
└─ examples/
   └─ layout_spec.example.json
```

## 推荐工作流

1. 读取原图尺寸和布局，建立像素坐标系。
2. 将标题、正文、表格、框线、箭头等拆成独立矢量对象。
3. 仅对照片/扫描书影等区域保留局部位图。
4. 从 `templates/known_good_two_page_template.vsdx` 派生，避免极简 VSDX 包导致桌面版 Visio 无法打开。
5. 运行结构预检：

```bash
python scripts/preflight_vsdx.py output.vsdx --editable-page 2
```

6. 导出 PDF、渲染可编辑页、与原图做 QA：

```bash
python scripts/export_and_verify.py source.png output.vsdx \
  --page 2 --dpi 100 --outdir qa_out
```

## 像素核对

单独比较：

```bash
python scripts/verify_pixel_match.py source.png rendered.png \
  --src-min 0.995 --render-min 0.98 --outdir qa_out
```

关键指标：

- 原图与渲染图像素尺寸必须一致；
- `source_ink_match_1px`：原图墨迹在渲染结果 1 px 邻域内的命中率；
- `render_ink_match_1px`：渲染墨迹在原图 1 px 邻域内的命中率；
- RGB 完全一致率仅供参考，因为 Visio/PDF 字体抗锯齿会变化。

## 依赖

Python：

```bash
pip install pillow numpy
```

系统工具：

- LibreOffice / `soffice`
- Poppler / `pdftoppm`

## Skill 用法

把本仓库作为 Agent / Coding Agent 的技能目录使用时，读取 `SKILL.md`。Skill 中包含完整的重绘规则、VSDX 结构约束、QA 标准和兼容性恢复流程。

## License

MIT
