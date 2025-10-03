#!/usr/bin/env python3
"""
Script to fix indentation issues in portfolio_dashboard.py
"""
import re

def fix_indentation():
    with open('portfolio_dashboard.py', 'r') as f:
        content = f.read()

    # Fix common indentation issues
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        line_num = i + 1

        # Fix lines that start with too many spaces before 'return'
        if re.match(r'^\s{12,}return\s*{', line):
            # Replace with proper 8-space indentation
            fixed_line = '        ' + line.strip()
            print(f"Fixed line {line_num}: {line.strip()} -> {fixed_line}")
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)

    # Write back the fixed content
    with open('portfolio_dashboard.py', 'w') as f:
        f.write('\n'.join(fixed_lines))

    print("✅ Indentation fixes applied!")

if __name__ == "__main__":
    fix_indentation()

