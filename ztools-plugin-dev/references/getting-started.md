# 快速开始

hey，开发者，终于和你见面了。

从这里开始，将会慢慢的给你介绍如何开发一个 ZTools 插件应用，帮助你一步步的完成开发、构建和发布。

## 插件应用是什么

**Node.js 本地原生能力 + Web 前端网页**。(本地软件能做到的，理论上它也能做到)

ZTools 插件应用结合了 Web 前端技术的灵活性和 Node.js 的强大本地能力，让你可以：

- 🎨 使用 HTML、CSS、JavaScript 构建美观的用户界面
- ⚡ 通过 Node.js 访问系统原生能力（文件系统、网络、进程等）
- 🔌 使用丰富的 ZTools API（通知、剪贴板、窗口管理等）
- 📦 支持 Vue、React 等现代前端框架
- 🌍 跨平台运行（Windows、macOS、Linux）

## 环境要求

在开始开发你的第一个插件应用之前，请保证你已经做好以下准备：

### 必需工具

- **ZTools** - [下载地址](https://github.com/ZToolsCenter/ZTools/releases)
  - macOS: 下载 `ZTools-x.x.x-arm64.dmg` 或 `ZTools-x.x.x-arm64.zip`
  - Windows: 下载 `ZTools-x.x.x-setup.exe` 或 `ZTools-x.x.x-win.zip`
- **Node.js** >= 16.0.0 - [下载地址](https://nodejs.org/)
- **一个好用的代码编辑器** - 推荐 [VSCode](https://code.visualstudio.com/) 或者 [WebStorm](https://www.jetbrains.com/webstorm/)
- **Git** - 用于版本控制和插件发布（[下载地址](https://git-scm.com/)）

### 基础知识

- **熟悉 JavaScript** - 基础开发语言
- **熟悉 HTML 和 CSS** - 掌握基础的界面构建能力
- **了解 Node.js** - 接入强大的本地原生能力

### 进阶

可借助 **Vue** 或者 **React** 等主流的 Web 前端开发框架，增强你的应用界面。

ZTools 插件 CLI 工具提供了以下模板：

- **Vue + TypeScript + Vite** - 使用 Vue 3 开发插件 UI
- **React + TypeScript + Vite** - 使用 React 开发插件 UI
- **Preload Only (TypeScript)** - 仅使用 Preload API，无 UI 界面

## 下一步

现在你已经了解了插件应用的基本概念和环境要求，接下来可以：

1. 📖 [创建第一个插件](./first-plugin.md) - 使用 CLI 工具快速创建你的第一个插件
2. 📁 [了解插件应用目录结构](./file-structure.md) - 深入了解插件的文件组织方式
3. 📝 [学习 plugin.json 配置](./plugin-json.md) - 掌握插件配置文件的使用
4. 🔌 [查看插件 API 文档](./plugin-api.md) - 了解可用的 API 能力

准备好了吗？让我们开始吧！🚀

