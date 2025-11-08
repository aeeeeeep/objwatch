import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { ErrorHandler, MemoryOptimizer, PerformanceMonitor } from '../utils/performance';

export interface ObjWatchEvent {
    type: 'Function' | 'upd' | 'apd' | 'pop';
    module?: string;
    symbol?: string;
    symbol_type?: string;
    run_line?: number;
    qualified_name?: string;
    events?: ObjWatchEvent[];
    call_msg?: string;
    return_msg?: string;
    end_line?: number;
    name?: string;
    line?: number;
    old?: any;
    new?: any;
    call_depth?: number;
}

export interface ObjWatchData {
    ObjWatch: {
        runtime_info: {
            version: string;
            start_time: string;
            system_info: string;
            python_version: string;
        };
        config: {
            targets: string[];
            exclude_targets: string[] | null;
            framework: string | null;
            indexes: any;
            output: string;
            output_json: string;
            level: string;
            simple: boolean;
            wrapper: string;
            with_locals: boolean;
            with_globals: boolean;
        };
        events: ObjWatchEvent[];
    };
}

export class ObjWatchDocument implements vscode.CustomDocument {
    private readonly _uri: vscode.Uri;
    private readonly _fileWatcher: vscode.FileSystemWatcher;
    private _data: ObjWatchData | null = null;
    private _lastModified: number = 0;

    static async create(uri: vscode.Uri): Promise<ObjWatchDocument> {
        const document = new ObjWatchDocument(uri);
        await document.load();
        return document;
    }

    private constructor(uri: vscode.Uri) {
        this._uri = uri;
        
        // Create file watcher for real-time updates
        this._fileWatcher = vscode.workspace.createFileSystemWatcher(uri.fsPath);
        this._fileWatcher.onDidChange(() => this.load());
    }

    get uri(): vscode.Uri {
        return this._uri;
    }

    get data(): ObjWatchData | null {
        return this._data;
    }

    private async load(): Promise<void> {
        const errorHandler = ErrorHandler.getInstance();
        
        try {
            const config = vscode.workspace.getConfiguration('objwatch');
            const autoRefresh = config.get<boolean>('autoRefresh', true);
            const maxEvents = config.get<number>('maxEvents', 1000);
            
            // Check if auto-refresh is disabled
            if (!autoRefresh) {
                return;
            }
            
            const stats = await vscode.workspace.fs.stat(this._uri);
            const currentModified = stats.mtime;
            
            // Avoid reloading if file hasn't changed
            if (currentModified <= this._lastModified) {
                return;
            }
            
            this._lastModified = currentModified;
            
            // Check file accessibility before reading
            try {
                await vscode.workspace.fs.stat(this._uri);
            } catch (accessError) {
                errorHandler.handleRecoverableError(
                    new Error(`File not accessible: ${this._uri.fsPath}`),
                    'File Access',
                    () => this.load()
                );
                return;
            }
            
            const content = await vscode.workspace.fs.readFile(this._uri);
            const jsonContent = Buffer.from(content).toString('utf8');
            
            // Validate file size
            if (jsonContent.length > 100 * 1024 * 1024) { // 100MB limit
                errorHandler.handleError(
                    new Error(`File too large: ${(jsonContent.length / 1024 / 1024).toFixed(2)}MB`),
                    'File Size Check'
                );
            }
            
            // Parse JSON with error handling
            let parsedData: ObjWatchData;
            try {
                // Validate content before parsing
                if (!jsonContent || jsonContent.trim().length === 0) {
                    throw new Error('Empty file content');
                }
                
                // Check for common JSON issues
                if (jsonContent.length > 10 * 1024 * 1024) { // 10MB
                    console.warn('Large JSON file detected, parsing may be slow');
                }
                
                parsedData = JSON.parse(jsonContent) as ObjWatchData;
                
                // Validate basic structure
                if (!parsedData || typeof parsedData !== 'object') {
                    throw new Error('Invalid JSON structure: root must be an object');
                }
                
                // Ensure events array exists
                if (!Array.isArray(parsedData.ObjWatch.events)) {
                    console.warn('No events array found, creating empty array');
                    parsedData.ObjWatch.events = [];
                }
                
                // Validate individual events
                const validEvents = parsedData.ObjWatch.events.filter((event: any, index: number) => {
                    if (!event || typeof event !== 'object') {
                        console.warn(`Invalid event at index ${index}, skipping`);
                        return false;
                    }
                    return true;
                });
                
                if (validEvents.length !== parsedData.ObjWatch.events.length) {
                    console.warn(`Filtered ${parsedData.ObjWatch.events.length - validEvents.length} invalid events`);
                    parsedData.ObjWatch.events = validEvents;
                }
            } catch (parseError) {
                errorHandler.handleRecoverableError(
                    parseError as Error,
                    'JSON Parsing',
                    () => this.load()
                );
                return;
            }
            
            // Optimize memory usage for large files
            if (parsedData.ObjWatch.events) {
                // Apply event limit if configured
                if (maxEvents > 0 && parsedData.ObjWatch.events.length > maxEvents) {
                    parsedData.ObjWatch.events = parsedData.ObjWatch.events.slice(-maxEvents);
                }
                parsedData.ObjWatch.events = MemoryOptimizer.optimizeEvents(parsedData.ObjWatch.events);
            }
            
            this._data = parsedData;
            
            // Record performance metrics
            PerformanceMonitor.getInstance().recordEventProcessed();
            
            // Notify listeners about the update
            this._onDidChangeDocument.fire();
        } catch (error) {
            ErrorHandler.handleFileError(error as Error, this._uri.fsPath);
        }
    }

