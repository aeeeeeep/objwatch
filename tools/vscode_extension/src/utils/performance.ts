import * as vscode from 'vscode';

export class PerformanceMonitor {
    private static instance: PerformanceMonitor;
    private _startTime: number = 0;
    private _eventCount: number = 0;
    private _lastRenderTime: number = 0;
    private _renderCount: number = 0;
    private _averageRenderTime: number = 0;
    private _maxRenderTime: number = 0;
    private _minRenderTime: number = Infinity;
    private _totalRenderTime: number = 0;
    private _performanceThresholds = {
        slowRender: 10000, // ms
        highMemory: 5000, // MB
        maxEvents: 100000
    };

    static getInstance(): PerformanceMonitor {
        if (!PerformanceMonitor.instance) {
            PerformanceMonitor.instance = new PerformanceMonitor();
        }
        return PerformanceMonitor.instance;
    }

    startMonitoring(): void {
        this._startTime = Date.now();
        this._eventCount = 0;
        this._renderCount = 0;
        this._averageRenderTime = 0;
        this._maxRenderTime = 0;
        this._minRenderTime = Infinity;
        this._totalRenderTime = 0;
    }

    recordEventProcessed(): void {
        this._eventCount++;
    }

    recordRenderStart(): void {
        this._lastRenderTime = Date.now();
    }

    recordRenderEnd(): void {
        const renderTime = Date.now() - this._lastRenderTime;
        this._renderCount++;
        this._totalRenderTime += renderTime;
        
        // Update statistics
        this._maxRenderTime = Math.max(this._maxRenderTime, renderTime);
        this._minRenderTime = Math.min(this._minRenderTime, renderTime);
        this._averageRenderTime = this._totalRenderTime / this._renderCount;
        
        // Log performance warning if render time is too high
        if (renderTime > this._performanceThresholds.slowRender) {
            console.warn(`Slow render detected: ${renderTime}ms for ${this._eventCount} events`);
            vscode.window.showWarningMessage(
                `Slow rendering detected: ${renderTime}ms. Consider reducing the number of events.`
            );
        }
        
        // Log performance metrics periodically
        if (this._renderCount % 10 === 0) {
            console.log(`Performance stats - Avg: ${this._averageRenderTime.toFixed(2)}ms, ` +
                       `Min: ${this._minRenderTime}ms, Max: ${this._maxRenderTime}ms`);
        }
    }

    getPerformanceStats(): PerformanceStats {
        const totalTime = Date.now() - this._startTime;
        return {
            totalTime,
            eventCount: this._eventCount,
            renderCount: this._renderCount,
            averageRenderTime: this._averageRenderTime,
            eventsPerSecond: this._eventCount / (totalTime / 1000),
            maxRenderTime: this._maxRenderTime,
            minRenderTime: this._minRenderTime === Infinity ? 0 : this._minRenderTime,
            totalRenderTime: this._totalRenderTime
        };
    }
    
    getPerformanceRecommendations(): string[] {
        const recommendations: string[] = [];
        const stats = this.getPerformanceStats();
        
        if (stats.averageRenderTime > 500) {
            recommendations.push("Consider reducing the maximum number of events in settings");
        }
        
        if (stats.maxRenderTime > 2000) {
            recommendations.push("Large files detected. Enable auto-refresh to avoid frequent updates");
        }
        
        if (stats.eventCount > this._performanceThresholds.maxEvents) {
            recommendations.push(`File contains ${stats.eventCount} events. Consider filtering events.`);
        }
        
        return recommendations;
    }

    checkMemoryUsage(): void {
        if (typeof global !== 'undefined' && global.gc) {
            (global.gc as () => void)();
        }
        
        const memoryUsage = process.memoryUsage();
        const memoryMB = memoryUsage.heapUsed / 1024 / 1024;
        
        if (memoryMB > 500) {
            console.warn(`High memory usage: ${memoryMB.toFixed(2)}MB`);
            vscode.window.showWarningMessage(`ObjWatch Visualizer memory usage is high: ${memoryMB.toFixed(2)}MB`);
        }
    }
}

