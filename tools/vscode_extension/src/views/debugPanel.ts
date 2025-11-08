import * as vscode from 'vscode';
import { PerformanceMonitor, ErrorHandler, MemoryOptimizer } from '../utils/performance';

export class DebugPanel {
    private static _panel: vscode.WebviewPanel | undefined;
    private static _isVisible: boolean = false;
    private static _updateInterval: NodeJS.Timeout | undefined;

    static createOrShow(context: vscode.ExtensionContext): void {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (DebugPanel._panel) {
            DebugPanel._panel.reveal(column);
            return;
        }

        DebugPanel._panel = vscode.window.createWebviewPanel(
            'objwatchDebug',
            'ObjWatch Debug Panel',
            column || vscode.ViewColumn.Two,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        DebugPanel._panel.onDidDispose(() => {
            DebugPanel._panel = undefined;
            DebugPanel._isVisible = false;
            if (DebugPanel._updateInterval) {
                clearInterval(DebugPanel._updateInterval);
            }
        });

        DebugPanel._isVisible = true;
        DebugPanel.updateContent();
        
        // Update every 2 seconds
        DebugPanel._updateInterval = setInterval(() => {
            if (DebugPanel._isVisible && DebugPanel._panel) {
                DebugPanel.updateContent();
            }
        }, 2000);

        context.subscriptions.push(DebugPanel._panel);
    }

    static updateContent(): void {
        if (!DebugPanel._panel) {
            return;
        }

        const performanceMonitor = PerformanceMonitor.getInstance();
        const errorHandler = ErrorHandler.getInstance();
        
        const performanceStats = performanceMonitor.getPerformanceStats();
        const errorStats = errorHandler.getErrorStats();
        const memoryStats = MemoryOptimizer.getMemoryStats();
        
        const performanceRecommendations = performanceMonitor.getPerformanceRecommendations();
        const errorRecoverySuggestions = errorHandler.getErrorRecoverySuggestions();

        DebugPanel._panel.webview.html = DebugPanel.getHtml(
            performanceStats,
            errorStats,
            memoryStats,
            performanceRecommendations,
            errorRecoverySuggestions
        );
    }

    private static getHtml(
        performanceStats: any,
        errorStats: any,
        memoryStats: any,
        performanceRecommendations: string[],
        errorRecoverySuggestions: string[]
    ): string {
        return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ObjWatch Debug Panel</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            margin: 0;
            padding: var(--vscode-padding);
            background-color: var(--vscode-editor-background);
            color: var(--vscode-foreground);
            line-height: var(--vscode-line-height);
        }
        
        .section {
            background: var(--vscode-panel-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: var(--vscode-border-radius);
            padding: var(--vscode-padding);
            margin-bottom: var(--vscode-padding);
        }
        
        .section-title {
            font-size: calc(var(--vscode-font-size) + 2px);
            font-weight: 600;
            margin-bottom: calc(var(--vscode-padding) / 2);
            color: var(--vscode-textLink-foreground);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: calc(var(--vscode-padding) / 2);
            margin-bottom: calc(var(--vscode-padding) / 2);
        }
        
        .stat-item {
            background: var(--vscode-input-background);
            padding: calc(var(--vscode-padding) / 2);
            border-radius: var(--vscode-border-radius);
            border-left: 3px solid var(--vscode-textLink-foreground);
        }
        
        .stat-label {
            font-size: calc(var(--vscode-font-size) - 2px);
            color: var(--vscode-descriptionForeground);
            margin-bottom: 3px;
        }
        
        .stat-value {
            font-size: calc(var(--vscode-font-size) + 2px);
            font-weight: 600;
        }
        
        .warning {
            color: var(--vscode-inputValidation-warningForeground);
            border-left-color: var(--vscode-inputValidation-warningBorder);
        }
        
        .error {
            color: var(--vscode-inputValidation-errorForeground);
            border-left-color: var(--vscode-inputValidation-errorBorder);
        }
        
        .success {
            color: var(--vscode-testing-iconPassed);
            border-left-color: var(--vscode-testing-iconPassed);
        }
        
        .recommendation-list {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        
        .recommendation-item {
            padding: calc(var(--vscode-padding) / 4) 0;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .recommendation-item:last-child {
            border-bottom: none;
        }
        
        .timestamp {
            font-size: calc(var(--vscode-font-size) - 3px);
            color: var(--vscode-descriptionForeground);
            margin-top: calc(var(--vscode-padding) / 4);
        }
        
        .refresh-info {
            text-align: center;
            font-size: calc(var(--vscode-font-size) - 2px);
            color: var(--vscode-descriptionForeground);
            margin-top: var(--vscode-padding);
        }
    </style>
</head>
<body>
    <div class="section">
        <div class="section-title">Performance Statistics</div>
        <div class="stats-grid">
            <div class="stat-item ${performanceStats.averageRenderTime > 500 ? 'warning' : 'success'}">
                <div class="stat-label">Average Render Time</div>
                <div class="stat-value">${performanceStats.averageRenderTime.toFixed(2)} ms</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Max Render Time</div>
                <div class="stat-value">${performanceStats.maxRenderTime} ms</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Total Events</div>
                <div class="stat-value">${performanceStats.eventCount}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Render Count</div>
                <div class="stat-value">${performanceStats.renderCount}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Events/Second</div>
                <div class="stat-value">${performanceStats.eventsPerSecond.toFixed(2)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Total Render Time</div>
                <div class="stat-value">${(performanceStats.totalRenderTime / 1000).toFixed(2)} s</div>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Memory Statistics</div>
        <div class="stats-grid">
            <div class="stat-item ${memoryStats.heapUsedMB > 200 ? 'warning' : 'success'}">
                <div class="stat-label">Heap Used</div>
                <div class="stat-value">${memoryStats.heapUsedMB.toFixed(2)} MB</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Heap Total</div>
                <div class="stat-value">${memoryStats.heapTotalMB.toFixed(2)} MB</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">External Memory</div>
                <div class="stat-value">${memoryStats.externalMB.toFixed(2)} MB</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Cleanup Count</div>
                <div class="stat-value">${memoryStats.cleanupCount}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Last Cleanup</div>
                <div class="stat-value">${memoryStats.lastCleanupTime ? new Date(memoryStats.lastCleanupTime).toLocaleTimeString() : 'Never'}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title ${errorStats.errorCount > 0 ? 'error' : 'success'}">Error Statistics (${errorStats.errorCount} errors)</div>
        <div class="stats-grid">
            <div class="stat-item ${errorStats.errorCount > 0 ? 'error' : 'success'}">
                <div class="stat-label">Total Errors</div>
                <div class="stat-value">${errorStats.errorCount}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Last Error</div>
                <div class="stat-value">${errorStats.lastError || 'None'}</div>
            </div>
        </div>
        
        ${errorStats.recentErrors.length > 0 ? `
            <div style="margin-top: 10px;">
                <div style="font-size: 14px; margin-bottom: 8px;">Recent Errors:</div>
                ${errorStats.recentErrors.map((error: any) => `
                    <div class="recommendation-item">
                        <strong>${error.context}</strong>: ${error.message}
                        <div class="timestamp">${new Date(error.timestamp).toLocaleString()}</div>
                    </div>
                `).join('')}
            </div>
        ` : ''}
    </div>

    ${performanceRecommendations.length > 0 ? `
    <div class="section">
        <div class="section-title">Performance Recommendations</div>
        <ul class="recommendation-list">
            ${performanceRecommendations.map(rec => `
                <li class="recommendation-item">${rec}</li>
            `).join('')}
        </ul>
    </div>
    ` : ''}

    ${errorRecoverySuggestions.length > 0 ? `
    <div class="section">
        <div class="section-title">Error Recovery Suggestions</div>
        <ul class="recommendation-list">
            ${errorRecoverySuggestions.map(suggestion => `
                <li class="recommendation-item">${suggestion}</li>
            `).join('')}
        </ul>
    </div>
    ` : ''}

    <div class="refresh-info">
        Last updated: ${new Date().toLocaleString()}
        <br>
        Auto-refreshes every 2 seconds
    </div>
</body>
</html>`;
    }

    static isVisible(): boolean {
        return DebugPanel._isVisible;
    }

    static dispose(): void {
        if (DebugPanel._panel) {
            DebugPanel._panel.dispose();
        }
        if (DebugPanel._updateInterval) {
            clearInterval(DebugPanel._updateInterval);
        }
    }
}