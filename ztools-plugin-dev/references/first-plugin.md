# 第一个插件

本指南将帮助你使用 `@ztools-center/plugin-cli` 快速创建你的第一个 ZTools 插件，并发布到插件中心。

## 前置要求

在开始之前，请确保你已经安装了以下工具：

- **Node.js** >= 16.0.0
- **npm** 或 **pnpm** 包管理器
- **Git**（用于版本控制和发布）

## 安装 CLI 工具

首先，全局安装 ZTools 插件 CLI 工具：

```bash
npm install -g @ztools-center/plugin-cli
# 或
pnpm add -g @ztools-center/plugin-cli
```

安装完成后，你可以使用 `ztools` 命令来创建和管理插件。

## 创建第一个插件

### 步骤 1: 创建插件项目

使用 CLI 工具创建一个新的插件项目：

```bash
ztools create my-first-plugin
```

这个命令会引导你完成以下步骤：

1. **选择模板** - 你可以选择以下三种模板之一：
   - **Vue + TypeScript + Vite** - 使用 Vue 3 开发插件 UI
   - **React + TypeScript + Vite** - 使用 React 开发插件 UI
   - **Preload Only (TypeScript)** - 仅使用 Preload API，无 UI 界面

2. **输入插件信息**：
   - **Plugin name** - 插件唯一标识（ID），用于系统内部识别
   - **Plugin title** - 插件显示名称（在 ZTools 中展示给用户的标题）
   - **Plugin description** - 插件描述
   - **Author** - 作者名称

### 步骤 2: 进入项目目录

创建完成后，进入项目目录：

```bash
cd my-first-plugin
```

### 步骤 3: 安装依赖

根据你选择的包管理器安装依赖：

```bash
npm install
# 或
pnpm install
```

### 步骤 4: 开发插件

现在你可以开始开发你的插件了。根据你选择的模板，项目结构会有所不同：

- **Vue/React 模板**：在 `src/` 目录下开发 UI 组件
- **Preload Only 模板**：在 `src/` 目录下编写 Preload 脚本

开发时，你可以运行开发服务器：

```bash
npm run dev
# 或
pnpm run dev
```

### 步骤 5: 构建插件

开发完成后，构建插件：

```bash
npm run build
# 或
pnpm run build
```

构建产物会输出到 `dist/` 目录。这个目录就是你的插件应用，可以打包提交。

## 发布插件

当你完成插件开发并准备好发布时，可以使用 CLI 工具将插件发布到 ZTools 插件中心。

### 前置条件

在发布之前，请确保：

1. ✅ 项目包含 `plugin.json` 文件（CLI 会自动生成）
2. ✅ 已初始化 Git 仓库（`git init`）
3. ✅ 至少有一次提交记录
4. ✅ 工作区干净（没有未提交的改动）

### 初始化 Git 仓库

如果还没有初始化 Git 仓库，请执行：

```bash
git init
git add .
git commit -m "Initial commit"
```

### 发布流程

执行发布命令：

```bash
ztools publish
```

#### 首次发布

首次执行 `ztools publish` 时，CLI 会自动完成：

1. **GitHub OAuth 认证** - 通过 Device Flow 引导你在浏览器授权一次（含 `workflow` scope），token 保存在 `~/.config/ztools/cli-config.json`
2. **Fork 中心仓库** - 自动在你账号下 fork `ZToolsCenter/ZTools-plugins`（已存在则复用）
3. **同步 fork main** - 调用 GitHub merge-upstream API 把 fork 的 main 拉齐到上游，避免后续分支基于落后的 main 导致冲突
4. **判定 Add / Update** - 检查上游 `plugins/<你的插件 ID>/` 目录是否存在，决定 PR 标题用 `Add` 还是 `Update`
5. **复制工作目录文件** - 把当前目录内容复制到 fork 的 `plugins/<插件 ID>/`（自动忽略 `node_modules`、`dist`、`.env*` 等）
6. **生成 commit + 推送分支** - 在 fork 的 `plugin/<插件 ID>` 分支上做**一个** commit 并普通 push（不 force）
7. **创建 Draft Pull Request** - 自动开 PR 到中心仓库，默认 draft 状态

#### 后续发布（增量更新）

每次 `ztools publish` 都是**增量追加**：

- 远端分支保留旧 commit，只 fast-forward 追加一个新 commit
- 同一个 PR 自动复用，链接不变
- 不会 force-push，旧的 review 评论上下文不会丢失