export interface PerformanceStats {
    totalTime: number;
    eventCount: number;
    renderCount: number;
    averageRenderTime: number;
    eventsPerSecond: number;
    maxRenderTime: number;
    minRenderTime: number;
    totalRenderTime: number;
}

export class ErrorHandler {
    private static instance: ErrorHandler;
    private _errorCount: number = 0;
    private _lastError: Error | null = null;
    private _errorHistory: Array<{timestamp: number; context: string; error: Error}> = [];
    private _maxErrorHistory: number = 100;
    
    static getInstance(): ErrorHandler {
        if (!ErrorHandler.instance) {
            ErrorHandler.instance = new ErrorHandler();
        }
        return ErrorHandler.instance;
    }
    
    handleError(error: Error, context: string = 'Unknown', showToUser: boolean = true): void {
        this._errorCount++;
        this._lastError = error;
        
        // Add to error history
        this._errorHistory.push({
            timestamp: Date.now(),
            context,
            error
        });
        
        // Keep only recent errors
        if (this._errorHistory.length > this._maxErrorHistory) {
            this._errorHistory = this._errorHistory.slice(-this._maxErrorHistory);
        }
        
        console.error(`[${context}] Error:`, error);
        
        // Show error message to user for critical errors
        if (showToUser && this._errorCount < 5) {
            vscode.window.showErrorMessage(
                `ObjWatch Extension Error (${context}): ${error.message}`,
                'Show Details', 'Ignore'
            ).then(selection => {
                if (selection === 'Show Details') {
                    this.showErrorDetails(error, context);
                }
            });
        }
    }
    
    private showErrorDetails(error: Error, context: string): void {
        const errorDetails = `
Error Details:
- Context: ${context}
- Message: ${error.message}
- Stack: ${error.stack || 'No stack trace available'}
- Timestamp: ${new Date().toISOString()}
- Total Errors: ${this._errorCount}
        `;
        
        vscode.window.showInformationMessage(errorDetails, {modal: true});
    }
    
    handleRecoverableError(error: Error, context: string, recoveryAction: () => void): void {
        this.handleError(error, context, false);
        
        vscode.window.showWarningMessage(
            `Recoverable error in ${context}: ${error.message}`,
            'Retry', 'Skip'
        ).then(selection => {
            if (selection === 'Retry') {
                recoveryAction();
            }
        });
    }
    
    clearErrors(): void {
        this._errorCount = 0;
        this._lastError = null;
        this._errorHistory = [];
    }
    
    getErrorStats(): ErrorStats {
        return {
            errorCount: this._errorCount,
            lastError: this._lastError?.message || null,
            recentErrors: this._errorHistory.slice(-10).map(e => ({
                context: e.context,
                message: e.error.message,
                timestamp: e.timestamp
            }))
        };
    }
    
    getErrorRecoverySuggestions(): string[] {
        const suggestions: string[] = [];
        
        if (this._errorCount > 10) {
            suggestions.push("High error rate detected. Consider restarting the extension.");
        }
        
        const fileErrors = this._errorHistory.filter(e => 
            e.context.includes('file') || e.context.includes('parse')
        );
        if (fileErrors.length > 0) {
            suggestions.push("File parsing errors detected. Check file format and permissions.");
        }
        
        const renderErrors = this._errorHistory.filter(e => 
            e.context.includes('render') || e.context.includes('webview')
        );
        if (renderErrors.length > 0) {
            suggestions.push("Rendering errors detected. Try refreshing the webview.");
        }
        
        return suggestions;
    }

    static handleError(error: Error, context: string): void {
        ErrorHandler.getInstance().handleError(error, context);
    }

    static handleFileError(error: Error, filePath: string): void {
        const message = `Failed to process file ${filePath}: ${error.message}`;
        ErrorHandler.getInstance().handleError(new Error(message), 'File Processing');
    }

    static handleJsonParseError(error: Error, content: string): void {
        const message = `Invalid JSON format: ${error.message}`;
        ErrorHandler.getInstance().handleError(new Error(message), 'JSON Parsing');
        
        // Log first 200 characters of problematic content for debugging
        console.error('Problematic content:', content.substring(0, 200));
    }

