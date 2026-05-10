# 发布与协作流程

本页详细介绍 `ztools publish` 和 `ztools pull-contributions` 的内部机制与高级使用场景。如果你只想快速发布一次插件，先看 [第一个插件](./first-plugin.md) 的发布章节就够了。

## 整体模型

ZTools 插件中心采用 **fork + PR** 模式：

- 中心仓库：`ZToolsCenter/ZTools-plugins`
- 每位作者在自己 GitHub 账号下 fork 一份
- 每次发布走「复制工作目录 → 在 fork 的 `plugin/<插件 ID>` 分支上 commit → push → 开 PR」

`ztools-plugin-cli` 把这套流程自动化了，并提供以下保障：

- **增量发布**：每次发布只 fast-forward 追加一个 commit，不 force-push
- **持久化缓存**：fork 在本地 clone 一次（`~/.config/ztools/ZTools-plugins/`），后续发布复用
- **正确的 Add/Update 判定**：基于上游 main 的实际状态而非分支存在性
- **协作友好**：审核者直推后通过 `pull-contributions` 三方合并回本地

## 发布命令详解

### `ztools publish` 完整流程

```
1. 校验 plugin.json + git 仓库 + 工作区干净
2. CHANGELOG 检查（缺失当前版本节时交互式录入）
3. GitHub OAuth 认证（首次会引导浏览器授权）
4. Fork 中心仓库（不存在则自动创建）
5. ensureForkClone：clone 或 fetch 本地 fork 缓存
6. syncForkMain：调用 merge-upstream API 同步 fork main
7. pluginExistsUpstream：探测上游 plugins/<id>/ 目录决定 Add/Update
8. prepareBranch：在 fork 分支上 checkout（已存在则复用，否则基于 upstream/main 新建）
9. copyPluginFiles：把工作目录复制进 plugins/<id>/，自动忽略 node_modules、dist 等
10. commitPluginChanges：组装智能 commit message 并提交（无变更则跳过）
11. pushPluginBranch：普通 push，不 force（first push 用 -u）
12. createPullRequest：复用已有 open PR 或开 draft PR
13. tagLastPublishLocally：在你本地仓库 HEAD 打 ztools-last-publish 标签
```

### 智能 commit / PR 标题

CLI 会读取你本地 `ztools-last-publish..HEAD` 之间的 commit subjects（即"自上次发布以来你写了哪些 commit"），按以下规则组装：

| subjects 数量 | PR 标题 | fork 端 commit message |
|---|---|---|
| 0 | `Add/Update plugin <名称> v<版本>` | 同 PR 标题 |
| 1 | `Add/Update plugin <名称> v<版本>` | **直接用你的 commit subject 原文** |
| ≥2 | `Add/Update plugin <名称> v<版本>` | fallback 标题 + bullet list 列出所有 subject |

**关键设计**：PR 标题永远是规整的 `Add/Update ...` 格式，方便维护者扫 PR 列表。详细语义放在 commit body 里，审核者点进 Commits tab 仍能看到你的原话。

### Add vs Update 自动判定

CLI 调 `GET /repos/ZToolsCenter/ZTools-plugins/contents/plugins/<插件 ID>`：

- **404** → 上游没这个目录 → **Add**
- **200** → 上游已合并过此插件 → **Update**

> 这比"看 fork 分支是否存在"更准确：合并后分支被自动删除时仍能正确报告 Update。

API 网络异常时退化为 Add（保守策略，避免误导）。

## CHANGELOG.md 处理

### 自动抽取

如果你的项目根目录有 `CHANGELOG.md`，CLI 会按以下规则抓出"本次变更"内容注入到 PR description：

1. 找到匹配当前版本的标题（支持 `## 0.1.0`、`## v0.1.0`、`## [0.1.0]`、`# 0.1.0` 等多种写法）
2. 抽取该节内容到下一个同级或更高级标题之前
3. 注入到 PR body 的「本次变更」段

边界保护：`0.1.0` 不会误匹配 `0.10.0`，反之亦然。

