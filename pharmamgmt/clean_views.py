#!/usr/bin/env python
import os

def clean_duplicate_functions():
    views_file = r"c:\pharmaproject pratk\WebsiteHostingService\WebsiteHostingService\WebsiteHostingService\pharmamgmt\core\views.py"
    
    with open(views_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the line numbers of duplicate functions
    sale_rate_list_lines = []
    for i, line in enumerate(lines):
        if line.strip() == "def sale_rate_list(request):":
            sale_rate_list_lines.append(i)
    
    print(f"Found sale_rate_list functions at lines: {[x+1 for x in sale_rate_list_lines]}")
    
    # Keep only the first function and remove duplicates
    if len(sale_rate_list_lines) > 1:
        # Find the end of each function
        function_ranges = []
        for start_line in sale_rate_list_lines:
            end_line = start_line + 1
            # Find the next function or end of file
            while end_line < len(lines):
                if lines[end_line].startswith('def ') or lines[end_line].startswith('@'):
                    break
                end_line += 1
            function_ranges.append((start_line, end_line))
        
        print(f"Function ranges: {function_ranges}")
        
        # Remove duplicate functions (keep the first one)
        new_lines = []
        skip_ranges = function_ranges[1:]  # Skip all except the first
        
        i = 0
        while i < len(lines):
            should_skip = False
            for start, end in skip_ranges:
                if start <= i < end:
                    should_skip = True
                    break
            
            if not should_skip:
                new_lines.append(lines[i])
            i += 1
        
        # Write back to file
        with open(views_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"Removed {len(skip_ranges)} duplicate functions")
    else:
        print("No duplicate functions found")

if __name__ == "__main__":
    clean_duplicate_functions()