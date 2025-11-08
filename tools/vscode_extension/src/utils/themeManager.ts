import * as vscode from 'vscode';

/**
 * 主题管理器 - 负责从VSCode主题配置中获取所有视觉样式
 */
export class ThemeManager {
    private static _instance: ThemeManager;
    private _context: vscode.ExtensionContext;

    private constructor(context: vscode.ExtensionContext) {
        this._context = context;
    }

    public static getInstance(context?: vscode.ExtensionContext): ThemeManager {
        if (!ThemeManager._instance && context) {
            ThemeManager._instance = new ThemeManager(context);
        }
        return ThemeManager._instance;
    }

    /**
     * 获取完整的CSS样式定义，完全基于VSCode主题变量
     */
    public getStyles(): string {
        return `
            :root {
                /* 字体相关 */
                --vscode-font-family: ${this.getFontFamily()};
                --vscode-font-size: ${this.getFontSize()}px;
                --vscode-font-weight: ${this.getFontWeight()};
                --vscode-line-height: ${this.getLineHeight()};
                
                /* 编辑器字体 */
                --vscode-editor-font-family: ${this.getEditorFontFamily()};
                --vscode-editor-font-size: ${this.getEditorFontSize()}px;
                --vscode-editor-font-weight: ${this.getEditorFontWeight()};
                --vscode-editor-line-height: ${this.getEditorLineHeight()};
                
                /* 颜色主题 */
                --vscode-foreground: ${this.getForegroundColor()};
                --vscode-background: ${this.getBackgroundColor()};
                --vscode-editor-background: ${this.getEditorBackgroundColor()};
                --vscode-textCodeBlock-background: ${this.getTextCodeBlockBackground()};
                
                /* 描述性颜色 */
                --vscode-descriptionForeground: ${this.getDescriptionForeground()};
                --vscode-titleBar-activeForeground: ${this.getTitleBarActiveForeground()};
                
                /* 状态颜色 */
                --vscode-textLink-foreground: ${this.getTextLinkForeground()};
                --vscode-testing-iconPassed: ${this.getTestingIconPassed()};
                --vscode-inputValidation-warningBorder: ${this.getInputValidationWarningBorder()};
                --vscode-symbolIcon-fieldForeground: ${this.getSymbolIconFieldForeground()};
                --vscode-inputValidation-errorBorder: ${this.getInputValidationErrorBorder()};
                --vscode-inputValidation-errorBackground: ${this.getInputValidationErrorBackground()};
                
                /* 边框和面板 */
                --vscode-panel-border: ${this.getPanelBorderColor()};
                --vscode-border-radius: ${this.getBorderRadius()}px;
                --vscode-padding: ${this.getPadding()}px;
                
                /* 按钮和交互 */
                --vscode-button-hoverBackground: ${this.getButtonHoverBackground()};
                --vscode-button-background: ${this.getButtonBackground()};
                --vscode-button-foreground: ${this.getButtonForeground()};
                
                /* 焦点和选择 */
                --vscode-focus-border: ${this.getFocusBorder()};
                --vscode-selection-background: ${this.getSelectionBackground()};
                
                /* 滚动条 */
                --vscode-scrollbar-shadow: ${this.getScrollbarShadow()};
                --vscode-scrollbarSlider-background: ${this.getScrollbarSliderBackground()};
                --vscode-scrollbarSlider-hoverBackground: ${this.getScrollbarSliderHoverBackground()};
            }
            
            body {
                font-family: var(--vscode-font-family);
                font-size: var(--vscode-font-size);
                font-weight: var(--vscode-font-weight);
                line-height: var(--vscode-line-height);
                color: var(--vscode-foreground);
                background-color: var(--vscode-background);
                margin: 0;
                padding: 0;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            
            .container {
                max-width: 100%;
                margin: 0 auto;
                padding: var(--vscode-padding);
                box-sizing: border-box;
            }
            
            .header {
                border-bottom: 1px solid var(--vscode-panel-border);
                padding-bottom: calc(var(--vscode-padding) * 1.5);
                margin-bottom: calc(var(--vscode-padding) * 1.5);
            }
            
            .header h1 {
                margin: 0 0 calc(var(--vscode-padding) * 0.5) 0;
                color: var(--vscode-titleBar-activeForeground);
                font-size: calc(var(--vscode-font-size) * 1.25);
                font-weight: 600;
                line-height: 1.2;
            }
            
            .runtime-info {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: calc(var(--vscode-padding) * 0.5);
                font-size: calc(var(--vscode-font-size) * 0.9);
                color: var(--vscode-descriptionForeground);
                line-height: 1.3;
            }
            
            .runtime-info div {
                display: flex;
                align-items: center;
                min-height: calc(var(--vscode-font-size) * 1.3);
            }
            
            .runtime-info strong {
                margin-right: calc(var(--vscode-padding) * 0.25);
                color: var(--vscode-foreground);
            }
            
            .events-container {
                font-family: var(--vscode-editor-font-family);
                font-size: var(--vscode-editor-font-size);
                font-weight: var(--vscode-editor-font-weight);
                line-height: var(--vscode-editor-line-height);
                background-color: var(--vscode-textCodeBlock-background);
                border: 1px solid var(--vscode-panel-border);
                border-radius: var(--vscode-border-radius);
                padding: var(--vscode-padding);
                overflow-x: auto;
                white-space: pre;
                box-shadow: 0 1px 3px var(--vscode-scrollbar-shadow);
            }
            
            .event {
                display: flex;
                align-items: flex-start;
                margin: 0;
                min-height: calc(var(--vscode-editor-font-size) * var(--vscode-editor-line-height));
                white-space: pre;
                font-family: var(--vscode-editor-font-family);
                transition: opacity 0.15s ease;
            }
            
            .event:hover {
                background-color: var(--vscode-button-hoverBackground);
                border-radius: calc(var(--vscode-border-radius) * 0.5);
            }
            
            .event-line {
                width: 60px;
                color: var(--vscode-descriptionForeground);
                font-size: calc(var(--vscode-editor-font-size) * 0.9);
                text-align: right;
                padding-right: var(--vscode-padding);
                user-select: none;
                font-family: var(--vscode-editor-font-family);
                opacity: 0.8;
            }
            
            .event-content {
                flex: 1;
                display: flex;
                align-items: flex-start;
                min-height: calc(var(--vscode-editor-font-size) * var(--vscode-editor-line-height));
            }
            
            .indent-level {
                position: relative;
                width: 16px;
                min-width: 16px;
                min-height: calc(var(--vscode-editor-font-size) * var(--vscode-editor-line-height));
            }
            
            .indent-level::before {
                content: '';
                position: absolute;
                left: 50%;
                top: 0;
                bottom: 0;
                width: 1px;
                background-color: var(--vscode-panel-border);
                opacity: 0.3;
                transition: opacity 0.15s ease;
            }
            
            .indent-level:hover::before {
                opacity: 0.6;
            }
            
            .indent-level:last-child::before {
                opacity: 0.8;
            }
            
            .event-type {
                font-weight: 600;
                margin-right: var(--vscode-padding);
                min-width: 40px;
                color: var(--vscode-foreground);
                font-size: calc(var(--vscode-editor-font-size) * 0.95);
                user-select: none;
            }
            
            .event-type.run { color: var(--vscode-textLink-foreground); }
            .event-type.end { color: var(--vscode-testing-iconPassed); }
            .event-type.upd { color: var(--vscode-inputValidation-warningBorder); }
            .event-type.apd { color: var(--vscode-symbolIcon-fieldForeground); }
            .event-type.pop { color: var(--vscode-inputValidation-errorBorder); }
            
            .event-details {
                flex: 1;
                display: flex;
                align-items: center;
                min-height: calc(var(--vscode-editor-font-size) * var(--vscode-editor-line-height));
                flex-wrap: wrap;
            }
            
            .qualified-name {
                color: var(--vscode-foreground);
                font-weight: 500;
                font-size: var(--vscode-editor-font-size);
            }
            
            .call-msg, .return-msg {
                color: var(--vscode-descriptionForeground);
                font-style: normal;
                margin-left: var(--vscode-padding);
                font-size: calc(var(--vscode-editor-font-size) * 0.95);
                opacity: 0.9;
            }
            
            .update-details {
                color: var(--vscode-descriptionForeground);
                margin-left: var(--vscode-padding);
                font-size: calc(var(--vscode-editor-font-size) * 0.95);
                opacity: 0.9;
            }
            
            .toggle-button {
                background: var(--vscode-button-background);
                border: 1px solid var(--vscode-panel-border);
                color: var(--vscode-button-foreground);
                cursor: pointer;
                padding: 0;
                margin-right: calc(var(--vscode-padding) * 0.5);
                border-radius: calc(var(--vscode-border-radius) * 0.5);
                font-size: calc(var(--vscode-editor-font-size) * 0.8);
                width: 16px;
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: var(--vscode-editor-font-family);
                transition: all 0.15s ease;
            }
            
            .toggle-button:hover {
                background-color: var(--vscode-button-hoverBackground);
                border-color: var(--vscode-focus-border);
                transform: scale(1.1);
            }
            
            .children {
                margin-left: 20px;
                border-left: 1px solid var(--vscode-panel-border);
                padding-left: 10px;
                transition: all 0.2s ease;
            }
            
            .collapsed .children {
                display: none;
            }
            
            .event.collapsed {
                opacity: 0.6;
            }
            
            .event.collapsed:hover {
                opacity: 0.8;
            }
            
            .no-events {
                text-align: center;
                color: var(--vscode-descriptionForeground);
                font-style: italic;
                padding: calc(var(--vscode-padding) * 2);
                font-size: calc(var(--vscode-font-size) * 1.1);
            }
            
            /* 滚动条样式 */
            .events-container::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            .events-container::-webkit-scrollbar-track {
                background: transparent;
            }
            
            .events-container::-webkit-scrollbar-thumb {
                background: var(--vscode-scrollbarSlider-background);
                border-radius: 4px;
            }
            
            .events-container::-webkit-scrollbar-thumb:hover {
                background: var(--vscode-scrollbarSlider-hoverBackground);
            }
            
            /* 响应式设计 */
            @media (max-width: 768px) {
                .container {
                    padding: calc(var(--vscode-padding) * 0.5);
                }
                
                .runtime-info {
                    grid-template-columns: 1fr;
                    gap: calc(var(--vscode-padding) * 0.25);
                }
                
                .event-line {
                    width: 40px;
                    font-size: calc(var(--vscode-editor-font-size) * 0.8);
                }
                
                .event-type {
                    min-width: 35px;
                    font-size: calc(var(--vscode-editor-font-size) * 0.9);
                }
            }
        `;
    }

