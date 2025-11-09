// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');

// Global variables for indent rainbow functionality
let indentDecorationTypes = [];
let indentErrorDecorationType = null;
let activeEditor = null;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('ObjWatch Log Viewer extension is now active!');

    // Initialize indent rainbow functionality
    initializeIndentRainbow();

    // Listen for editor changes
    activeEditor = vscode.window.activeTextEditor;
    if (activeEditor && activeEditor.document.languageId === 'objwatch') {
        triggerUpdateIndentDecorations();
    }

    vscode.window.onDidChangeActiveTextEditor(editor => {
        activeEditor = editor;
        if (editor && editor.document.languageId === 'objwatch') {
            triggerUpdateIndentDecorations();
        }
    }, null, context.subscriptions);

    vscode.workspace.onDidChangeTextDocument(event => {
        if (activeEditor && event.document === activeEditor.document &&
            activeEditor.document.languageId === 'objwatch') {
            triggerUpdateIndentDecorations();
        }
    }, null, context.subscriptions);

    vscode.workspace.onDidChangeConfiguration(configChangeEvent => {
        if (configChangeEvent.affectsConfiguration('objwatch-log-viewer')) {
            initializeIndentRainbow();
            if (activeEditor && activeEditor.document.languageId === 'objwatch') {
                triggerUpdateIndentDecorations();
            }
        }
    }, null, context.subscriptions);

    // Register folding provider for ObjWatch logs
    const foldingProvider = vscode.languages.registerFoldingRangeProvider('objwatch', {
        provideFoldingRanges(document, context, token) {
            const ranges = [];
            const stack = [];
            const lineCount = document.lineCount;

            for (let line = 0; line < lineCount; line++) {
                const fullLine = document.lineAt(line).text;
                const trimmedLine = fullLine.trim();
                if (!trimmedLine) continue;

                // No longer skipping lines starting with #, now using === as block comments

                // Get indentation level by counting actual spaces in the line
                // This works for various log formats and indentation patterns
                const indentMatch = fullLine.match(/^(\s+)(\d+\s+)/);
                let indentLevel = 0;
                if (indentMatch && indentMatch[1]) {
                    // Use the actual space count as indentation level
                    indentLevel = indentMatch[1].length;
                }

                // Extract event type using regex
                const eventMatch = trimmedLine.match(/^(?:\d+\s+)?(run|end|upd|apd|pop)\s+/);
                const eventType = eventMatch ? eventMatch[1] : null;

                // Process run events (start of folding block)
                if (eventType === 'run') {
                    stack.push({ line, indentLevel, text: trimmedLine });
                }
                // Process end events (end of folding block)
                else if (eventType === 'end') {
                    // Find matching run event with the same indentation
                    let matchingStartIndex = -1;
                    for (let i = stack.length - 1; i >= 0; i--) {
                        const item = stack[i];
                        // Use exact space count for matching
                        // We already ensured it's a run event when pushing to stack
                        if (item.indentLevel === indentLevel) {
                            matchingStartIndex = i;
                            break;
                        }
                    }

                    // If we found a matching start event
                    if (matchingStartIndex !== -1) {
                        const startItem = stack[matchingStartIndex];
                        // Create folding range from start to end line
                        ranges.push(new vscode.FoldingRange(
                            startItem.line,
                            line,
                            vscode.FoldingRangeKind.Region
                        ));
                        // Remove only the matched run event from stack
                        stack.splice(matchingStartIndex, 1);
                    }
                }
            }

            return ranges;
        }
    });

    // Register command to toggle folding
    const toggleFoldingCommand = vscode.commands.registerCommand('objwatch-log-viewer.toggleFolding', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'objwatch') {
            vscode.window.showInformationMessage('Please open an ObjWatch log file first');
            return;
        }

        // Get configuration
        const config = vscode.workspace.getConfiguration('objwatch-log-viewer');
        const newEnabled = !config.get('enableFolding');
        await config.update('enableFolding', newEnabled, vscode.ConfigurationTarget.Global);

        vscode.window.showInformationMessage(`ObjWatch log folding ${newEnabled ? 'enabled' : 'disabled'}`);

        // Refresh editor
        editor.document.save();
    });

    // Register command to format log
    const formatLogCommand = vscode.commands.registerCommand('objwatch-log-viewer.formatLog', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'objwatch') {
            vscode.window.showInformationMessage('Please open an ObjWatch log file first');
            return;
        }

        // Simple formatting: ensure consistent indentation
        const text = editor.document.getText();
        const lines = text.split('\n');
        const formattedLines = [];

        for (const line of lines) {
            // Ensure line numbers are properly aligned
            const match = line.match(/^(\s*)(\d+)(\s+)(.*)$/);
            if (match) {
                const spaces = '   '; // 3 spaces before line number
                const lineNum = match[2].padStart(5, ' ');
                formattedLines.push(`${spaces}${lineNum}${match[3]}${match[2]}`);
            } else {
                formattedLines.push(line);
            }
        }

        // Apply formatting
        const edit = new vscode.WorkspaceEdit();
        const range = new vscode.Range(
            editor.document.positionAt(0),
            editor.document.positionAt(text.length)
        );
        edit.replace(editor.document.uri, range, formattedLines.join('\n'));
        await vscode.workspace.applyEdit(edit);

        vscode.window.showInformationMessage('ObjWatch log formatted successfully');
    });

    // Add to subscriptions
    context.subscriptions.push(foldingProvider);
    context.subscriptions.push(toggleFoldingCommand);
    context.subscriptions.push(formatLogCommand);
}

