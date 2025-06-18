#!/usr/bin/env python

import argparse
import importlib.util
import inspect
import os
import re
import shutil
import sys


def load_module(module_path):
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def format_google_docstring(docstring):
    if not docstring:
        return 'TBD'

    lines = docstring.splitlines()
    formatted = []
    section = None
    collecting = []

    def flush_section():
        nonlocal section, collecting
        if section and collecting:
            formatted.append(f'**{section}:**\n')

            prev_indent = None
            first_line_output = False
            for i, line in enumerate(collecting):
                if not line.strip():
                    continue

                indent = len(line) - len(line.lstrip())
                stripped_line = line.strip()

                if not first_line_output:
                    # First line: type only (e.g., Union[str, None]:)
                    match = re.match(r'^([\w\[\],. ]+):\s*$', stripped_line)
                    if match:
                        type_line = match.group(1)
                        formatted.append(f'- `{type_line}`:')
                        first_line_output = True
                        continue

                # Already markdown-formatted (e.g., '- str: ...')
                if stripped_line.startswith(('-', '*')):
                    formatted.append(f'  {stripped_line}')  # Indent once
                    continue

                # Name/type/desc pattern
                match = re.match(
                    r'^(\w+)\s*\(([^)]+)\):\s*(.*)', stripped_line)
                if match:
                    name, type_, desc = match.groups()
                    formatted.append(f'- `{name}` ({type_}): {desc}')
                    prev_indent = indent
                    continue

                # Return/param type only
                match = re.match(r'^([^:]+):\s*(.*)', stripped_line)
                if match:
                    type_, desc = match.groups()
                    formatted.append(f'- `{type_.strip()}`: {desc.strip()}')
                    prev_indent = indent
                    continue

                # Fallback: continuation
                if prev_indent is not None:
                    formatted.append(f'  {stripped_line}')
                else:
                    formatted.append(f'- {stripped_line}')

            formatted.append('')  # Blank line
        collecting = []
        section = None

    for line in lines:
        stripped = line.strip()

        # First: detect one-liner sections like 'Note: something'
        one_liner_match = re.match(
            r'^(Note|Notes|Warning|Warnings):\s*(.+)', stripped)
        if one_liner_match:
            flush_section()
            title, content = one_liner_match.groups()
            formatted.append(f'**{title}:**\n')
            formatted.append(f'{content}\n')
            continue

        section_match = re.match(
            r'^(Args|Arguments|Parameters|Returns|Yields|Raises|Examples|Note|Notes):$',
            stripped)
        if section_match:
            flush_section()
            section = section_match.group(1)
        elif section:
            if line.strip():
                collecting.append(line)
        else:
            formatted.append(stripped)

    flush_section()
    return '\n'.join(formatted)


def format_function(func):
    name = func.__name__
    doc = format_google_docstring(inspect.getdoc(func))
    signature = inspect.signature(func)
    return f'### `{name}`()\n\n```python\n{name}{signature}\n```\n\n{doc}\n\n'


def format_class(cls):
    name = cls.__name__
    doc = format_google_docstring(inspect.getdoc(cls))
    methods = inspect.getmembers(cls, predicate=inspect.isfunction)

    result = f'## Class: `{name}`\n\n{doc}\n\n'
    for _, method in methods:
        if method.__qualname__.startswith(f'{cls.__name__}.'):
            result += format_function(method)
    return result


def generate_markdown(module_path):
    module = load_module(module_path)
    docs = f'# API Documentation for `{module.__name__}`\n\n'
    members = inspect.getmembers(module)

    for name, obj in members:
        if inspect.isfunction(obj) and obj.__module__ == module.__name__:
            docs += format_function(obj)
        elif inspect.isclass(obj) and obj.__module__ == module.__name__:
            docs += format_class(obj)

    return docs


def collect_python_files(directory):
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                py_files.append(os.path.join(root, file))
    return py_files


def process_directory(source_dir, output_dir):
    py_files = collect_python_files(source_dir)
    os.makedirs(output_dir, exist_ok=True)

    for file_path in py_files:
        try:
            markdown = generate_markdown(file_path)
            rel_path = os.path.relpath(file_path, source_dir)
            md_filename = os.path.splitext(rel_path)[0] + '.md'
            output_path = os.path.join(output_dir, md_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f'[OK]: {file_path} ==>> {output_path}')
        except Exception as e:
            print(f'[NG]: Error processing {file_path}: {e}')


def remove_pycache_dirs(directory):
    for root, dirs, _ in os.walk(directory):
        for d in dirs:
            if d == '__pycache__':
                pycache_path = os.path.join(root, d)
                try:
                    shutil.rmtree(pycache_path)
                    print(f'[OK] Removed: {pycache_path}')
                except Exception as e:
                    print(f'[NG] Failed to remove {pycache_path}: {e}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate Markdown API documentation (Google style docstring).')
    parser.add_argument(
        '-i',
        '--input-dir', default='.',
        help='Input directory containing Python files (default: current directory)')
    parser.add_argument(
        '-o',
        '--output-dir', default='.',
        help='Directory to output Markdown files (default: current directory)')
    parser.add_argument(
        '-c',
        '--clean-pycache', action='store_true',
        help='Delete __pycache__ directories after processing')
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f'Error: {args.input_dir} is not a valid directory.')
        sys.exit(1)

    process_directory(args.input_dir, args.output_dir)

    if args.clean_pycache:
        remove_pycache_dirs(args.input_dir)