    /**
     * 获取字体配置方法
     */
    private getFontFamily(): string {
        const config = vscode.workspace.getConfiguration('editor');
        return config.get('fontFamily') || 'Menlo, Monaco, "Courier New", monospace';
    }

    private getFontSize(): number {
        const config = vscode.workspace.getConfiguration('editor');
        return config.get('fontSize') || 14;
    }

    private getFontWeight(): string {
        const config = vscode.workspace.getConfiguration('editor');
        return config.get('fontWeight') || 'normal';
    }

    private getLineHeight(): number {
        const config = vscode.workspace.getConfiguration('editor');
        return config.get('lineHeight') || 1.4;
    }

    private getEditorFontFamily(): string {
        const config = vscode.workspace.getConfiguration('editor');
        return config.get('fontFamily') || 'Menlo, Monaco, "Courier New", monospace';
    }

    private getEditorFontSize(): number {
        const config = vscode.workspace.getConfiguration('editor');
        return config.get('fontSize') || 14;
    }

    private getEditorFontWeight(): string {
        const config = vscode.workspace.getConfiguration('editor');
        return config.get('fontWeight') || 'normal';
    }

    private getEditorLineHeight(): number {
        const config = vscode.workspace.getConfiguration('editor');
        return config.get('lineHeight') || 1.4;
    }

