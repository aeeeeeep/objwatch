# ObjWatch Visualizer - VSCode Extension

一个专业的VSCode扩展，用于可视化ObjWatch生成的JSON日志文件，提供类似`objwatch.log`风格的实时渲染界面。

## 功能特性

### 🎯 核心功能
- **实时渲染**: 将`objwatch.json`文件内容实时渲染为`objwatch.log`风格的可视化页面
- **智能缩进**: 通过CSS渲染实现缩进，而非使用"|"字符
- **折叠/展开**: 支持多级嵌套内容的交互式折叠/展开操作
- **文件监听**: 自动监听文件变化，实时更新可视化界面

### 🚀 性能优化
- **内存管理**: 智能内存优化，支持大文件处理
- **性能监控**: 实时性能统计和优化建议
- **事件限制**: 自动限制显示事件数量，防止性能问题
- **垃圾回收**: 定期内存清理，保持系统稳定

### 🔧 调试工具
- **调试面板**: 实时显示性能统计、内存使用和错误信息
- **错误恢复**: 智能错误处理和恢复机制
- **详细日志**: 完整的调试日志和性能指标

## 快速开始

### 方法一：从 Marketplace 安装（推荐）
1. 在VSCode中打开扩展面板 (`Ctrl+Shift+X`)
2. 搜索 "ObjWatch Visualizer"
3. 点击安装

### 方法二：从源码安装

#### 前提条件
- Node.js 14.0 或更高版本（推荐 Node.js 18+）
- npm 6.0 或更高版本

#### 安装步骤
1. 克隆仓库或下载源码
2. 进入扩展目录：`cd tools/vscode_extension`
3. 安装依赖：`npm install`
4. 编译并打包：`npm run build`
5. 在VSCode中安装VSIX文件：
   - 打开命令面板 (`Ctrl+Shift+P`)
   - 输入 "Extensions: Install from VSIX..."
   - 选择 `dist/objwatch-visualizer-1.0.0.vsix` 文件

#### 一键安装（开发模式）
```bash
cd tools/vscode_extension
npm install && npm run compile
# 然后按 F5 启动调试模式
```

### 使用方法

#### 方法一：通过命令面板
1. 打开一个`objwatch.json`文件
2. 按`Ctrl+Shift+P`打开命令面板
3. 输入 "ObjWatch: Open Visualizer"
4. 按回车键打开可视化界面

#### 方法二：右键菜单
1. 在资源管理器中右键点击`objwatch.json`文件
2. 选择 "Open with ObjWatch Visualizer"

#### 方法三：文件关联
1. 双击`objwatch.json`文件
2. 如果未自动打开，点击右上角的编辑器选择器
3. 选择 "ObjWatch Visualizer"

## 界面说明

### 主界面布局
- **顶部工具栏**: 显示文件信息和基本操作
- **事件列表**: 按时间顺序显示所有事件
- **缩进层次**: 通过CSS实现的多级缩进，清晰展示调用层次
- **颜色编码**: 不同事件类型使用不同颜色标识

### 交互功能
- **折叠/展开**: 点击事件左侧的箭头图标折叠/展开嵌套内容
- **搜索过滤**: 使用浏览器搜索功能 (`Ctrl+F`) 搜索特定内容
- **滚动同步**: 主界面与源代码视图保持同步

## 配置选项

### 扩展设置

在VSCode设置中搜索 "ObjWatch" 可配置以下选项：

- `objwatchVisualizer.maxEvents`: 最大显示事件数量 (默认: 1000)
- `objwatchVisualizer.autoRefresh`: 启用/禁用自动刷新 (默认: true)
- `objwatchVisualizer.refreshInterval`: 刷新间隔毫秒数 (默认: 1000)
- `objwatchVisualizer.showLineNumbers`: 显示/隐藏行号 (默认: true)
- `objwatchVisualizer.theme`: 可视化主题 (默认: "dark")
- `objwatchVisualizer.memoryOptimization`: 内存优化开关 (默认: true)
- `objwatchVisualizer.errorRecovery`: 错误恢复功能 (默认: true)

### 主题配置

ObjWatch Visualizer 使用 VSCode 原生主题变量，确保与当前 IDE 主题完全一致：

#### 主题变量系统
扩展使用以下 VSCode CSS 变量来自动适配当前主题：

