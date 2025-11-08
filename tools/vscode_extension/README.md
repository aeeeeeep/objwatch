# ObjWatch Log Viewer - VSCode Extension

\[ English | [中文](README_zh.md) \]

<img src="images/objwatch-logo.png" width="256px" alt="ObjWatch Logo">

Enhanced viewer for ObjWatch debugging logs with syntax highlighting, nested structure recognition, and folding support.

## Features

- **Syntax Highlighting**: Differentiated colors for various log elements like line numbers, event types, function names, and variable names
- **Nested Structure Recognition**: Automatically identifies the hierarchical structure of logs based on indentation
- **Folding/Unfolding**: Supports collapsing and expanding nested log nodes for better readability of complex logs
- **Custom Commands**: Provides commands for toggling folding and formatting logs

## Event Types Highlighting

- `run`: Function execution start
- `end`: Function execution end
- `upd`: Variable update
- `apd`: Collection element addition
- `pop`: Collection element removal

## Usage

1. Open any `.objwatch` log file in VSCode
2. The extension will automatically activate and apply syntax highlighting
3. Use the fold/unfold controls in the gutter to collapse/expand nested sections

## Configuration

The extension provides the following configuration options:

- `objwatch-log-viewer.enableFolding`: Enable code folding for ObjWatch logs (default: true)
- `objwatch-log-viewer.highlightEventTypes`: Highlight different event types with different colors (default: true)
- `objwatch-log-viewer.enableIndentRainbow`: Enable indentation rainbow highlighting for ObjWatch logs (default: true)
- `objwatch-log-viewer.indentRainbowColors`: Colors used for indentation highlighting (default: [
  "rgba(255,255,64,0.07)",
  "rgba(127,255,127,0.07)",
  "rgba(255,127,255,0.07)",
  "rgba(79,236,236,0.07)"
])
- `objwatch-log-viewer.indentRainbowErrorColor`: Color used to highlight indentation errors (default: "rgba(128,32,32,0.3)")
- `objwatch-log-viewer.indentRainbowIndicatorStyle`: Style of indentation indicators (default: "classic", options: "classic", "light")

## Log Format

The extension supports the ObjWatch log format with the following structure:

"{line_number} {'  '*call_depth}{event_type} {object_string} {message_string}", for example:

```
  69 run __main__.main <- 
  61     run __main__.TestClass.outer_function <- '0':(type)TestClass
  10         upd TestClass.a None -> 10
  ...
  61     end __main__.TestClass.outer_function -> [(list)[200, 3, 4, '... (1 more elements)']]
  69 end __main__.main -> None
```

Where:
- Line numbers are right-aligned
- Nested levels are indicated by 2 spaces per level

## Development

To set up the development environment:

1. Clone the repository
2. Navigate to the extension directory (`tools/vscode_extension`)
3. Run `npm install` to install dependencies
4. Press `F5` to start debugging the extension in a new VSCode window
