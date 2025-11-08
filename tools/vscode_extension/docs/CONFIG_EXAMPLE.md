# ObjWatch Visualizer 配置示例

## 概述

本文档提供 ObjWatch Visualizer 扩展的完整配置示例，帮助用户根据具体需求优化扩展行为。

## 基础配置

### 最小配置示例

```json
{
    "objwatchVisualizer.autoRefresh": true,
    "objwatchVisualizer.maxEvents": 1000,
    "objwatchVisualizer.refreshInterval": 1000
}
```

### 推荐配置（平衡性能与功能）

```json
{
    "objwatchVisualizer.autoRefresh": true,
    "objwatchVisualizer.maxEvents": 2000,
    "objwatchVisualizer.refreshInterval": 500,
    "objwatchVisualizer.showLineNumbers": true,
    "objwatchVisualizer.theme": "dark",
    "objwatchVisualizer.memoryOptimization": true,
    "objwatchVisualizer.errorRecovery": true
}
```

## 性能优化配置

### 大文件处理配置

适用于处理超过 10MB 的大型 `objwatch.json` 文件：

```json
{
    "objwatchVisualizer.maxEvents": 500,
    "objwatchVisualizer.refreshInterval": 2000,
    "objwatchVisualizer.memoryOptimization": true,
    "objwatchVisualizer.autoRefresh": true,
    "objwatchVisualizer.eventRetention": "recent"
}
```

### 高性能配置

适用于需要实时监控的场景：

```json
{
    "objwatchVisualizer.maxEvents": 5000,
    "objwatchVisualizer.refreshInterval": 100,
    "objwatchVisualizer.autoRefresh": true,
    "objwatchVisualizer.showLineNumbers": false,
    "objwatchVisualizer.memoryOptimization": false
}
```

## 调试配置

### 开发调试配置

适用于扩展开发和问题诊断：

```json
{
    "objwatchVisualizer.debug": true,
    "objwatchVisualizer.logLevel": "verbose",
    "objwatchVisualizer.autoRefresh": true,
    "objwatchVisualizer.maxEvents": 100,
    "objwatchVisualizer.showPerformanceStats": true
}
```

### 生产环境配置

适用于稳定运行的生产环境：

```json
{
    "objwatchVisualizer.debug": false,
    "objwatchVisualizer.logLevel": "warn",
    "objwatchVisualizer.autoRefresh": true,
    "objwatchVisualizer.maxEvents": 1000,
    "objwatchVisualizer.memoryOptimization": true,
    "objwatchVisualizer.errorRecovery": true
}
```

## 主题配置

### 深色主题配置

```json
{
    "objwatchVisualizer.theme": "dark",
    "objwatchVisualizer.eventColors": {
        "RUN": "#4EC9B0",
        "END": "#569CD6", 
        "UPD": "#CE9178",
        "APD": "#B5CEA8",
        "POP": "#D7BA7D"
    }
}
```

### 浅色主题配置

```json
{
    "objwatchVisualizer.theme": "light",
    "objwatchVisualizer.eventColors": {
        "RUN": "#098658",
        "END": "#0451A5",
        "UPD": "#A31515",
        "APD": "#795E26",
        "POP": "#267F99"
    }
}
```

### 自定义主题配置

```json
{
    "objwatchVisualizer.theme": "custom",
    "objwatchVisualizer.customTheme": {
        "background": "#1E1E1E",
        "text": "#D4D4D4",
        "border": "#464647",
        "highlight": "#2A2D2E",
        "eventColors": {
            "RUN": "#4EC9B0",
            "END": "#569CD6",
            "UPD": "#CE9178", 
            "APD": "#B5CEA8",
            "POP": "#D7BA7D"
        }
    }
}
```

## 高级配置

### 文件监听配置

```json
{
    "objwatchVisualizer.fileWatch": {
        "enabled": true,
        "pollingInterval": 1000,
        "debounceDelay": 100,
        "fileSizeLimit": 10485760
    }
}
```

### 内存管理配置

```json
{
    "objwatchVisualizer.memory": {
        "optimizationEnabled": true,
        "cleanupInterval": 30000,
        "memoryThreshold": 524288000,
        "eventRetentionPolicy": "recent"
    }
}
```

### 错误处理配置

```json
{
    "objwatchVisualizer.errorHandling": {
        "recoveryEnabled": true,
        "maxRetryAttempts": 3,
        "retryDelay": 1000,
        "logErrors": true,
        "showUserNotifications": true
    }
}
```

## 工作区特定配置

### 项目A配置（小型项目）

```json
{
    "objwatchVisualizer.maxEvents": 500,
    "objwatchVisualizer.refreshInterval": 1000,
    "objwatchVisualizer.autoRefresh": true
}
```

### 项目B配置（大型项目）

```json
{
    "objwatchVisualizer.maxEvents": 2000,
    "objwatchVisualizer.refreshInterval": 2000,
    "objwatchVisualizer.memoryOptimization": true,
    "objwatchVisualizer.autoRefresh": true
}
```

## 配置说明

### 关键配置参数说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `autoRefresh` | boolean | true | 是否自动刷新界面 |
| `maxEvents` | number | 1000 | 最大显示事件数量 |
| `refreshInterval` | number | 1000 | 刷新间隔（毫秒） |
| `showLineNumbers` | boolean | true | 是否显示行号 |
| `theme` | string | "dark" | 界面主题 |
| `memoryOptimization` | boolean | true | 内存优化开关 |
| `errorRecovery` | boolean | true | 错误恢复开关 |
| `debug` | boolean | false | 调试模式开关 |
| `logLevel` | string | "info" | 日志级别 |

### 性能调优建议

1. **小文件（<1MB）**：使用默认配置即可
2. **中等文件（1-10MB）**：适当增加 `maxEvents` 到 2000-3000
3. **大文件（>10MB）**：减少 `maxEvents` 到 500，增加 `refreshInterval`
4. **实时监控**：减少 `refreshInterval` 到 100-200ms
5. **节省资源**：增加 `refreshInterval` 到 2000-5000ms

### 故障排除配置

如果遇到性能问题，可以尝试以下配置：

```json
{
    "objwatchVisualizer.maxEvents": 100,
    "objwatchVisualizer.refreshInterval": 5000,
    "objwatchVisualizer.memoryOptimization": true,
    "objwatchVisualizer.autoRefresh": false
}
```

## 配置验证

配置完成后，可以通过以下方式验证配置是否生效：

1. 打开调试面板查看当前配置状态
2. 检查性能统计数据是否改善
3. 观察内存使用情况变化
4. 验证错误处理机制是否正常工作

## 配置备份和恢复

建议将重要配置备份：

```bash
# 备份VSCode设置
code --list-extensions > extensions.txt
# 配置存储在 settings.json 文件中
```

---

*配置示例最后更新：2025年*