    /**
     * 获取颜色配置方法
     */
    private getForegroundColor(): string {
        return this.getColor('foreground') || '#cccccc';
    }

    private getBackgroundColor(): string {
        return this.getColor('background') || '#1e1e1e';
    }

    private getEditorBackgroundColor(): string {
        return this.getColor('editor.background') || '#1e1e1e';
    }

    private getTextCodeBlockBackground(): string {
        return this.getColor('textCodeBlock.background') || '#0d1117';
    }

    private getDescriptionForeground(): string {
        return this.getColor('descriptionForeground') || '#969696';
    }

    private getTitleBarActiveForeground(): string {
        return this.getColor('titleBar.activeForeground') || '#ffffff';
    }

    private getTextLinkForeground(): string {
        return this.getColor('textLink.foreground') || '#3794ff';
    }

    private getTestingIconPassed(): string {
        return this.getColor('testing.iconPassed') || '#73c991';
    }

    private getInputValidationWarningBorder(): string {
        return this.getColor('inputValidation.warningBorder') || '#b89500';
    }

    private getSymbolIconFieldForeground(): string {
        return this.getColor('symbolIcon.fieldForeground') || '#75beff';
    }

    private getInputValidationErrorBorder(): string {
        return this.getColor('inputValidation.errorBorder') || '#f48771';
    }

