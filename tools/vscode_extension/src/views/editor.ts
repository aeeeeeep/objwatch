import * as vscode from 'vscode';
import { ObjWatchDocument, ProcessedEvent, EventProcessor } from '../models/document';
import { PerformanceMonitor, ErrorHandler, MemoryOptimizer } from '../utils/performance';
import { ThemeManager } from '../utils/themeManager';

export class ObjWatchEditor {
    private readonly _context: vscode.ExtensionContext;
    private readonly _document: ObjWatchDocument;
    private readonly _webviewPanel: vscode.WebviewPanel;
    private readonly _themeManager: ThemeManager;
    private _collapsedStates: Set<string> = new Set();
    private _disposables: vscode.Disposable[] = [];

    constructor(
        context: vscode.ExtensionContext,
        document: ObjWatchDocument,
        webviewPanel: vscode.WebviewPanel
    ) {
        this._context = context;
        this._document = document;
        this._webviewPanel = webviewPanel;
        this._themeManager = ThemeManager.getInstance(context);

        this.setupWebview();
        this.setupThemeListeners();
        this.updateWebview();

        // Listen for document changes
        this._document.onDidChangeDocument(() => {
            this.updateWebview();
        });

        // Handle webview messages
        this._webviewPanel.webview.onDidReceiveMessage(
            async (message: any) => {
                await this.handleMessage(message);
            }
        );

        // Handle panel disposal
        this._webviewPanel.onDidDispose(() => {
            this.dispose();
        });
    }

