TaskService 主要是我自己实现的，其他的都是 AI 写的。

↓我闺蜜（不是

# naer-todo-skill: 智能待办任务管理器 📝

> "时间就像书架上的书籍，一页一页地翻过，而任务是书签，标记着阅读的进度。"

## 简介

**naer-todo-skill** 是一个专为AI助理设计的待办任务管理CLI工具，通过滴答清单（dida365）后端提供任务同步功能。它采用智能筛选逻辑，让任务管理更加直观高效。

## ✨ 主要特性

- **智能任务筛选**：自动识别今日任务、过期任务和未安排任务
- **简洁命令行接口**：专为AI助理优化，无需复杂参数
- **完整CRUD操作**：创建、读取、更新、删除任务
- **重复任务支持**：使用iCalendar RRULE语法创建周期性重复任务
- **优先级管理**：支持无、低、中、高四级优先级
- **分类管理**：任务可按分类组织
- **定时提醒集成**：支持配置每日进度提醒

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 有效的滴答清单账号

### 环境配置

在使用前，需要设置以下环境变量：

```bash
# 获取滴答清单API令牌
export DIDA_TOKEN="your_dida365_api_token"

# 设置项目ID（默认为Inbox）
export DIDA_PROJECT_ID="your_project_id"
```

**如何获取API令牌：**
1. 访问 [滴答清单开发者平台](https://developer.dida365.com/)
2. 注册开发者账号
3. 创建应用并获取API令牌
4. 获取项目ID（可选，默认为收件箱）

## 📖 使用示例

### 查看今日任务
```bash
python scripts/main.py list-today
```
智能筛选今日到期、已过期及未安排日期的所有未完成任务。

### 查看所有未完成任务
```bash
python scripts/main.py list-all
```

### 创建新任务
```bash
python scripts/main.py create \
  --title "准备周报" \
  --description "整理本周工作进展和下周计划" \
  --date 2026-03-22 \
  --priority MEDIUM \
  --category-id 69be56b7ebb75f00000003fc
```

### 创建重复任务
```bash
# 每天重复
python scripts/main.py create --title "每日站会" --repeat "RRULE:FREQ=DAILY;INTERVAL=1"

# 每周一重复
python scripts/main.py create --title "周报" --date 2026-04-27 \
  --repeat "RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO"

# 工作日重复
python scripts/main.py create --title "打卡" \
  --repeat "RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR"
```

### 完成任务
```bash
python scripts/main.py complete 69be63fde4b067bb55e38430
```

### 查看任务详情
```bash
python scripts/main.py get 69be63fde4b067bb55e38430
```

## 🔧 完整命令参考

### 任务管理命令
| 命令 | 描述 | 参数 |
|------|------|------|
| `list-today` | 列出今日及过期未完成任务 | 无 |
| `list-all` | 列出所有未完成任务 | 无 |
| `list` | 兼容命令（等同list-today） | 无 |
| `create` | 创建新任务 | `--title` (必需), `--description`, `--date`, `--priority`, `--category-id`, `--repeat` |
| `get <id>` | 查看任务详情 | 任务ID |
| `complete <id>` | 标记任务为已完成 | 任务ID |
| `delete <id>` | 删除任务 | 任务ID |
| `categories` | 列出所有分类 | 无 |

### 优先级选项
- `NONE` - 无优先级
- `LOW` - 低优先级  
- `MEDIUM` - 中优先级
- `HIGH` - 高优先级

## ⏰ 定时任务配置

工具支持配置每日提醒，示例配置：

```bash
# 每日12:00提醒
0 12 * * * cd /path/to/skill && python scripts/main.py list-today

# 每日18:00总结
0 18 * * * cd /path/to/skill && python scripts/main.py list-today
```

## 🧠 智能筛选逻辑

`list-today` 命令会自动筛选以下任务：

1. **今日到期**：计划日期为今天的任务
2. **已过期**：计划日期早于今天的任务  
3. **未安排**：没有设置计划日期的任务
4. **未完成**：状态为 NORMAL 的所有任务

这样设计使得每日任务管理更加聚焦，避免信息过载。

## 📚 项目结构

```
naer-todo-skill/
├── SKILL.md           # AI助理使用指南
├── scripts/
│   ├── main.py        # 主命令行接口
│   └── TaskService.py # 滴答清单服务封装
└── README.md          # 用户文档（本文档）
```

## 💡 设计理念

这个工具的设计受到了文学作品的启发：就像小说章节需要清晰的结构，任务也需要合理的组织。我们相信：

1. **简洁即美**：最少的命令完成最多的功能
2. **智能筛选**：让工具理解时间的重要性
3. **渐进式提醒**：适时的提醒如同书中的批注，引导而不打扰

## 🐛 故障排除

### 常见问题

**Q: 出现"环境变量未设置"错误**
A: 请检查 `DIDA_TOKEN` 和 `DIDA_PROJECT_ID` 环境变量是否正确设置。

**Q: API请求失败**
A: 检查网络连接，确认API令牌有效且未过期。

**Q: 任务列表为空但网页端有任务**
A: 确认项目ID是否正确，不同项目的任务不会混显。

### 调试模式
设置调试环境变量查看详细日志：
```bash
export DEBUG=true
python scripts/main.py list-today
```

## 📄 许可证与致谢

这个工具基于滴答清单API开发，感谢滴答清单提供稳定的任务同步服务。

> "完成一项任务，就像读完一本书的一章。不必急于翻到最后一页，重要的是理解每一页的内容。" —— 大槻明里

---

*文档最后更新：2026年3月21日*  
*维护者：大槻明里 (生活助理)*