**基础变量**
- `--vscode-font-family`: 字体家族
- `--vscode-font-size`: 字体大小
- `--vscode-line-height`: 行高
- `--vscode-padding`: 内边距基准
- `--vscode-border-radius`: 边框圆角

**颜色变量**
- `--vscode-foreground`: 前景色（文本颜色）
- `--vscode-background`: 背景色
- `--vscode-editor-background`: 编辑器背景色
- `--vscode-panel-background`: 面板背景色
- `--vscode-panel-border`: 面板边框色
- `--vscode-descriptionForeground`: 描述文本颜色
- `--vscode-textLink-foreground`: 链接文本颜色

**事件类型颜色**
- `RUN` 事件: `--vscode-textLink-foreground` (蓝色)
- `END` 事件: `--vscode-testing-iconPassed` (绿色)
- `UPD` 事件: `--vscode-inputValidation-warningBorder` (橙色)
- `APD` 事件: `--vscode-symbolIcon-fieldForeground` (紫色)
- `POP` 事件: `--vscode-inputValidation-errorBorder` (红色)

**状态颜色**
- 警告状态: `--vscode-inputValidation-warningForeground`
- 错误状态: `--vscode-inputValidation-errorForeground`
- 成功状态: `--vscode-testing-iconPassed`

#### 主题兼容性
扩展支持所有 VSCode 主题，包括：
- **浅色主题**: Default Light+, Quiet Light, Solarized Light
- **深色主题**: Default Dark+, Monokai, One Dark Pro
- **高对比度主题**: High Contrast, High Contrast Light

#### 自定义主题支持
如果您使用自定义主题，扩展会自动继承主题的 CSS 变量，确保视觉一致性。

### 文件监听

扩展自动监听`objwatch.json`文件变化，支持以下配置：

- 文件变化检测灵敏度
- 文件更新防抖间隔
- 文件大小限制（性能优化）

## 调试工具

### 调试面板

扩展提供了强大的调试面板功能：

1. **打开调试面板**: 
   - 按`Ctrl+Shift+P`打开命令面板
   - 输入 "ObjWatch: Show Debug Panel"
   - 或使用快捷键 `Ctrl+Shift+D`

2. **面板功能**:
   - **性能统计**: 实时显示渲染性能指标
   - **内存使用**: 当前内存占用和优化建议
   - **错误信息**: 最近发生的错误和恢复状态
   - **事件统计**: 各类事件的数量和分布

### 性能监控

扩展内置了完整的性能监控系统：

- **渲染时间**: 监控每次界面更新的渲染耗时
- **内存优化**: 自动清理过期数据，防止内存泄漏
- **事件限制**: 智能限制显示事件数量
- **错误恢复**: 自动检测和恢复可恢复错误

## 故障排除

### 常见问题

1. **文件未找到**: 确保`objwatch.json`文件存在且可访问
2. **性能问题**: 在设置中减少`maxEvents`值
3. **内存问题**: 启用内存优化功能
4. **渲染错误**: 检查JSON文件格式和语法

### 调试模式

启用调试模式获取详细日志：

1. 打开VSCode设置
2. 搜索 "ObjWatch"
3. 启用 "Debug Mode"
4. 在输出面板查看 "ObjWatch Visualizer" 日志

## 开发信息

### 项目结构

```
src/
├── extension.ts          # 扩展入口点
├── models/
│   └── document.ts       # 文档模型和解析逻辑
├── views/
│   ├── editor.ts         # 主编辑器视图
│   ├── debugPanel.ts     # 调试面板视图
│   └── components/       # 可复用组件
└── utils/
    ├── performance.ts    # 性能监控和错误处理
    └── constants.ts      # 常量定义
```

### 文档资源

- **[调试指南](./docs/DEBUG_GUIDE.md)**: 详细的调试工具使用说明
- **[配置示例](./docs/CONFIG_EXAMPLE.md)**: 各种场景的配置示例
- **[打包指南](./docs/PACKAGING_GUIDE.md)**: 扩展打包和分发指南

### 从源码构建

1. 克隆仓库
2. 安装依赖: `npm install`
3. 编译TypeScript: `npm run compile`
4. 运行测试: `npm test`
5. 启动扩展: 在VSCode中按`F5`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure code quality
5. Submit a pull request

## License

This extension is part of the ObjWatch project and follows the same licensing terms.

## Support

For issues and feature requests, please create an issue in the main ObjWatch repository.