    private getInputValidationErrorBackground(): string {
        return this.getColor('inputValidation.errorBackground') || '#5a1d1d';
    }

    private getPanelBorderColor(): string {
        return this.getColor('panel.border') || '#454545';
    }

    private getButtonHoverBackground(): string {
        return this.getColor('button.hoverBackground') || '#0e639c';
    }

    private getButtonBackground(): string {
        return this.getColor('button.background') || '#0e639c';
    }

    private getButtonForeground(): string {
        return this.getColor('button.foreground') || '#ffffff';
    }

    private getFocusBorder(): string {
        return this.getColor('focusBorder') || '#007fd4';
    }

    private getSelectionBackground(): string {
        return this.getColor('selection.background') || '#264f78';
    }

    private getScrollbarShadow(): string {
        return this.getColor('scrollbar.shadow') || '#000000';
    }

    private getScrollbarSliderBackground(): string {
        return this.getColor('scrollbarSlider.background') || '#424242';
    }

    private getScrollbarSliderHoverBackground(): string {
        return this.getColor('scrollbarSlider.hoverBackground') || '#4a4a4a';
    }

    /**
     * 获取布局配置方法
     */
    private getBorderRadius(): number {
        return 3; // VSCode标准圆角
    }

    private getPadding(): number {
        return 16; // VSCode标准内边距
    }

    /**
     * 通用颜色获取方法
     */
    private getColor(colorId: string): string | undefined {
        try {
            // 从工作区配置获取颜色自定义
            const config = vscode.workspace.getConfiguration('workbench');
            const colorCustomizations = config.get('colorCustomizations') as any;
            if (colorCustomizations && colorCustomizations[colorId]) {
                return colorCustomizations[colorId];
            }
            
            // 使用VSCode内置的颜色变量，让CSS变量处理主题颜色
            // 这里返回undefined，让CSS使用var(--vscode-*)变量
            return undefined;
        } catch (error) {
            console.warn(`Failed to get color for ${colorId}:`, error);
            return undefined;
        }
    }

    /**
     * 监听主题变化并更新样式
     */
    public onThemeChange(callback: () => void): vscode.Disposable {
        return vscode.window.onDidChangeActiveColorTheme(callback);
    }

    /**
     * 监听配置变化并更新样式
     */
    public onConfigurationChange(callback: () => void): vscode.Disposable {
        return vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration('editor') || e.affectsConfiguration('workbench')) {
                callback();
            }
        });
    }
}