    static handleRenderError(error: Error, eventCount: number): void {
        const message = `Rendering failed for ${eventCount} events: ${error.message}`;
        ErrorHandler.getInstance().handleError(new Error(message), 'Rendering');
    }
}

interface ErrorStats {
    errorCount: number;
    lastError: string | null;
    recentErrors: Array<{
        context: string;
        message: string;
        timestamp: number;
    }>;
}

export class MemoryOptimizer {
    private static readonly MAX_EVENTS = 10000;
    private static readonly CLEANUP_INTERVAL = 30000; // 30 seconds
    private static readonly MEMORY_THRESHOLD = 500; // MB
    private static _lastCleanupTime: number = 0;
    private static _cleanupCount: number = 0;
    
    static optimizeEvents(events: any[]): any[] {
        const originalCount = events.length;
        
        if (events.length > this.MAX_EVENTS) {
            console.warn(`Event count (${originalCount}) exceeds maximum (${this.MAX_EVENTS}). Truncating...`);
            
            // Keep recent events but preserve some older ones for context
            const recentEvents = events.slice(-this.MAX_EVENTS * 0.8); // 80% recent
            const olderEvents = events.slice(0, Math.floor(originalCount * 0.02)); // 2% from start for context
            
            const optimized = [...olderEvents, ...recentEvents];
            console.log(`Optimized events: ${originalCount} -> ${optimized.length}`);
            
            return optimized;
        }
        
        return events;
    }
    
    static shouldCleanup(): boolean {
        const now = Date.now();
        const timeSinceLastCleanup = now - this._lastCleanupTime;
        
        // Don't cleanup too frequently
        if (timeSinceLastCleanup < 10000) { // 10 seconds minimum
            return false;
        }
        
        // Check memory usage if available
        if (typeof process !== 'undefined' && process.memoryUsage) {
            const memoryUsage = process.memoryUsage();
            const memoryMB = memoryUsage.heapUsed / 1024 / 1024;
            
            if (memoryMB > this.MEMORY_THRESHOLD) {
                console.log(`High memory usage detected: ${memoryMB.toFixed(2)}MB`);
                return true;
            }
        }
        
        // Cleanup every 30 seconds by default
        return timeSinceLastCleanup >= this.CLEANUP_INTERVAL;
    }
    
    static performCleanup(): void {
        if (!this.shouldCleanup()) {
            return;
        }
        
        if (typeof global !== 'undefined' && global.gc) {
            try {
                (global.gc as () => void)();
                this._lastCleanupTime = Date.now();
                this._cleanupCount++;
                
                if (typeof process !== 'undefined' && process.memoryUsage) {
                    const memoryUsage = process.memoryUsage();
                    console.log(`Memory cleanup #${this._cleanupCount}: ${(memoryUsage.heapUsed / 1024 / 1024).toFixed(2)}MB`);
                } else {
                    console.log(`Memory cleanup #${this._cleanupCount} performed`);
                }
            } catch (error) {
                console.error('Memory cleanup failed:', error);
            }
        }
    }
    
    static scheduleCleanup(): void {
        setInterval(() => {
            this.performCleanup();
        }, 5000); // Check every 5 seconds
    }
    
    static getMemoryStats(): MemoryStats {
        let memoryUsage = { heapUsed: 0, heapTotal: 0, external: 0 };
        
        if (typeof process !== 'undefined' && process.memoryUsage) {
            memoryUsage = process.memoryUsage();
        }
        
        return {
            heapUsedMB: memoryUsage.heapUsed / 1024 / 1024,
            heapTotalMB: memoryUsage.heapTotal / 1024 / 1024,
            externalMB: memoryUsage.external / 1024 / 1024,
            cleanupCount: this._cleanupCount,
            lastCleanupTime: this._lastCleanupTime
        };
    }
}

interface MemoryStats {
    heapUsedMB: number;
    heapTotalMB: number;
    externalMB: number;
    cleanupCount: number;
    lastCleanupTime: number;
}