    // Event emitter for document changes
    private readonly _onDidChangeDocument = new vscode.EventEmitter<void>();
    public readonly onDidChangeDocument = this._onDidChangeDocument.event;

    dispose(): void {
        this._fileWatcher.dispose();
        this._onDidChangeDocument.dispose();
    }
}

export class EventProcessor {
    static processEvents(events: ObjWatchEvent[], call_depth: number = 0): ProcessedEvent[] {
        const processed: ProcessedEvent[] = [];
        
        for (const event of events) {
            if (event.type === 'Function') {
                // Add run event
                const runEvent: ProcessedEvent = {
                    type: 'run',
                    line: event.run_line!,
                    depth: call_depth,
                    qualifiedName: event.qualified_name!,
                    callMsg: event.call_msg,
                    hasChildren: event.events && event.events.length > 0,
                    eventId: this.generateEventId('run', event.run_line!, call_depth, event.qualified_name!)
                };
                processed.push(runEvent);
                
                // Process nested events - use call_depth + 1 to match Python script behavior
                if (event.events && event.events.length > 0) {
                    const nested = this.processEvents(event.events, call_depth + 1);
                    processed.push(...nested);
                }
                
                // Add end event - use the same call_depth as run event
                processed.push({
                    type: 'end',
                    line: event.end_line!,
                    depth: call_depth,
                    qualifiedName: event.qualified_name!,
                    returnMsg: event.return_msg,
                    eventId: this.generateEventId('end', event.end_line!, call_depth, event.qualified_name!)
                });
            } else {
                // Handle update events - use event.call_depth if available, otherwise use current call_depth
                processed.push({
                    type: event.type as 'upd' | 'apd' | 'pop',
                    line: event.line!,
                    depth: event.call_depth !== undefined ? event.call_depth : call_depth,
                    name: event.name!,
                    oldValue: event.old,
                    newValue: event.new,
                    eventId: this.generateEventId(event.type, event.line!, event.call_depth !== undefined ? event.call_depth : call_depth, event.name!)
                });
            }
        }
        
        return processed;
    }
    
    private static generateEventId(type: string, line: number, call_depth: number, identifier: string): string {
        // Use a consistent algorithm that matches Python script's implicit event identification
        // Python script relies on event order and nesting structure, not explicit IDs
        // For cross-platform consistency, use a simple hash-based approach
        const content = `${type}-${line}-${call_depth}-${identifier}`;
        let hash = 0;
        for (let i = 0; i < content.length; i++) {
            const char = content.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return `event-${Math.abs(hash).toString(36)}`;
    }
}

export interface ProcessedEvent {
    type: 'run' | 'end' | 'upd' | 'apd' | 'pop';
    line: number;
    depth: number;
    qualifiedName?: string;
    callMsg?: string;
    returnMsg?: string;
    name?: string;
    oldValue?: any;
    newValue?: any;
    hasChildren?: boolean;
    eventId: string;
}