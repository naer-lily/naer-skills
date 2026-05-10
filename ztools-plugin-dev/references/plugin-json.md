# plugin.json 配置

plugin.json 文件是插件应用的配置文件，它是最重要的一个文件，用来定义这个插件应用将如何与 ZTools 集成。 每当你创建一个插件应用时，都需要从创建一个 plugin.json 文件开始。

## 配置文件格式
plugin.json 文件是一个标准的 JSON 文件，它的结构如下：
```json
{
  "name": "example",
  "title": "示例插件",
  "description": "这是一个示例插件",
  "version": "1.0.0",
  "main": "index.html",
  "logo": "logo.png",
  "preload": "preload.js",
  "features": [
    {
      "code": "hello",
      "explain": "hello world",
      "cmds": ["hello", "你好"]
    }
  ]
}
```

## 基础字段说明

### `name`
- 类型：`string`
- 必填：是

插件应用唯一标识（ID），用于在系统中唯一标识该插件。

### `title`
- 类型：`string`
- 必填：是

插件应用显示名称，在 ZTools 中展示给用户看的标题。

### `description`
- 类型：`string`
- 必填：否

插件应用描述

### `version`
- 类型：`string`
- 必填：否

插件应用版本

### `main`
- 类型：`string`
- 必填：是

插件入口，可以是一个相对于 `plugin.json` 的相对路径的 `.html` 文件，或者是一个在线地址

### `logo`
- 类型：`string`
- 必填：是

插件应用 Logo，必须为 png 或 jpg 文件

### `preload`
- 类型：`string`
- 必填：是

预加载 js 文件，这是一个关键文件，你可以在此文件内调用 nodejs、 electron 提供的 api。
查看更多关于 [preload.js](./preload.js)

## 开发模式字段说明

### `development`
- 类型：`object`
- 必填：否

开发模式下的配置，对象的同名字段会覆盖基础配置字段。

### `development.main`
- 类型：`string`
- 必填：否

开发模式下，插件应用的入口文件，与基础配置字段 main 字段相同

## 插件应用功能字段说明
### `features`
- 类型：`Array<Feature>`
- 必填：否

插件功能列表，定义插件支持的功能及其触发方式。

### `feature.code`
- 类型：`string`
- 说明：功能唯一标识，用于区分不同功能。

### `feature.explain`
- 类型：`string`
- 说明：功能说明，显示在搜索结果中。

### `feature.cmds`
- 类型：`Array<string | RegexCmd | OverCmd | ImgCmd | FilesCmd>`
- 说明：触发指令列表。可以是简单的字符串，也可以是匹配对象（正则、全局、图片、文件等）。

### `feature.platform`
- 类型：`Array<'win32' | 'darwin' | 'linux'>`
- 必填：否
- 说明：支持的平台。如果不填，默认支持所有平台。

## 指令类型详解

### 文本指令 (String)
最简单的触发方式，当用户输入完全匹配该文本时触发。
```json
{
  "features": [
    {
      "code": "hello",
      "explain": "打招呼",
      "cmds": ["hello", "你好"]
    }
  ]
}
```

### 正则表达式指令 (RegexCmd)
使用正则表达式匹配用户输入。
```json
{
  "features": [
    {
      "code": "color",
      "explain": "颜色预览",
      "cmds": [
        {
          "type": "regex",
          "label": "颜色预览",
          "match": "/^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$/i",
          "minLength": 4
        }
      ]
    }
  ]
}
```
- `type`: 固定为 `"regex"`
- `label`: 匹配成功后显示的名称
- `match`: 正则表达式字符串 (例如 `"/^abc/i"`)
- `minLength`: 触发匹配的最小字符长度

### 全局匹配指令 (OverCmd)
匹配任意文本，通常用于需要处理所有输入的场景（如翻译、搜索插件）。
```json
{
  "features": [
    {
      "code": "translate",
      "explain": "翻译",
      "cmds": [
        {
          "type": "over",
          "label": "翻译",
          "exclude": "/^exclude/i",
          "minLength": 1,
          "maxLength": 1000
        }
      ]
    }
  ]
}
```
- `type`: 固定为 `"over"`
- `label`: 显示的名称
- `exclude`: (可选) 排除匹配的正则表达式字符串
- `minLength`: (可选) 最小字符数
- `maxLength`: (可选) 最大字符数 (默认 10000)

### 图片匹配指令 (ImgCmd)
当用户粘贴图片到 ZTools 时触发，用于处理图片的插件（如图片压缩、格式转换、OCR 识别等）。

```json
{
  "features": [
    {
      "code": "image-process",
      "explain": "图片处理",
      "cmds": [
        {
          "type": "img",
          "label": "图片处理"
        }
      ]
    }
  ]
}
```
- `type`: 固定为 `"img"`
- `label`: 显示的名称

**使用场景**：
- 图片压缩
- 图片格式转换
- OCR 文字识别
- 图片编辑
- 图片上传

### 文件匹配指令 (FilesCmd)
当用户粘贴文件或文件夹到 ZTools 时触发，支持多种过滤条件来精确匹配文件。

```json
{
  "features": [
    {
      "code": "file-process",
      "explain": "文件处理",
      "cmds": [
        {
          "type": "files",
          "label": "批量重命名",
          "fileType": "file",
          "extensions": ["txt", "md", "json"],
          "match": "/^test/i",
          "minLength": 1,
          "maxLength": 100
        }
      ]
    }
  ]
}
```

- `type`: 固定为 `"files"`
- `label`: 显示的名称
- `fileType`: (可选) 文件类型，`"file"` 表示只匹配文件，`"directory"` 表示只匹配文件夹。不指定则文件和文件夹都匹配
- `extensions`: (可选) 文件扩展名数组，只对文件有效（不检查文件夹）。例如 `["jpg", "png", "gif"]`
- `match`: (可选) 匹配文件(夹)名称的正则表达式字符串。例如 `"/^test/i"` 表示匹配以 "test" 开头的文件名（不区分大小写）
- `minLength`: (可选) 最少文件数，默认 1
- `maxLength`: (可选) 最多文件数，默认 10000

**匹配规则**：
1. 首先检查文件数量是否在 `minLength` 和 `maxLength` 范围内
2. 然后检查每个文件是否满足以下条件（如果指定）：
   - 文件类型（`fileType`）
   - 文件扩展名（`extensions`）
   - 文件名正则匹配（`match`）

**使用场景**：
- 批量文件重命名
- 文件格式转换
- 文件压缩打包
- 文件批量上传
- 代码文件批量处理