> 例：你本地累计 5 个 commit 发布出去后，远端 PR 上是 1 个 "Add plugin Foo v0.1.0" commit；又改了 3 个 commit 再发布，远端就 fast-forward 多 1 个 "Update plugin Foo v0.1.1" commit，旧的不动。

更详细的发布与协作机制（CHANGELOG 自动注入、智能 commit 标题、`pull-contributions` 拉回审核者改动等）请参考 [发布与协作流程](./publish-and-update.md)。

### 发布成功后

CLI 会输出类似：

```
✨ 插件发布成功!
🔗 Pull Request: https://github.com/ZToolsCenter/ZTools-plugins/pull/123

💡 下一步：去 PR 网页完善以下内容（CLI 无法自动生成）
  📸 上传截图 / 演示 GIF
  ✅ 勾选自检清单
  🚦 把 PR 从 Draft 切到 "Ready for review"
```

务必完成这 3 件事，否则维护者不会进入审核：

1. **截图 / 演示 GIF** - 直接拖图到 PR description 编辑框，GitHub 会自动上传
2. **自检清单** - PR description 里有 5 项 checkbox，逐条勾上
3. **Mark as ready for review** - 右下角按钮，把 PR 从 Draft 切到正式审核状态

## 项目结构

创建的项目通常包含以下结构：

```
my-first-plugin/
├── plugin.json          # 插件配置文件
├── package.json         # 项目依赖配置
├── tsconfig.json        # TypeScript 配置
├── vite.config.js       # Vite 构建配置（如果使用 Vite 模板）
├── src/                 # 源代码目录
│   ├── preload.ts       # Preload 脚本
│   └── ...              # 其他源文件
├── public/              # 静态资源
│   └── logo.png         # 插件 Logo
└── dist/                # 构建输出目录（构建后生成）
```

## 常见问题

### Q: 如何修改插件配置？

A: 编辑项目根目录下的 `plugin.json` 文件。你可以修改插件标识（name）、显示名称（title）、描述、功能列表等。更多信息请参考 [plugin.json 配置](./plugin-json.md)。

### Q: 如何添加插件功能？

A: 在 `plugin.json` 的 `features` 数组中添加功能配置。每个功能需要定义：
- `code` - 功能唯一标识
- `explain` - 功能说明
- `cmds` - 触发指令列表

### Q: 发布失败怎么办？

A: 检查以下几点：
- 确保在插件项目根目录下执行命令
- 确保已初始化 Git 并至少有一次提交
- 确保 `plugin.json` 文件存在且格式正确
- 检查网络连接和 GitHub 认证状态

### Q: 如何更新已发布的插件？

A: 修改代码、`git commit`，然后再次执行 `ztools publish`。CLI 会自动在**同一个 PR** 上 fast-forward 追加一个新 commit，链接不变。如果上一次的 PR 已经合并，新的 publish 会以 `Update` 标题开一个新 PR。

### Q: 审核者直接在 PR 分支上改了代码，我下次 publish 会被拒，怎么办？

A: 跑 `ztools pull-contributions`，它会把审核者的 commit 三方合并回你本地，再 `ztools publish` 即可。详见 [发布与协作流程](./publish-and-update.md#pull-contributions)。

### Q: PR 标题是怎么决定的？

A: PR 标题始终是 `Add plugin <名称> v<版本>` 或 `Update plugin <名称> v<版本>`，由"中心仓库 main 是否已有该插件目录"决定。每次发布在 commit message 里会附带你本地自上次发布以来的 commit subjects 作为变更明细。

### Q: 我删了上一个 PR 重新 publish 没反应？

A: 你之前 publish 过时 fork 上分支已经存在；CLI 检测到本地内容与 fork 一致就不会再 commit。这种情况会**自动复用已有 branch 重开一个 PR**——直接重新跑 `ztools publish` 即可，新 PR 链接会显示在终端。

## 下一步

- 📖 了解 [插件应用目录结构](./file-structure.md)
- 📖 学习 [plugin.json 配置](./plugin-json.md)
- 📖 查看 [插件 API 文档](./plugin-api.md)
- 📖 阅读 [preload.js 说明](./preload-js.md)

## 相关资源

- [ZTools GitHub 仓库](https://github.com/ZToolsCenter/ZTools)
- [API 类型定义](https://www.npmjs.com/package/@ztools-center/ztools-api-types)
- [插件 CLI 工具](https://www.npmjs.com/package/@ztools-center/plugin-cli)

