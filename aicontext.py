#!/usr/bin/env python3
"""
AI Context CLI Tool

A command-line tool for working with .aicontext files as defined by the AI Context Standard.
Automatically discovers commands based on file hierarchy and content sections.
"""

import os
import sys
import argparse
import yaml
import re
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import markdown


@dataclass
class ContextFile:
    """Represents a parsed .aicontext file"""
    path: Path
    version: str
    extends: List[str]
    applies_to: List[str]
    ignore: List[str]
    metadata: Dict[str, Any]
    content: str
    sections: Dict[str, str]


class ContextParser:
    """Parses .aicontext files according to the AI Context Standard"""
    
    def __init__(self):
        self.parsed_files: Dict[str, ContextFile] = {}
    
    def parse_file(self, file_path: Path) -> Optional[ContextFile]:
        """Parse a single .aicontext file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split frontmatter and content
            frontmatter = {}
            markdown_content = content
            
            if content.startswith('---\n'):
                try:
                    # Find end of frontmatter
                    end_idx = content.find('\n---\n', 4)
                    if end_idx != -1:
                        frontmatter_text = content[4:end_idx]
                        markdown_content = content[end_idx + 5:]
                        frontmatter = yaml.safe_load(frontmatter_text) or {}
                except yaml.YAMLError:
                    # Skip invalid YAML, continue with content
                    pass
            
            # Extract sections from markdown
            sections = self._extract_sections(markdown_content)
            
            context_file = ContextFile(
                path=file_path,
                version=frontmatter.get('version', '1.0'),
                extends=frontmatter.get('extends', []),
                applies_to=frontmatter.get('applies_to', []),
                ignore=frontmatter.get('ignore', []),
                metadata=frontmatter.get('metadata', {}),
                content=markdown_content,
                sections=sections
            )
            
            self.parsed_files[str(file_path)] = context_file
            return context_file
            
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
            return None
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract markdown sections and their content"""
        sections = {}
        
        # Split by headers (## or ###)
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for section headers
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line[3:].strip().lower()
                current_content = []
            elif line.startswith('### '):
                # Subsection - treat as part of current section
                current_content.append(line)
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections


class ContextResolver:
    """Resolves context hierarchy according to the AI Context Standard"""
    
    def __init__(self, parser: ContextParser):
        self.parser = parser
    
    def find_context_files(self, start_path: Path) -> List[Path]:
        """Find all .aicontext files in directory tree"""
        context_files = []
        
        # Walk up the directory tree
        current_path = start_path.resolve()
        while True:
            context_file = current_path / '.aicontext'
            if context_file.exists():
                context_files.append(context_file)
            
            parent = current_path.parent
            if parent == current_path:  # Reached root
                break
            current_path = parent
        
        # Reverse to get root-to-leaf order
        return list(reversed(context_files))
    
    def resolve_context(self, target_file: Optional[Path] = None) -> Dict[str, str]:
        """Resolve merged context for a target file or directory"""
        if target_file is None:
            target_file = Path.cwd()
        
        if target_file.is_file():
            search_path = target_file.parent
        else:
            search_path = target_file
        
        context_files = self.find_context_files(search_path)
        merged_sections = {}
        
        # Process files in hierarchy order (root to leaf)
        for file_path in context_files:
            context = self.parser.parse_file(file_path)
            if context:
                # Check if applies to target file
                if target_file.is_file() and context.applies_to:
                    if not self._file_matches_patterns(target_file, context.applies_to):
                        continue
                
                # Merge sections (child overrides parent)
                merged_sections.update(context.sections)
        
        return merged_sections
    
    def _file_matches_patterns(self, file_path: Path, patterns: List[str]) -> bool:
        """Check if file matches any of the given patterns"""
        filename = file_path.name
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False