### 找不到当前版本节怎么办？

CLI 在交互式终端会主动提示：

```
📝 未在 CHANGELOG.md 中找到 v0.3.0 的变更说明
? 选择处理方式 ›
❯ 现在编辑（打开 $EDITOR 录入本次变更）
  跳过（PR 中显示 placeholder，稍后在网页填）
  中止发布
```

**选 "现在编辑"** → CLI 启动 `$EDITOR`（默认 `vi`）打开预填模板的临时文件：

```md
# 请简述 Demo Plugin v0.3.0 的本次变更。
# 以 # 开头的行会被忽略；保存并关闭编辑器即可继续发布。
# 直接关闭（不保存）或留空 → 跳过本次录入。
#
# 例如：
#   ### Added
#   - 新增批量导入
#
#   ### Fixed
#   - 修复空输入崩溃

```

保存退出后，CLI 会再确认是否把这一节写回 `CHANGELOG.md`：

```
? 把这一节写入 CHANGELOG.md（同时自动 git commit）？ › (Y/n)
```

确认 → 在 H1 之后、首个 H2 之前插入新版本节 → `git add CHANGELOG.md && git commit -m "chore(changelog): add vX.Y.Z entry"` → 继续发布主流程。

### 非交互式 / CI 环境

`stdin` 或 `stdout` 不是 TTY 时（CI、`< /dev/null` 重定向等），CLI 不会弹任何 prompt，自动按以下优先级填充 PR 的「本次变更」段：

1. CHANGELOG.md 当前版本节（如有）
2. 本地 commit subjects bullet list（如有）
3. `<!-- 简要描述本次新增 / 更新内容 -->` placeholder

这样 `ztools publish < /dev/null` 在脚本里跑也不会卡。

### 长 CHANGELOG 截断

如果当前版本节找不到、且整个 CHANGELOG 文件超过 80 行，CLI 只截前 50 行注入并附 `_…(CHANGELOG 已截断，完整内容请见仓库)_` 标记，避免 PR description 过长。

## PR description 模板

每个 PR 自动生成的 description 包含 4 节：

```md
## 插件信息

- **名称**: ...
- **插件ID**: ...
- **版本**: ...
- **描述**: ...
- **作者**: ...
- **类型**: 新增 / 更新

## 本次变更

{CHANGELOG 节 / commit subjects / placeholder}

## 截图 / 演示

<!-- 如果是新插件或包含界面变化，请附 1-2 张截图或 GIF -->

## 自检清单

- [ ] plugin.json 的 name / title / version / description / author 字段均已检查
- [ ] 已移除调试日志、未使用文件、敏感信息（.env、token、密钥等）
- [ ] 本次 PR 的 diff 仅涉及 `plugins/<id>/` 目录
- [ ] 已在本地 ZTools 客户端实际加载并测试过此插件，主要功能正常
- [ ] 同意以仓库声明的开源协议发布此插件
```

CLI 把所有可自动生成的部分都填好；**截图、自检清单勾选、Ready for review 切换**这三件事必须你手动到 PR 网页上完成。

## 增量发布：远端只追加，不改写

### 每次 publish 远端发生什么

| 场景 | 远端分支变化 |
|---|---|
| 首次 publish | 创建 `plugin/<id>` 分支，1 个 commit |
| 后续 publish（有改动）| 在分支末尾 fast-forward 追加 1 个 commit，旧 commit SHA 不变 |
| 后续 publish（无改动）| 不动分支；如果当前没有 open PR，会基于现有分支重开一个 |
| 审核者直推后 publish | 被拒 → 提示跑 `pull-contributions` |

### 为什么不 force-push

force-push 会让审核者本地 checkout 的分支无法 fast-forward、PR 评论上下文错位、其他贡献者直推的 commit 被覆盖。Raycast 也是这么设计的。

## `ztools pull-contributions`

当审核者或其他贡献者直接在你的 PR 分支上推送过 commit，下次 `ztools publish` 会被拒：

