import * as vscode from 'vscode';
import { ObjWatchDocument } from '../models/document';
import { ObjWatchEditor } from '../views/editor';

export class ObjWatchVisualizerProvider implements vscode.CustomReadonlyEditorProvider<ObjWatchDocument> {
    constructor(private readonly context: vscode.ExtensionContext) {}

    async openCustomDocument(uri: vscode.Uri): Promise<ObjWatchDocument> {
        return await ObjWatchDocument.create(uri);
    }

    async resolveCustomEditor(
        document: ObjWatchDocument,
        webviewPanel: vscode.WebviewPanel
    ): Promise<void> {
        new ObjWatchEditor(this.context, document, webviewPanel);
    }
}