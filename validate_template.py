#!/usr/bin/env python3
"""
Template Validation Script
Checks for Jinja2 template syntax errors
"""

import sys
import os
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

def validate_template():
    """Validate the edit_analyst_profile.html template"""
    try:
        # Set up Jinja2 environment
        template_dir = 'templates'
        env = Environment(loader=FileSystemLoader(template_dir))
        
        # Try to load and parse the template
        template = env.get_template('edit_analyst_profile.html')
        
        print("✅ Template syntax is valid!")
        return True
        
    except TemplateSyntaxError as e:
        print(f"❌ Template Syntax Error:")
        print(f"   Line {e.lineno}: {e.message}")
        print(f"   Template: {e.name}")
        return False
        
    except Exception as e:
        print(f"❌ Error validating template: {e}")
        return False

def check_block_structure():
    """Check the block structure in the template"""
    try:
        with open('templates/edit_analyst_profile.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count block tags
        lines = content.split('\n')
        blocks = []
        
        for i, line in enumerate(lines, 1):
            if '{% block' in line:
                block_name = line.split('{% block')[1].split('%}')[0].strip()
                blocks.append((i, 'start', block_name))
            elif '{% endblock' in line:
                blocks.append((i, 'end', ''))
        
        print("\n📋 Block Structure Analysis:")
        print("-" * 40)
        
        open_blocks = []
        for line_num, block_type, block_name in blocks:
            if block_type == 'start':
                open_blocks.append((line_num, block_name))
                print(f"Line {line_num}: Start block '{block_name}'")
            else:
                if open_blocks:
                    start_line, start_name = open_blocks.pop()
                    print(f"Line {line_num}: End block (started at line {start_line}: '{start_name}')")
                else:
                    print(f"Line {line_num}: ❌ End block without matching start!")
                    return False
        
        if open_blocks:
            print(f"❌ Unclosed blocks: {open_blocks}")
            return False
        else:
            print("✅ All blocks properly matched!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking block structure: {e}")
        return False

def main():
    print("🔍 TEMPLATE VALIDATION")
    print("=" * 50)
    
    # Check block structure first
    structure_ok = check_block_structure()
    
    # Validate template syntax
    syntax_ok = validate_template()
    
    print("\n📋 VALIDATION SUMMARY:")
    print("=" * 50)
    print(f"📐 Block Structure: {'PASS' if structure_ok else 'FAIL'}")
    print(f"📝 Template Syntax: {'PASS' if syntax_ok else 'FAIL'}")
    
    if structure_ok and syntax_ok:
        print("\n🎉 TEMPLATE IS VALID!")
        return True
    else:
        print("\n❌ TEMPLATE HAS ISSUES!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
