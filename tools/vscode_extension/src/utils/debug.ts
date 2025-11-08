import * as vscode from 'vscode';

/**
 * Debug utilities for the ObjWatch Visualizer extension
 */
export class DebugUtils {
    private static debugMode = false;
    private static outputChannel: vscode.OutputChannel;

    /**
     * Initialize debug utilities
     */
    public static initialize(): void {
        this.outputChannel = vscode.window.createOutputChannel('ObjWatch Visualizer');
        this.debugMode = vscode.workspace.getConfiguration('objwatch').get('debug', false);
        
        // Listen for configuration changes
        vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('objwatch.debug')) {
                this.debugMode = vscode.workspace.getConfiguration('objwatch').get('debug', false);
                this.log('Debug mode ' + (this.debugMode ? 'enabled' : 'disabled'));
            }
        });
    }

    /**
     * Log message to output channel if debug mode is enabled
     */
    public static log(message: string, ...args: any[]): void {
        if (this.debugMode) {
            const timestamp = new Date().toISOString();
            const formattedMessage = `[${timestamp}] ${message}`;
            
            if (args.length > 0) {
                this.outputChannel.appendLine(formattedMessage + ' ' + args.map(arg => 
                    typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
                ).join(' '));
            } else {
                this.outputChannel.appendLine(formattedMessage);
            }
        }
    }

    /**
     * Log error message (always shown regardless of debug mode)
     */
    public static error(message: string, error?: Error): void {
        const timestamp = new Date().toISOString();
        const errorMessage = `[${timestamp}] ERROR: ${message}`;
        
        this.outputChannel.appendLine(errorMessage);
        
        if (error) {
            this.outputChannel.appendLine(`Stack: ${error.stack}`);
        }
        
        // Show error message to user
        vscode.window.showErrorMessage(`ObjWatch Visualizer: ${message}`);
    }

    /**
     * Log warning message
     */
    public static warn(message: string): void {
        const timestamp = new Date().toISOString();
        this.outputChannel.appendLine(`[${timestamp}] WARN: ${message}`);
    }

    /**
     * Show output channel
     */
    public static showOutput(): void {
        this.outputChannel.show();
    }

    /**
     * Get performance metrics
     */
    public static getPerformanceMetrics(): {
        memoryUsage: NodeJS.MemoryUsage;
        uptime: number;
        timestamp: string;
    } {
        return {
            memoryUsage: process.memoryUsage(),
            uptime: process.uptime(),
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Dump current state for debugging
     */
    public static dumpState(context: vscode.ExtensionContext): void {
        this.log('=== Extension State Dump ===');
        this.log(`Extension ID: ${context.extension.id}`);
        this.log(`Extension Version: ${context.extension.packageJSON.version}`);
        this.log(`Storage Path: ${context.storageUri?.fsPath || 'Not available'}`);
        this.log(`Global Storage Path: ${context.globalStorageUri.fsPath}`);
        this.log(`Log Path: ${context.logUri.fsPath}`);
        
        const metrics = this.getPerformanceMetrics();
        this.log('Performance Metrics:', JSON.stringify(metrics, null, 2));
        this.log('=== End State Dump ===');
    }
}