---
name: ztools-plugin-dev
description: >-
  ZTools 插件开发全流程指南。覆盖架构理解、项目初始化、plugin.json 配置、
  插件 API 调用、调试与发布。当用户提及 ZTools、ztools 插件、uTools 平替
  开发时使用。
---

# ZTools 插件开发

## 概述

ZTools 是 uTools 的开源桌面插件平台，技术栈 Electron 38.5 + Vue 3 + TypeScript + LMDB + Chrome 140，跨 macOS/Windows/Linux。每个插件由一个 Web 前端页面 + 一个 preload.js 组成，通过 `window.ztools` 暴露约 80 个系统 API。

详见 `references/index.md`（产品概览）和 `references/CLAUDE.md`（主仓库完整架构）。

## 核心架构：双 preload 体系

ZTools 有两套完全独立的 preload，这是理解插件系统的关键：

| | 主程序 preload | 插件 preload |
|---|---|---|
| **文件** | `src/preload/index.ts`（Vite 构建） | `resources/preload.js`（原生 JS） |
| **消费者** | ZTools 自己的 Vue 界面 | 所有插件（第三方 + 内置） |
| **修改生效** | 热重载 | 必须重启应用 |
| **写插件关心哪个** | 不关心 | 它是你的 Node.js 能力入口 |

插件页面跑在纯浏览器沙箱（`contextIsolation: true`），无法 `require()`，所有系统能力通过 `window.ztools` 调用。preload.js 在隔离的另一侧拥有完整 Node.js 能力，通过 `contextBridge` 把 API 选择性暴露给页面。

## 插件系统三条铁律

1. **plugin.json 是入口** — name/title/main/logo/preload 必填，features 数组定义触发方式（6 种类型）
2. **preload.js 不可混淆** — 源码及第三方模块必须清晰可读，禁止打包/压缩
3. **数据自动隔离** — LMDB 操作自动加 `PLUGIN/{插件名}/` 前缀，删除插件时自动清理

## 开发流程

```
npm install -g @ztools-center/plugin-cli
ztools create <plugin-name>        # 选择模板：Vue / React / Preload Only
cd <plugin-name> && npm install
npm run dev                         # 开发（热重载）
npm run build                       # 构建到 dist/
ztools publish                      # 发布（自动 fork + PR）
```

### 模板选择

| 模板 | 场景 |
|---|---|
| React + TypeScript + Vite | 需要 UI，熟悉 React |
| Vue + TypeScript + Vite | 需要 UI，熟悉 Vue 3 |
| Preload Only (TypeScript) | 无界面插件 |

### 目录结构

```
plugin-name/
├── plugin.json          # 入口配置（必读 references/plugin-json.md）
├── preload.js           # Node.js 能力层（必读 references/preload-js.md）
├── index.html           # 前端入口
├── logo.png             # Logo（png/jpg）
├── src/                 # 框架源码
└── dist/                # 构建输出（仅此目录打包为插件）
```

关键规则：ZTools 只识别 `html + css + javascript`，框架代码须编译到 `dist/`。Node.js 第三方依赖放在 preload.js 同级，不可混淆。

## 写插件时的核心文件

### plugin.json

定义插件的身份和触发方式。6 种 cmds 类型：

- **字符串** — 精确匹配用户输入，支持拼音
- **regex** — 正则匹配（如颜色值 `#xxx`）
- **over** — 匹配任意文本（翻译、搜索场景）
- **img** — 用户粘贴图片时触发
- **files** — 用户拖入文件/文件夹时触发（可限制扩展名、数量）
- **window** — 匹配当前活动窗口

完整字段和示例见 `references/plugin-json.md`。

### preload.js

遵循 CommonJS，用 `require` 引入 Node.js 模块。通过 `window.xxx` 暴露自定义 API 给前端。三种引入方式见 `references/node-js.md`：

1. **Node.js 原生模块** — `require('node:fs')` 等
2. **自编模块** — `require('./libs/myModule.js')`
3. **第三方模块** — npm install 或 git clone 源码

安全红线：不可压缩/混淆，源码必须审计可读。

### 插件 API（window.ztools）

约 80 个 API，覆盖 13 大类。完整参考见 `references/plugin-api.md`。常用类别：

| 类别 | 关键 API | 用途 |
|---|---|---|
| 窗口/UI | `setExpendHeight`, `onPluginEnter`, `setSubInput` | 控制插件视图和搜索框 |
| 数据库 | `db.put/get/remove`, `dbStorage.setItem/getItem` | 持久化存储（自动隔离） |
| 剪贴板 | `clipboard.writeContent`, `copyText`, `copyImage` | 读写剪贴板 |
| 文件 | `showOpenDialog`, `showSaveDialog`, `screenCapture` | 文件对话框、截图 |
| Shell | `shellOpenExternal`, `shellShowItemInFolder` | 打开 URL/文件 |
| 系统 | `isMacOs`, `getNativeId`, `showNotification` | 系统信息、通知 |
| 输入 | `simulateKeyboardTap`, `sendInputEvent` | 模拟键盘/鼠标 |
| AI | `ztools.ai(option, streamCallback)` | 调用 AI 模型（支持流式） |

## 发布流程

```bash
ztools publish
```

首次发布自动完成：GitHub OAuth 认证 → fork 中心仓库 → 同步 main → 复制文件 → commit + push → 创建 Draft PR。后续发布只 fast-forward 追加，不 force-push。

发布后必须手动完成 3 件事：上传截图/GIF、勾选自检清单、将 PR 从 Draft 切到 Ready for review。

详细机制（CHANGELOG 处理、冲突解决、`pull-contributions` 等）见 `references/publish-and-update.md`。

## 调试

- 插件 UI 热重载：`npm run dev`（无需重启 ZTools）
- preload.js 修改：**必须重启 ZTools 应用**
- 使用 `ztools.isDev()` 判断是否开发模式
- 开发模式配置：在 `plugin.json` 的 `development.main` 中指定本地 dev server URL

## 参考文件索引

所有详细文档位于 `references/` 目录，按阅读优先级排列：

| 优先级 | 文件 | 何时读 |
|:---:|:---|:---|
| 1 | `getting-started.md` | 首次了解环境要求 |
| 2 | `first-plugin.md` | 第一个插件的完整步骤 |
| 3 | `file-structure.md` | 确认目录结构和打包规则 |
| 4 | `plugin-json.md` | 写 plugin.json 配置时 |
| 5 | `preload-js.md` | 写 preload.js 时 |
| 6 | `node-js.md` | preload 中引入 Node 模块时 |
| 7 | `plugin-api.md` | 调用 `window.ztools` API 时（**核心**） |
| 8 | `publish-and-update.md` | 发布遇到问题时 |
| 9 | `CLAUDE.md` | 理解主仓库架构或新增 API 时 |
| 10 | `index.md` | 了解产品定位 |
| 11 | `README.md` | 了解主项目特性 |
| 12 | `changelog.md` | 查看版本变更 |

### 大型文件搜索提示

- `plugin-api.md`（~550 行）：用 API 名称直接 grep，如 `copyText`、`setSubInput`、`onPluginEnter`
- `CLAUDE.md`（~380 行）：按模块名搜索，如 `pluginManager`、`IPC`、`LMDB`
- `publish-and-update.md`（~290 行）：搜索 `pull-contributions`、`CHANGELOG`、`422`

## 关键提示

- `resources/preload.js` 不经过 Vite 构建，修改需重启
- 插件 .zpx 格式 = asar + gzip，构建命令 `npm run build` 自动输出
- 插件 UI 完全可控（自定义 CSS/组件），无框架限制
