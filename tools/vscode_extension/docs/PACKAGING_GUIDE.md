# ObjWatch Visualizer 打包指南

## 概述

本文档提供 ObjWatch Visualizer VSCode 扩展的打包和分发指南，包括从源码构建、打包为 VSIX 文件以及安装方法。

## 打包工具准备

### 安装依赖

确保已安装 Node.js (版本 14 或更高) 和 npm。

```bash
# 检查 Node.js 版本
node --version

# 检查 npm 版本  
npm --version
```

### 安装项目依赖

```bash
# 进入扩展目录
cd tools/vscode_extension

# 安装依赖
npm install
```

## 打包流程

ObjWatch Visualizer 提供了两种打包方法：

### 方法一：使用自定义打包脚本（推荐，兼容 Node.js 18+）

由于 Node.js 版本兼容性问题，我们提供了自定义打包脚本，无需依赖外部工具：

```bash
# 一键构建（编译 + 打包）
npm run build
```

此命令将：
1. 编译 TypeScript 代码到 `out/` 目录
2. 使用自定义脚本创建 VSIX 文件到 `dist/` 目录

### 方法二：使用 vsce 工具（需要 Node.js 20+）

如果您的环境支持 Node.js 20+，也可以使用官方 vsce 工具：

```bash
# 编译 TypeScript 代码
npm run compile

# 打包扩展为 VSIX 文件
npm run package
```

打包成功后，VSIX 文件将生成在 `dist/` 目录中，文件名为 `objwatch-visualizer-1.0.0.vsix`。

### 3. 一键构建（推荐）

```bash
# 编译并打包（一步完成）
npm run build
```

## 从源码安装

### 方法一：使用 VSIX 文件安装

1. **生成 VSIX 文件**（如果尚未生成）：
   ```bash
   npm run build
   ```

2. **在 VSCode 中安装**：
   - 打开 VSCode
   - 按 `Ctrl+Shift+P` 打开命令面板
   - 输入 "Extensions: Install from VSIX..."
   - 选择生成的 `dist/objwatch-visualizer-1.0.0.vsix` 文件
   - 重启 VSCode

### 方法二：开发模式安装（用于调试）

1. **克隆仓库**：
   ```bash
   git clone <repository-url>
   cd objwatch/tools/vscode_extension
   ```

2. **安装依赖**：
   ```bash
   npm install
   ```

3. **编译代码**：
   ```bash
   npm run compile
   ```

4. **在 VSCode 中调试**：
   - 打开扩展目录
   - 按 `F5` 启动调试模式
   - 新窗口中将加载开发版本的扩展

### 方法三：命令行安装

```bash
# 使用 code 命令安装 VSIX 文件
code --install-extension dist/objwatch-visualizer-1.0.0.vsix
```

## 发布到 Marketplace

### 准备工作

1. **创建发布者账户**：
   - 访问 [Azure DevOps](https://azure.microsoft.com/services/devops/)
   - 创建组织和个人访问令牌 (PAT)

2. **配置发布者**：
   ```bash
   # 安装 vsce
   npm install -g @vscode/vsce
   
   # 创建发布者
   vsce create-publisher <publisher-name>
   
   # 登录
   vsce login <publisher-name>
   ```

### 发布扩展

```bash
# 发布到 Marketplace
npm run publish
```

## 版本管理

### 更新版本号

在 `package.json` 中更新版本号：

```json
{
  "version": "1.0.1"
}
```

### 版本命名规范

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

## 配置说明

### package.json 关键配置

```json
{
  "name": "objwatch-visualizer",           // 扩展标识符
  "displayName": "ObjWatch Visualizer",    // 显示名称
  "version": "1.0.0",                       // 版本号
  "publisher": "objwatch",                 // 发布者名称
  "engines": {
    "vscode": "^1.60.0"                    // VSCode 版本要求
  }
}
```

### 打包配置

VSIX 打包会自动包含：
- `package.json` 文件
- `out/` 目录中的编译后代码
- `media/` 目录中的资源文件
- 排除 `node_modules/` 和开发文件

## 故障排除

### 常见问题

#### 1. 打包失败：缺少依赖

**错误信息**：
```
Error: Cannot find module '@vscode/vsce'
```

**解决方案**：
```bash
npm install @vscode/vsce --save-dev
```

#### 2. 版本冲突

**错误信息**：
```
Error: Extension version already exists
```

**解决方案**：更新 `package.json` 中的版本号。

#### 3. 文件大小限制

**错误信息**：
```
Error: Package size exceeds the limit
```

**解决方案**：
- 优化资源文件大小
- 排除不必要的文件
- 使用 `.vscodeignore` 文件

### 调试技巧

#### 检查打包内容

```bash
# 查看 VSIX 文件内容（Linux/Mac）
unzip -l dist/objwatch-visualizer-1.0.0.vsix

# 查看打包配置
vsce show <extension-id>
```

#### 验证扩展

```bash
# 验证扩展元数据
vsce verify

# 检查依赖关系
npm ls --depth=0
```

## 自动化构建

### GitHub Actions 示例

创建 `.github/workflows/release.yml`：

```yaml
name: Release Extension
on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
    - name: Install dependencies
      run: |
        cd tools/vscode_extension
        npm install
    - name: Build extension
      run: |
        cd tools/vscode_extension
        npm run build
    - name: Upload VSIX
      uses: actions/upload-artifact@v2
      with:
        name: extension
        path: tools/vscode_extension/dist/*.vsix
```

## 最佳实践

### 1. 版本控制
- 使用语义化版本控制
- 为每个发布创建 Git 标签
- 维护更新日志 (CHANGELOG.md)

### 2. 测试验证
- 在打包前运行完整测试
- 在不同 VSCode 版本上测试兼容性
- 验证安装和卸载流程

### 3. 文档维护
- 更新 README 中的版本信息
- 提供清晰的安装说明
- 记录已知问题和限制

### 4. 安全考虑
- 定期更新依赖项
- 扫描安全漏洞
- 遵循 VSCode 扩展安全指南

---

*打包指南最后更新：2025年*