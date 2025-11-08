import * as vscode from 'vscode';
import { ObjWatchVisualizerProvider } from './providers/visualizerProvider';
import { DebugUtils } from './utils/debug';
import { DebugPanel } from './views/debugPanel';

export function activate(context: vscode.ExtensionContext) {
    // Initialize debug utilities
    DebugUtils.initialize();
    DebugUtils.log('ObjWatch Visualizer extension activated');
    DebugUtils.dumpState(context);

    // Register custom editor provider
    const provider = new ObjWatchVisualizerProvider(context);
    const providerRegistration = vscode.window.registerCustomEditorProvider(
        'objwatch.visualizer',
        provider,
        {
            webviewOptions: {
                retainContextWhenHidden: true,
            },
            supportsMultipleEditorsPerDocument: false,
        }
    );

    // Register command to open visualizer
    const openCommand = vscode.commands.registerCommand('objwatch.openVisualizer', () => {
        DebugUtils.log('Opening ObjWatch Visualizer via command');
        
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor && activeEditor.document.fileName.endsWith('objwatch.json')) {
            vscode.commands.executeCommand('vscode.openWith', activeEditor.document.uri, 'objwatch.visualizer');
        } else {
            vscode.window.showInformationMessage('Please open an objwatch.json file first.');
        }
    });

    // Register debug commands
    const debugCommandRegistration = vscode.commands.registerCommand('objwatch.showDebugOutput', () => {
        DebugUtils.showOutput();
    });
    
    const metricsCommandRegistration = vscode.commands.registerCommand('objwatch.showMetrics', () => {
        const metrics = DebugUtils.getPerformanceMetrics();
        vscode.window.showInformationMessage(
            `Memory: ${Math.round(metrics.memoryUsage.heapUsed / 1024 / 1024)}MB, Uptime: ${Math.round(metrics.uptime)}s`
        );
    });
    
    // Register debug panel command
    const debugPanelCommandRegistration = vscode.commands.registerCommand('objwatch.showDebugPanel', () => {
        DebugPanel.createOrShow(context);
    });

    context.subscriptions.push(
        providerRegistration, 
        openCommand, 
        debugCommandRegistration,
        metricsCommandRegistration,
        debugPanelCommandRegistration
    );
    
    DebugUtils.log('All commands and providers registered successfully');
}

export function deactivate() {
    console.log('ObjWatch Visualizer extension is now deactivated!');
}