```
❌ 发布失败
错误: 远端 plugin/<id> 分支有你本地缓存中没有的新 commit。
请先把这些改动同步回本地，再次发布：
  $ ztools pull-contributions
  $ ztools publish
```

### 工作机制（三方合并）

1. 校验工作区干净 + 找到本地的 `ztools-last-publish` 标签作为 merge base
2. 拉取 fork 端 plugin 分支最新内容
3. 在你本地仓库新建临时分支 `ztools/pull-<时间戳>`，从 `ztools-last-publish` 出发
4. 把 fork 当前文件镜像到临时分支并 commit "Pull contributions from PR"
5. 切回原分支，`git merge --no-ff` 临时分支 → 触发 git 三方合并
6. 不冲突的文件 → 自动并入；冲突文件 → 暴露给你手工解决

### 合并示例

设上次发布后：

- **你本地**：在 `index.js` 末尾加了一行 `// my change`，对 `util.ts` 加了一个新函数
- **fork PR 分支**：审核者在 `index.js` 末尾加了 `// reviewer fix`，新建了 `REVIEWER.md`

`ztools pull-contributions` 之后：

- `util.ts` ：保留你的新函数（双方无冲突，自动合并）
- `REVIEWER.md`：被并入你本地（双方无冲突，自动合并）
- `index.js`：触发冲突，文件里出现 `<<<<<<< HEAD` / `=======` / `>>>>>>>` 标记，需要你手工编辑后 `git add` + `git commit`

### 冲突时怎么办

CLI 会停在合并未完成状态并提示：

```
❌ 合并出现冲突，需要你手工解决。
  当前处于合并未完成状态：
  - 临时分支: ztools/pull-1700000000000

  解决步骤：
    1) 编辑冲突文件 → git add <文件>
    2) git commit  完成合并
    3) 然后再 ztools publish

  或者放弃此次拉取：git merge --abort && git branch -D ztools/pull-1700000000000
```

按提示走即可。解决冲突后再 `ztools publish` 就能继续追加发布。

## 故障排查

### 推送被拒：`refusing to allow an OAuth App to ... workflow`

中心仓库 main 含 `.github/workflows/*.yml`，OAuth token 必须有 `workflow` scope。CLI 默认请求该 scope；如果你是从老版本升级上来的、本地 token 没这个 scope：

```bash
# 清掉旧 token，重新授权一次（这次会要求 workflow scope）
rm ~/.config/ztools/cli-config.json
ztools publish
```

### `merge-upstream` 422 错误

通常是 fork main 已经偏离上游（你手动改过 fork 的 main）。处理：

```bash
# 进入 fork 缓存
cd ~/.config/ztools/ZTools-plugins
git checkout main
git fetch upstream
git reset --hard upstream/main
git push -f origin main
```

或更简单：删除本地 fork 缓存 + 重新发布

```bash
rm -rf ~/.config/ztools/ZTools-plugins
ztools publish
```

### 工作区有未提交改动

CLI 拒绝带脏工作区发布：

```
❌ 发布失败
错误: 工作区存在未提交的改动，请先 commit 或 discard 后再发布
```

按字面意思 `git commit` 或 `git restore` 处理即可。

### 想看 CLI 的本地缓存仓库

所有 fork 操作发生在 `~/.config/ztools/ZTools-plugins/`，里面是个普通 git 仓库，可以正常 `git log` / `git branch -a` 检查。

### 想完全重置

```bash
rm -rf ~/.config/ztools/                # 清掉 token + fork 缓存
git tag -d ztools-last-publish 2>/dev/null  # 清掉本地 publish 标签
```

下次 `ztools publish` 会重走 OAuth + 重新 clone fork。

## 相关链接

- [ztools-plugin-cli (npm)](https://www.npmjs.com/package/@ztools-center/plugin-cli)
- [ZTools-plugins 中心仓库](https://github.com/ZToolsCenter/ZTools-plugins)
- [GitHub merge-upstream API](https://docs.github.com/en/rest/branches/branches#sync-a-fork-branch-with-the-upstream-repository)
