def print_tree(linked_list, indent_level=0):
    base_indent = "    " 
    branch_indent = "│   " if indent_level > 0 else ""
    item_indent = "├── "
    last_item_indent = "└── "
    
    root_label = linked_list[0]
    print(f"{branch_indent * (indent_level - 1)}{last_item_indent if indent_level > 0 else ''}{root_label}")
    
    for i, item in enumerate(linked_list[1:], start=1):
        if isinstance(item, list):
            print_tree(item, indent_level + 1)
        else:
            is_last = i == len(linked_list) - 1
            current_indent = last_item_indent if is_last else item_indent
            print(f"{branch_indent * indent_level}{current_indent}{item}")