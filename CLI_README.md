# AI Context CLI Tool

A command-line tool for working with `.aicontext` files as defined by the [AI Context Standard](./SPEC.md). This tool automatically discovers commands based on your project's file hierarchy and content sections, allowing LLMs and developers to easily access relevant context.

## Features

🔍 **Auto-Discovery**: Automatically discovers available commands from your `.aicontext` files  
🏗️ **Hierarchical**: Properly resolves context hierarchy as per AI Context Standard  
⚡ **Flexible Syntax**: Supports both `--command` and `command` formats  
📄 **Multiple Formats**: Output in text, JSON, or YAML format  
🎯 **File-Specific**: Can target specific files for context resolution  
🔧 **Independent**: Works alongside existing tools without requiring changes

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/ai-context-standard.git
cd ai-context-standard

# Install using the provided script
./install.sh

# Or install manually
pip install -r requirements.txt
pip install -e .
```

### Basic Usage

```bash
# List all available commands based on your .aicontext files
aicontext --list-commands

# Show architecture section
aicontext architecture
aicontext --architecture

# Show coding standards
aicontext coding-standards
aicontext --coding-standards

# Show all context
aicontext full
aicontext --full

# Get context for a specific file
aicontext --file src/components/Button.tsx architecture

# Output in JSON format
aicontext --format json architecture
```

## How It Works

The tool scans your directory tree for `.aicontext` files and:

1. **Discovers Commands**: Extracts section names (like "Architecture", "Coding Standards") and converts them to commands
2. **Resolves Hierarchy**: Merges context from multiple files according to the AI Context Standard
3. **Provides Flexible Access**: Allows both `--flag` and `flag` syntax for commands
4. **Supports Aliases**: Common aliases like `arch` for `architecture`, `deps` for `dependencies`

### Command Discovery Examples

Given this `.aicontext` file:
```markdown
---
version: "1.0"
---

# My Project

## Architecture
System design details...

## Coding Standards  
Style guidelines...

## Testing Strategy
Test approaches...
```

The tool automatically creates these commands:
- `architecture` / `--architecture` / `arch`
- `coding-standards` / `--coding-standards` / `standards`
- `testing-strategy` / `--testing-strategy`

## Command Reference

### Core Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `architecture` | `arch`, `structure` | Show architecture section |
| `coding-standards` | `standards`, `code-standards`, `style` | Show coding standards |
| `overview` | `summary`, `about` | Show project overview |
| `dependencies` | `deps`, `libraries` | Show dependencies information |
| `context-hints` | `hints`, `context` | Show context hints |
| `full` | `all`, `everything` | Show all context sections |

### Options

| Option | Description |
|--------|-------------|
| `--list-commands` | List all available commands |
| `--file FILE` | Target specific file for context |
| `--format FORMAT` | Output format: `text`, `json`, `yaml` |
| `--help` | Show help message |

## Examples

### Basic Project Context

Create a `.aicontext` file:
```markdown
---
version: "1.0"
---

# React App

## Architecture
- Next.js 14 with App Router
- TypeScript throughout
- Tailwind for styling

## Coding Standards
- Use functional components
- Include prop interfaces
- Follow ESLint rules
```

Use the CLI:
```bash
$ aicontext --list-commands
Available commands:
  architecture
  --architecture
  coding-standards
  --coding-standards
  # ... more commands

$ aicontext architecture
- Next.js 14 with App Router
- TypeScript throughout  
- Tailwind for styling
```

### Hierarchical Context

With nested `.aicontext` files:
```
project/
├── .aicontext              # Project-wide context
├── src/
│   ├── components/
│   │   └── .aicontext     # Component-specific rules
│   └── api/
│       └── .aicontext     # API-specific guidelines
```

The tool automatically merges context from all relevant files:
```bash
# From project/src/components/
$ aicontext architecture
# Shows merged architecture from project/.aicontext and components/.aicontext
```

### File-Specific Context

Target specific files:
```bash
# Get context specific to a TypeScript file
aicontext --file src/utils/helpers.ts coding-standards

# Get context for a React component
aicontext --file src/components/Button.tsx architecture
```

### JSON Output for Tool Integration

```bash
$ aicontext --format json architecture
{
  "command": "architecture", 
  "content": "- Next.js 14 with App Router\n- TypeScript throughout\n- Tailwind for styling"
}
```

## Integration with AI Tools

This tool is designed to be used by LLMs and AI coding assistants:

```bash
# LLM can discover available commands
aicontext --list-commands

# Get specific context sections
aicontext architecture
aicontext coding-standards  

# Get full project context
aicontext full

# Get context in structured format
aicontext --format json full
```

## Advanced Usage

### Custom Section Discovery

The tool automatically discovers any section in your `.aicontext` files:

```markdown
## Custom Deployment Process
Deploy using our internal tools...

## Security Guidelines  
Follow these security practices...
```

Becomes:
- `custom-deployment-process`
- `security-guidelines`

### File Pattern Support

Use `applies_to` in frontmatter to target specific file types:

```yaml
---
version: "1.0"
applies_to: ["*.tsx", "*.jsx"]
---
```

Then:
```bash
# Only shows context for React files
aicontext --file Button.tsx coding-standards
```

## Development

### Running Tests

```bash
# Create test .aicontext files
mkdir -p test-project/src/components
echo "## Architecture\nTest architecture" > test-project/.aicontext

# Test the tool
cd test-project
aicontext --list-commands
aicontext architecture
```

### Contributing

1. Fork the repository
2. Make your changes
3. Test with various `.aicontext` file configurations
4. Submit a pull request

## Troubleshooting

**Command not found**: Make sure the tool is in your PATH after installation
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**No commands available**: Ensure you have `.aicontext` files in your project directory

**Invalid YAML**: The tool will skip invalid frontmatter and continue with content parsing

## License

This tool is released under the same license as the AI Context Standard specification: [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) - dedicated to the public domain.