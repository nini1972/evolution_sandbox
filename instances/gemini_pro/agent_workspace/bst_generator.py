import json
import random

class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

def insert(root, key, animation_steps):
    if root is None:
        animation_steps.append({"action": "insert", "key": key, "parent": None})
        return Node(key)
    
    animation_steps.append({"action": "visit", "key": root.key, "target": key})
    
    if key < root.key:
        root.left = insert(root.left, key, animation_steps)
    else:
        root.right = insert(root.right, key, animation_steps)
    return root

def tree_to_json(root):
    if root is None:
        return []

    nodes = []
    queue = [(root, 0, 0)]  # (node, x, y)
    visited = set()

    while queue:
        current_node, x, y = queue.pop(0)

        if current_node.key in visited:
            continue
        visited.add(current_node.key)

        node_data = {
            "id": current_node.key,  # Using key as id for simplicity
            "key": current_node.key,
            "x": x,
            "y": y,
            "left": current_node.left.key if current_node.left else None,
            "right": current_node.right.key if current_node.right else None
        }
        nodes.append(node_data)

        if current_node.left:
            queue.append((current_node.left, x - 50, y + 50))
        if current_node.right:
            queue.append((current_node.right, x + 50, y + 50))
            
    return nodes

if __name__ == "__main__":
    elements = random.sample(range(1, 100), 15)  # Generate 15 unique random numbers
    
    root = None
    animation_steps = []
    for element in elements:
        root = insert(root, element, animation_steps)

    final_tree_nodes = tree_to_json(root)

    # The animation steps are now simpler, focusing on just the action and key
    # We'll re-process these steps to build up the tree at each stage in HTML
    
    output_data = {
        "animation_steps": animation_steps,
        "final_tree": final_tree_nodes
    }

    with open("bst_data.json", "w") as f:
        json.dump(output_data, f, indent=4)
