# OpenClaw 研究报告编排器

## 使用

在包含本仓库 `skills/` 目录的 OpenClaw 工作区中输入：

```text
/research-report-orchestrator

主题：生成式 AI 对独立软件开发者的影响
篇幅：standard
读者：懂产品但不熟悉 AI 技术的创业者
目的：判断未来两年应该优先培养哪些能力
交付：Markdown + 自包含 HTML
```

编排器会按需调用已下载的子 Skill，而不是强制每份报告都做评分或图表。

## 已下载能力

| Skill | 固定版本 | 用途 | 外部要求 |
| --- | --- | --- | --- |
| `academic-research-hub` | 0.1.0 | arXiv、PubMed、Semantic Scholar | Python 依赖，网络 |
| `cellcog` | 2.0.15 | Data Cog 的 SDK 指引 | `CELLCOG_API_KEY` |
| `data-cog` | 1.0.11 | 远程数据分析 | `CELLCOG_API_KEY`，数据会上传 |
| `academic-writing` | 1.0.0 | 正式及学术写作规范 | 无 |
| `kai-report-creator` | 1.23.3 | 单文件 HTML 报告 | 图片导出可选依赖 Playwright |

具体版本记录在仓库根目录 `.clawhub/lock.json`。

本地 `research-chart` Skill 使用 Python 标准库生成 SVG，不需要额外依赖。

## 可选依赖

在 OpenClaw 运行环境中按实际使用的能力安装，不要为了未使用的步骤预装全部依赖。

学术检索：

```bash
python3 -m venv .venv-research
source .venv-research/bin/activate
pip install -r skills/@anisafifi/academic-research-hub/scripts/requirements.txt
```

远程数据分析：

```bash
export CELLCOG_API_KEY="..."
```

不要把密钥写入仓库。`data-cog` 会把 `<SHOW_FILE>` 指定的文件上传到 CellCog；内部或机密数据默认禁止使用该路线。

## 安全说明

这些社区 Skill 已通过 ClawHub 页面展示的自动安全检查，但自动检查不是安全保证。更新前应重新检查：

```bash
npx -y clawhub@latest inspect @owner/skill --files
```

本工作流没有下载 `deep-researcher`：检查结果同时出现 `Moderate CLEAN` 和 `Security SUSPICIOUS`，信号冲突。其有价值的方法已用更保守的方式实现在自有编排器中。

`academic-citation-manager` 也未保留：安装后的语法检查发现其主 Python 文件存在 `SyntaxError`。引用核验由编排器结合学术检索结果和原始出版页面执行。

`chart-image` 未保留：其锁定依赖在 `npm audit` 中报告 6 个高危 Vega/Vega-Lite 漏洞。工作流改用无第三方依赖的本地 `research-chart`。
