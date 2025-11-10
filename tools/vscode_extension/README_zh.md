<img src="images/objwatch-logo.png" width="128px" alt="ObjWatch Logo">

# ObjWatch Log Viewer - VSCode 扩展插件

\[ [English](README.md) | 中文 \]

专为 ObjWatch 调试日志设计的增强型查看器，提供语法高亮、嵌套结构识别和代码折叠支持。

获取它：[VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=aeeeeeep.objwatch-log-viewer)

## 功能特性

- **语法高亮**：为日志中的行号、事件类型、函数名和变量名等不同元素提供差异化的颜色
- **嵌套结构识别**：基于缩进自动识别日志的层次结构
- **折叠/展开**：支持折叠和展开嵌套日志节点，提高复杂日志的可读性
- **自定义命令**：提供切换折叠和格式化日志的命令

## 事件类型高亮

- `run`：函数执行开始
- `end`：函数执行结束
- `upd`：变量更新
- `apd`：集合元素添加
- `pop`：集合元素移除

## 使用方法

1. 在 VSCode 中打开任何 `.objwatch` 日志文件
2. 扩展将自动激活并应用语法高亮
3. 使用装订线中的折叠/展开控件来折叠/展开嵌套部分

## 配置选项

扩展提供以下配置选项：

- `objwatch-log-viewer.enableFolding`：启用 ObjWatch 日志的代码折叠功能（默认值：true）
- `objwatch-log-viewer.highlightEventTypes`：使用不同颜色高亮显示不同的事件类型（默认值：true）
- `objwatch-log-viewer.enableIndentRainbow`：为 ObjWatch 日志启用缩进彩虹高亮（默认值：true）
- `objwatch-log-viewer.indentRainbowColors`：用于缩进高亮的颜色（默认值：[
  "rgba(255,255,64,0.07)",
  "rgba(127,255,127,0.07)",
  "rgba(255,127,255,0.07)",
  "rgba(79,236,236,0.07)"
]）
- `objwatch-log-viewer.indentRainbowErrorColor`：用于高亮缩进错误的颜色（默认值："rgba(128,32,32,0.3)"）
- `objwatch-log-viewer.indentRainbowIndicatorStyle`：缩进指示器的样式（默认值："classic"，选项："classic"、"light"）

## 日志格式

扩展支持以下结构的 ObjWatch 日志格式：

"{行号} {'  '*call_depth}{事件类型} {对象字符串} {消息字符串}"，如：

```
  69 run __main__.main <- 
  61     run __main__.TestClass.outer_function <- '0':(type)TestClass
  10         upd TestClass.a None -> 10
  ...
  61     end __main__.TestClass.outer_function -> [(list)[200, 3, 4, '... (1 more elements)']]
  69 end __main__.main -> None
```

其中：
- 行号右对齐
- 嵌套级别由每个级别 2 个空格表示

## 开发指南

设置开发环境：

1. 克隆代码库
2. 导航到扩展目录 (`tools/vscode_extension`)
3. 运行 `npm install` 安装依赖
4. 运行 `npx vsce package` 打包扩展
5. 运行 `code --install-extension <path-to-vsix>` 安装扩展
