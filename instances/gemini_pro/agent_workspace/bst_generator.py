import json
import random

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

    def to_dict(self):
        return {
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

def insert(root, value, history):
    if root is None:
        new_node = Node(value)
        history.append(new_node.to_dict())
        return new_node
    else:
        if value < root.value:
            root.left = insert(root.left, value, history)
        else:
            root.right = insert(root.right, value, history)
        history.append(root.to_dict())
        return root

def build_bst_with_history(numbers):
    root = None
    history = []
    # Add initial empty tree to history
    history.append(None)

    for number in numbers:
        # Make a deep copy of the current root state to add to history
        # before modifying it further. This requires careful handling
        # for recursive data structures. For simplicity in JSON, we'll 
        # just append the state *after* each insertion.
        if root is None:
            root = insert(root, number, history)
        else:
            # To capture snapshots at each insertion step, we need to manually
            # re-insert each number into a new tree (or a deep copy) and trace it.
            # For a simpler history, we will capture the tree's state after each *successful* insertion of a number.
            # The `insert` function currently appends dict representations potentially multiple times during recursion.
            # Let's refactor `insert` to only append the *final* tree state after a number is fully inserted.
            pass # This part needs modification. Resetting `insert` design.
    
    # Redesigning the history capture for BST build
    history_of_trees = []
    current_root = None
    for number in numbers:
        temp_history_for_one_insertion = []
        if current_root is None:
            current_root = Node(number)
        else:
            node_to_insert = Node(number)
            curr = current_root
            while True:
                if number < curr.value:
                    if curr.left is None:
                        curr.left = node_to_insert
                        break
                    else:
                        curr = curr.left
                else:
                    if curr.right is None:
                        curr.right = node_to_insert
                        break
                    else:
                        curr = curr.right
        history_of_trees.append(current_root.to_dict())

    return history_of_trees


if __name__ == "__main__":
    # Generate a random list of numbers
    SIZE = 15 # Number of elements to insert
    MIN_VALUE = 1
    MAX_VALUE = 100
    random_numbers = random.sample(range(MIN_VALUE, MAX_VALUE + 1), SIZE)

    # Build BST and record history
    bst_history = build_bst_with_history(random_numbers)

    output_data = {
        "initial_numbers": random_numbers,
        "bst_history": bst_history
    }

    with open("bst_data.json", "w") as f:
        json.dump(output_data, f, indent=4)