function deactivate() {
    console.log('ObjWatch Log Viewer extension is now deactivated!');
}

// Initialize indent rainbow functionality
function initializeIndentRainbow() {
    // Clean up previous decorations
    indentDecorationTypes.forEach(decorationType => {
        decorationType.dispose();
    });
    indentDecorationTypes = [];

    if (indentErrorDecorationType) {
        indentErrorDecorationType.dispose();
        indentErrorDecorationType = null;
    }

    const config = vscode.workspace.getConfiguration('objwatch-log-viewer');
    const enableIndentRainbow = config.get('enableIndentRainbow', true);

    if (!enableIndentRainbow) {
        return;
    }

    const colors = config.get('indentRainbowColors', [
        "rgba(255,255,64,0.07)",
        "rgba(127,255,127,0.07)",
        "rgba(255,127,255,0.07)",
        "rgba(79,236,236,0.07)"
    ]);

    const errorColor = config.get('indentRainbowErrorColor', "rgba(128,32,32,0.3)");
    const indicatorStyle = config.get('indentRainbowIndicatorStyle', 'classic');

    // Create error decoration
    indentErrorDecorationType = vscode.window.createTextEditorDecorationType({
        backgroundColor: errorColor
    });

    // Create decorations for each indentation level
    colors.forEach((color, index) => {
        if (indicatorStyle === 'classic') {
            indentDecorationTypes[index] = vscode.window.createTextEditorDecorationType({
                backgroundColor: color
            });
        } else if (indicatorStyle === 'light') {
            indentDecorationTypes[index] = vscode.window.createTextEditorDecorationType({
                borderStyle: "solid",
                borderColor: color,
                borderWidth: "0 0 0 1px"
            });
        }
    });
}

// Trigger update of indent decorations
let indentUpdateTimeout = null;
function triggerUpdateIndentDecorations() {
    if (indentUpdateTimeout) {
        clearTimeout(indentUpdateTimeout);
    }
    indentUpdateTimeout = setTimeout(updateIndentDecorations, 100);
}

// Update indent decorations
function updateIndentDecorations() {
    if (!activeEditor || !indentDecorationTypes.length) {
        return;
    }

    const config = vscode.workspace.getConfiguration('objwatch-log-viewer');
    const enableIndentRainbow = config.get('enableIndentRainbow', true);

    if (!enableIndentRainbow) {
        return;
    }

    const document = activeEditor.document;
    const decorators = indentDecorationTypes.map(() => []);
    const errorDecorators = [];

    // 遍历每一行
    for (let lineNum = 0; lineNum < document.lineCount; lineNum++) {
        const line = document.lineAt(lineNum);
        const lineText = line.text;

        // Match line number format: any spaces + digits + spaces + content
        const match = lineText.match(/^(\s*)(\d+)(\s+)(.*)$/);
        if (match) {
            // Skip spaces before line number
            // Skip line number itself
            // Skip one space after line number
            const lineNumberPrefix = match[1]; // Spaces before line number
            const lineNumber = match[2];        // Line number itself
            const afterLineNumber = match[3];   // All spaces after line number

            // Calculate position after skipping one space and remaining indentation
            const skipOneSpace = afterLineNumber.length > 0 ? 1 : 0;
            const indentStartPos = lineNumberPrefix.length + lineNumber.length + skipOneSpace;
            const remainingIndent = afterLineNumber.substring(skipOneSpace);
            const indentEndPos = indentStartPos + remainingIndent.length;

            // Calculate remaining indentation level (based on space count)
            const spaceCount = remainingIndent.replace(/\t/g, ' '.repeat(2)).length;

            // Check for indentation errors (not multiples of 2)
            if (spaceCount > 0 && spaceCount % 2 !== 0) {
                const startPos = new vscode.Position(lineNum, indentStartPos);
                const endPos = new vscode.Position(lineNum, indentEndPos);
                errorDecorators.push({
                    range: new vscode.Range(startPos, endPos)
                });
            }

            // Create decorations for each indentation level
            let pos = indentStartPos;
            for (let i = 0; i < spaceCount; i += 2) {
                const level = (i / 2) % decorators.length;
                const startPos = new vscode.Position(lineNum, pos);
                const endPos = new vscode.Position(lineNum, Math.min(pos + 2, indentEndPos));
                decorators[level].push({
                    range: new vscode.Range(startPos, endPos)
                });
                pos += 2;
            }
        }
    }

    // Apply decorations
    indentDecorationTypes.forEach((decorationType, index) => {
        activeEditor.setDecorations(decorationType, decorators[index]);
    });

    if (indentErrorDecorationType) {
        activeEditor.setDecorations(indentErrorDecorationType, errorDecorators);
    }
}

module.exports = {
    activate,
    deactivate
};