class CommandDiscovery:
    """Discovers available commands from context files"""
    
    def __init__(self, resolver: ContextResolver):
        self.resolver = resolver
    
    def get_available_commands(self, target_path: Optional[Path] = None) -> Set[str]:
        """Get all available commands based on context sections"""
        sections = self.resolver.resolve_context(target_path)
        commands = set()
        
        # Add section names as commands
        for section_name in sections.keys():
            # Normalize section names to command format
            command = section_name.replace(' ', '-').lower()
            commands.add(command)
        
        # Add common aliases
        command_aliases = {
            'architecture': ['arch', 'structure'],
            'coding-standards': ['standards', 'code-standards', 'style'],
            'overview': ['summary', 'about'],
            'dependencies': ['deps', 'libraries'],
            'context-hints': ['hints', 'context'],
        }
        
        for command in list(commands):
            if command in command_aliases:
                commands.update(command_aliases[command])
        
        return commands
    
    def execute_command(self, command: str, target_path: Optional[Path] = None) -> str:
        """Execute a command and return the relevant context"""
        sections = self.resolver.resolve_context(target_path)
        
        # Normalize command
        normalized_command = command.replace('-', ' ').lower()
        
        # Try exact match first
        if normalized_command in sections:
            return sections[normalized_command]
        
        # Try with dashes
        dash_command = command.replace(' ', '-').lower()
        if dash_command in [k.replace(' ', '-') for k in sections.keys()]:
            for k, v in sections.items():
                if k.replace(' ', '-') == dash_command:
                    return v
        
        # Check aliases
        alias_map = {
            'arch': 'architecture',
            'structure': 'architecture',
            'standards': 'coding standards',
            'code-standards': 'coding standards',
            'style': 'coding standards',
            'summary': 'overview',
            'about': 'overview',
            'deps': 'dependencies',
            'libraries': 'dependencies',
            'hints': 'context hints',
            'context': 'context hints',
        }
        
        if command.lower() in alias_map:
            return self.execute_command(alias_map[command.lower()], target_path)
        
        # Try partial matches
        for section_name, content in sections.items():
            if normalized_command in section_name.lower():
                return content
        
        # Handle special commands
        if command in ['full', 'all', 'everything']:
            return self._format_full_context(sections)
        
        return f"No content found for command: {command}"
    
    def _format_full_context(self, sections: Dict[str, str]) -> str:
        """Format all sections as full context"""
        output = []
        for section_name, content in sections.items():
            output.append(f"## {section_name.title()}")
            output.append(content)
            output.append("")
        return '\n'.join(output)


def create_cli() -> argparse.ArgumentParser:
    """Create the CLI argument parser"""
    parser = argparse.ArgumentParser(
        prog='aicontext',
        description='AI Context CLI Tool - Work with .aicontext files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aicontext --architecture          Show architecture section
  aicontext architecture            Show architecture section (no dashes)
  aicontext --full                  Show all context
  aicontext --code-standards        Show coding standards
  aicontext --list-commands         List available commands
  
The tool automatically discovers commands from your .aicontext files.
""")
    
    parser.add_argument(
        '--list-commands', 
        action='store_true',
        help='List all available commands based on current context files'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=Path,
        help='Target file to get context for (default: current directory)'
    )
    
    parser.add_argument(
        '--format', 
        choices=['text', 'json', 'yaml'],
        default='text',
        help='Output format (default: text)'
    )
    
    # Add dynamic arguments - we'll handle these specially
    parser.add_argument(
        'command',
        nargs='?',
        help='Command to execute (try --list-commands to see available)'
    )
    
    return parser


def main():
    """Main CLI entry point"""
    # Create parser and discovery system
    context_parser = ContextParser()
    resolver = ContextResolver(context_parser)
    discovery = CommandDiscovery(resolver)
    
    # Handle special case for listing commands first
    if '--list-commands' in sys.argv:
        target_path = Path.cwd()
        if '--file' in sys.argv:
            file_idx = sys.argv.index('--file')
            if file_idx + 1 < len(sys.argv):
                target_path = Path(sys.argv[file_idx + 1])
        
        commands = discovery.get_available_commands(target_path)
        print("Available commands:")
        for command in sorted(commands):
            print(f"  {command}")
            print(f"  --{command}")
        return
    
    # Parse known args first
    parser = create_cli()
    args, unknown = parser.parse_known_args()
    
    # Handle dynamic command discovery
    target_path = args.file or Path.cwd()
    available_commands = discovery.get_available_commands(target_path)
    
    # Add common commands to available list
    available_commands.update(['full', 'all', 'everything'])
    
    # Check if any unknown args are actually valid commands
    command_to_execute = args.command
    
    # Handle --command format
    for arg in unknown:
        if arg.startswith('--') and arg[2:] in available_commands:
            command_to_execute = arg[2:]
            break
    
    # Also check for commands without dashes in remaining args
    if not command_to_execute:
        for arg in unknown:
            if not arg.startswith('-') and arg in available_commands:
                command_to_execute = arg
                break
    
    # Check if a direct argument was provided (covers cases like `aicontext full`)
    if not command_to_execute and args.command:
        if args.command in available_commands:
            command_to_execute = args.command
    
    if not command_to_execute:
        parser.print_help()
        print("\nAvailable commands:", ', '.join(sorted(available_commands)))
        return
    
    # Execute the command
    try:
        result = discovery.execute_command(command_to_execute, target_path)
        
        if args.format == 'json':
            import json
            print(json.dumps({"command": command_to_execute, "content": result}))
        elif args.format == 'yaml':
            print(yaml.dump({"command": command_to_execute, "content": result}))
        else:
            print(result)
            
    except Exception as e:
        print(f"Error executing command '{command_to_execute}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()