    private setupWebview(): void {
        this._webviewPanel.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.joinPath(this._context.extensionUri, 'media'),
                vscode.Uri.joinPath(this._context.extensionUri, 'out')
            ]
        };
    }

    private setupThemeListeners(): void {
        // 监听主题变化
        const themeDisposable = this._themeManager.onThemeChange(() => {
            this.updateWebview();
        });
        
        // 监听配置变化
        const configDisposable = this._themeManager.onConfigurationChange(() => {
            this.updateWebview();
        });
        
        this._disposables.push(themeDisposable, configDisposable);
    }

    private async updateWebview(): Promise<void> {
        if (!this._webviewPanel) return;
        
        const performanceMonitor = PerformanceMonitor.getInstance();
        const errorHandler = ErrorHandler.getInstance();
        
        performanceMonitor.recordRenderStart();
        
        try {
            if (!this._document.data) {
                this._webviewPanel.webview.html = this.getLoadingHtml();
                return;
            }

            // Check if we should skip this update for performance
            if (this.shouldSkipUpdate()) {
                console.log('Skipping webview update for performance optimization');
                return;
            }

            const events = EventProcessor.processEvents(this._document.data.ObjWatch.events);
            const optimizedEvents = MemoryOptimizer.optimizeEvents(events);
            
            // Generate HTML with performance monitoring
            const htmlGenerationStart = Date.now();
            const html = this.getHtml(optimizedEvents);
            const htmlGenerationTime = Date.now() - htmlGenerationStart;
            
            if (htmlGenerationTime > 1000) {
                console.warn(`Slow HTML generation: ${htmlGenerationTime}ms`);
            }
            
            // Update webview
            this._webviewPanel.webview.html = html;
            
            performanceMonitor.recordRenderEnd();
            
            // Schedule memory cleanup
            MemoryOptimizer.scheduleCleanup();
            
            // Log performance metrics
            this.logPerformanceMetrics(performanceMonitor, events.length);
            
        } catch (error) {
            errorHandler.handleRecoverableError(
                error as Error,
                'Webview Update',
                () => this.updateWebview()
            );
            
            this._webviewPanel.webview.html = this.getErrorHtml(error as Error);
        }
    }
    
    private _lastUpdateTime: number = 0;
    
    private shouldSkipUpdate(): boolean {
        const now = Date.now();
        
        // Don't update too frequently (debounce)
        if (this._lastUpdateTime && now - this._lastUpdateTime < 100) { // 100ms debounce
            return true;
        }
        
        this._lastUpdateTime = now;
        return false;
    }
    
    private logPerformanceMetrics(performanceMonitor: PerformanceMonitor, eventCount: number): void {
        const stats = performanceMonitor.getPerformanceStats();
        
        // Log detailed performance information
        if (stats.renderCount % 20 === 0) {
            console.log(`Performance Summary:
- Total Events Processed: ${stats.eventCount}
- Render Count: ${stats.renderCount}
- Average Render Time: ${stats.averageRenderTime.toFixed(2)}ms
- Max Render Time: ${stats.maxRenderTime}ms
- Events/Second: ${stats.eventsPerSecond.toFixed(2)}
- Current Event Count: ${eventCount}`);
            
            // Show performance recommendations
            const recommendations = performanceMonitor.getPerformanceRecommendations();
            if (recommendations.length > 0) {
                console.log('Performance Recommendations:', recommendations);
            }
        }
        
        // Show warning for very slow renders
        if (stats.averageRenderTime > 2000) {
            vscode.window.showWarningMessage(
                `Slow rendering detected (avg: ${stats.averageRenderTime.toFixed(0)}ms). Consider optimizing your ObjWatch configuration.`
            );
        }
    }

    private getLoadingHtml(): string {
        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ObjWatch Visualizer</title>
                <style>
                    ${this._themeManager.getStyles()}
                    
                    .loading {
                        text-align: center;
                        padding: calc(var(--vscode-padding) * 2.5);
                        color: var(--vscode-descriptionForeground);
                        font-size: calc(var(--vscode-font-size) * 1.1);
                        line-height: 1.5;
                    }
                </style>
            </head>
            <body>
                <div class="loading">Loading ObjWatch data...</div>
            </body>
            </html>
        `;
    }

    private getErrorHtml(error: Error): string {
        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ObjWatch Visualizer - Error</title>
                <style>
                    ${this._themeManager.getStyles()}
                    
                    .error-container {
                        text-align: center;
                        padding: calc(var(--vscode-padding) * 2.5);
                        color: var(--vscode-inputValidation-errorBorder);
                    }
                    .error-title {
                        font-size: calc(var(--vscode-font-size) * 1.2);
                        font-weight: 600;
                        margin-bottom: calc(var(--vscode-padding) * 1.25);
                        line-height: 1.3;
                    }
                    .error-message {
                        background-color: var(--vscode-inputValidation-errorBackground);
                        border: 1px solid var(--vscode-inputValidation-errorBorder);
                        padding: calc(var(--vscode-padding) * 0.94);
                        border-radius: var(--vscode-border-radius);
                        margin-bottom: calc(var(--vscode-padding) * 1.25);
                        text-align: left;
                        font-family: var(--vscode-editor-font-family);
                        font-size: calc(var(--vscode-editor-font-size) * 0.86);
                        line-height: var(--vscode-editor-line-height);
                        white-space: pre-wrap;
                        word-break: break-word;
                    }
                    .error-help {
                        color: var(--vscode-descriptionForeground);
                        font-size: calc(var(--vscode-font-size) * 0.9);
                        line-height: 1.4;
                    }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <div class="error-title">Error Loading ObjWatch Data</div>
                    <div class="error-message">${error.message}</div>
                    <div class="error-help">Please check the console for more details.</div>
                </div>
            </body>
            </html>
        `;
    }

    private getHtml(events: ProcessedEvent[]): string {
        const runtimeInfo = this._document.data!.ObjWatch.runtime_info;
        const config = this._document.data!.ObjWatch.config;

        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ObjWatch Visualizer</title>
                <style>
                    ${this._themeManager.getStyles()}
                    ${this.getStyles()}
                </style>
            </head>
            <body>
                <div class="container">
                    <header class="header">
                        <h1>ObjWatch Visualizer</h1>
                        <div class="runtime-info">
                            <div><strong>Version:</strong> ${runtimeInfo.version}</div>
                            <div><strong>Start Time:</strong> ${runtimeInfo.start_time}</div>
                            <div><strong>System:</strong> ${runtimeInfo.system_info}</div>
                            <div><strong>Python:</strong> ${runtimeInfo.python_version}</div>
                        </div>
                    </header>
                    
                    <main class="main">
                        <div class="events-container">
                            ${this.renderEvents(events)}
                        </div>
                    </main>
                </div>
                
                <script>
                    ${this.getScript()}
                </script>
            </body>
            </html>
        `;
    }

    private getStyles(): string {
        return `
            .event {
                margin: calc(var(--vscode-padding) * 0.125) 0;
                padding-left: calc(var(--vscode-padding) * 1.25);
                position: relative;
            }
            
            .event.run {
                color: var(--vscode-debugIcon-startForeground);
            }
            
            .event.end {
                color: var(--vscode-debugIcon-stopForeground);
            }
            
            .event.upd {
                color: var(--vscode-debugIcon-stepOverForeground);
            }
            
            .event.apd {
                color: var(--vscode-debugIcon-continueForeground);
            }
            
            .event.pop {
                color: var(--vscode-debugIcon-breakpointForeground);
            }
            
            .toggle-button {
                position: absolute;
                left: 0;
                top: 0;
                width: calc(var(--vscode-padding) * 1);
                height: calc(var(--vscode-padding) * 1);
                cursor: pointer;
                border: none;
                background: none;
                color: var(--vscode-descriptionForeground);
                font-size: calc(var(--vscode-font-size) * 0.75);
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: var(--vscode-border-radius);
            }
            
            .toggle-button:hover {
                color: var(--vscode-foreground);
                background-color: var(--vscode-button-hoverBackground);
            }
            
            .children {
                margin-left: calc(var(--vscode-padding) * 1.25);
                border-left: 1px solid var(--vscode-panel-border);
                padding-left: calc(var(--vscode-padding) * 0.625);
            }
            
            .hidden {
                display: none;
            }
            
            .indent {
                display: inline-block;
                width: calc(var(--vscode-padding) * 1.25);
            }
            
            .timestamp {
                color: var(--vscode-descriptionForeground);
                font-size: calc(var(--vscode-font-size) * 0.9);
                margin-right: calc(var(--vscode-padding) * 0.625);
            }
            
            .event-type {
                font-weight: 600;
                margin-right: calc(var(--vscode-padding) * 0.5);
            }
            
            .event-content {
                word-break: break-all;
                font-family: var(--vscode-editor-font-family);
                font-size: var(--vscode-editor-font-size);
                line-height: var(--vscode-editor-line-height);
            }
        `;
    }

    private renderEvents(events: ProcessedEvent[]): string {
        if (events.length === 0) {
            return '<div class="no-events">No events recorded</div>';
        }

        // Use a simpler approach that matches Python script's recursive processing
        // This avoids complex nested event detection that can cause cross-platform differences
        let html = '';
        let i = 0;
        
        while (i < events.length) {
            const event = events[i];
            
            // For run events with children, render them with their nested events
            if (event.type === 'run' && event.hasChildren) {
                // Find the corresponding end event
                let endIndex = i + 1;
                let nestedDepth = event.depth + 1;
                
                while (endIndex < events.length) {
                    const nextEvent = events[endIndex];
                    if (nextEvent.type === 'end' && nextEvent.depth === event.depth && 
                        nextEvent.qualifiedName === event.qualifiedName) {
                        break;
                    }
                    endIndex++;
                }
                
                // Render the run event
                html += this.renderEvent(event);
                
                // Render nested events (if any exist and not collapsed)
                if (!this._collapsedStates.has(event.eventId) && endIndex > i + 1) {
                    const nestedEvents = events.slice(i + 1, endIndex);
                    html += '<div class="children">';
                    html += this.renderEvents(nestedEvents); // Recursive call for nested events
                    html += '</div>';
                }
                
                // Render the end event
                if (endIndex < events.length) {
                    html += this.renderEvent(events[endIndex]);
                }
                
                i = endIndex + 1; // Move to next event after end
            } else {
                // For simple events (end, upd, apd, pop) or run events without children
                html += this.renderEvent(event);
                i++;
            }
        }

        return html;
    }

    private renderEvent(event: ProcessedEvent): string {
        const isCollapsed = this._collapsedStates.has(event.eventId);
        const hasChildren = event.type === 'run' && event.hasChildren;
        
        let html = `
            <div class="event ${isCollapsed ? 'collapsed' : ''}" data-event-id="${event.eventId}" data-depth="${event.depth}">
                ${this.renderEventLine(event)}
                <div class="event-content">
                    ${this.renderIndent(event.depth)}
                    ${hasChildren ? this.renderToggleButton(event.eventId, isCollapsed) : '<div style="width: 16px;"></div>'}
                    <span class="event-type ${event.type}">${event.type}</span>
                    <div class="event-details">
                        ${this.renderEventDetails(event)}
                    </div>
                </div>
            </div>
        `;

        return html;
    }

    private renderToggleButton(eventId: string, isCollapsed: boolean): string {
        const icon = isCollapsed ? '▶' : '▼';
        return `<button class="toggle-button" data-event-id="${eventId}">${icon}</button>`;
    }

    private renderIndent(depth: number): string {
        let html = '';
        for (let i = 0; i < depth; i++) {
            html += '<div class="indent-level"></div>';
        }
        return html;
    }

    private renderEventDetails(event: ProcessedEvent): string {
        switch (event.type) {
            case 'run':
                return `
                    <span class="qualified-name">${event.qualifiedName}</span>
                    ${event.callMsg ? `<span class="call-msg"> <- ${event.callMsg}</span>` : ''}
                `;
            case 'end':
                return `
                    <span class="qualified-name">${event.qualifiedName}</span>
                    ${event.returnMsg ? `<span class="return-msg"> -> ${event.returnMsg}</span>` : ''}
                `;
            case 'upd':
                return `
                    <span class="qualified-name">${event.name}</span>
                    <span class="update-details"> ${event.oldValue} -> ${event.newValue}</span>
                `;
            case 'apd':
            case 'pop':
                return `<span class="qualified-name">${event.name}</span>`;
            default:
                return '';
        }
    }

    private renderEventLine(event: ProcessedEvent): string {
        // Format the line number to match objwatch.log format (right-aligned, 4 characters)
        const lineNumber = event.line.toString().padStart(4);
        return `<span class="event-line">${lineNumber}</span>`;
    }



    private getScript(): string {
        return `
            const vscode = acquireVsCodeApi();
            
            // Handle toggle events
            document.addEventListener('click', (event) => {
                const toggleButton = event.target.closest('.toggle-button');
                if (toggleButton) {
                    const eventElement = toggleButton.closest('.event');
                    const eventId = eventElement.dataset.eventId;
                    
                    vscode.postMessage({
                        type: 'toggle',
                        eventId: eventId
                    });
                }
            });
            
            // Handle initial state
            window.addEventListener('load', () => {
                vscode.postMessage({
                    type: 'ready'
                });
            });
        `;
    }

    private async handleMessage(message: any): Promise<void> {
        switch (message.type) {
            case 'toggle':
                await this.handleToggle(message.eventId);
                break;
            case 'ready':
                // Webview is ready
                break;
        }
    }

    private async handleToggle(eventId: string): Promise<void> {
        if (this._collapsedStates.has(eventId)) {
            this._collapsedStates.delete(eventId);
        } else {
            this._collapsedStates.add(eventId);
        }
        
        await this.updateWebview();
    }

    dispose(): void {
        // Clean up resources
        this._disposables.forEach(disposable => disposable.dispose());
        this._disposables = [];
    }
}