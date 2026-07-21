
# adventure_game_engine.py

# Game World Definition
rooms = {
    'start_room': {
        'description': "You are in a dimly lit chamber. A flickering torch barely illuminates ancient carvings on the walls.",
        'exits': {'north': 'dark_corridor', 'east': 'storage_room'}
    },
    'dark_corridor': {
        'description': "The corridor is cold and damp. You hear a faint dripping sound from further north. It's too dark to see clearly.", # Dark description
        'light_description': "The corridor is still cold and damp, but now illuminated, you see intricate carvings depicting ancient battles on the walls.", # Light description
        'exits': {'south': 'start_room'}
    },
    'storage_room': {
        'description': "Dusty shelves line the walls, filled with forgotten relics. A strange key glints from atop a tall stack of crates.",
        'exits': {'west': 'start_room'}
    },
    'cavern': {
        'description': "A vast underground cavern stretches before you. A mysterious pedestal stands in the center.",
        'exits': {'south': 'dark_corridor'}
    }
}

items = {
    'key': {
        'description': "A small, ornate silver key.",
        'location': 'storage_room',
        'can_use': True,
        'on_use': 'unlock_something'
    },
    'torch': {
        'description': "A wooden torch, still flickering.",
        'location': 'start_room',
        'can_use': True,
        'on_use': 'light_the_way'
    }
}

# Player State
player_inventory = []
current_room = 'start_room'

# New Global States for game progression
is_dark_corridor_lit = False
is_cavern_unlocked = False

# --- Game Functions (to be implemented later) ---
def display_room_info():
    global current_room, items, is_dark_corridor_lit

    print(f"\n--- {current_room.replace('_', ' ').title()} ---")
    
    # Display dynamic room description based on game state
    if current_room == 'dark_corridor' and is_dark_corridor_lit and 'light_description' in rooms[current_room]:
        print(rooms[current_room]['light_description'])
    else:
        print(rooms[current_room]['description'])

    # List items in the current room
    current_room_items = [item_name for item_name, item_data in items.items() if item_data['location'] == current_room]
    if current_room_items:
        print("\nYou see:")
        for item_name in current_room_items:
            print(f"- {items[item_name]['description']} ({item_name.replace('_', ' ').title()})")
    
    print("\nExits:", end=" ")
    exits = rooms[current_room]['exits'].keys()
    print(", ".join(exits))



def apply_item_effect(effect_name):
    global is_dark_corridor_lit, is_cavern_unlocked, rooms

    if effect_name == 'light_the_way':
        is_dark_corridor_lit = True
        print("The dark corridor is now illuminated!")
    elif effect_name == 'unlock_something':
        if not is_cavern_unlocked:
            is_cavern_unlocked = True
            rooms['dark_corridor']['exits']['north'] = 'cavern'
            print("You hear a click as a hidden passage to the cavern opens!")
        else:
            print("It's already unlocked.")
    else:
        print(f"Unhandled effect: {effect_name}")

def handle_command(command):
    global current_room, player_inventory, items

    command_parts = command.split()
    verb = command_parts[0]

    if verb == 'move':
        if len(command_parts) > 1:
            direction = command_parts[1]
            if direction in rooms[current_room]['exits']:
                current_room = rooms[current_room]['exits'][direction]
            else:
                print("You can't go that way.")
        else:
            print("Move where? Specify a direction (e.g., 'move north').")
    elif verb == 'look':
        display_room_info()
    elif verb == 'take':
        if len(command_parts) > 1:
            item_name = command_parts[1]
            # Check if the item is in the current room
            if item_name in items and items[item_name]['location'] == current_room:
                player_inventory.append(item_name)
                items[item_name]['location'] = 'inventory' # Move item to player's inventory
                print(f"You take the {item_name.replace('_', ' ')}.")
            else:
                print("You don't see that here.")
        else:
            print("Take what? Specify an item (e.g., 'take key').")
    elif verb == 'inventory':
        if player_inventory:
            print("Your inventory:")
            for item in player_inventory:
                print(f"- {items[item]['description']} ({item.replace('_', ' ').title()})")
        else:
            print("Your inventory is empty.")
    elif verb == 'use':
        if len(command_parts) > 1:
            item_name = command_parts[1]
            if item_name in player_inventory:
                if items[item_name]['can_use']:
                    print(f"You use the {item_name.replace('_', ' ')}.")
                    apply_item_effect(items[item_name]['on_use'])
                else:
                    print(f"You can't use the {item_name}.")
            else:
                print(f"You don't have a {item_name} in your inventory.")
        else:
            print("Use what? Specify an item (e.g., 'use key').")
    else:
        print("I don't understand that command.")


def save_game(filename='savegame.json'):
    pass

def load_game(filename='savegame.json'):
    pass

# --- Main Game Loop (to be implemented later) ---
if __name__ == "__main__":
    print("Welcome to the Adventure Game!")
    while True:
        display_room_info()
        command = input("> ").lower().strip()
        if command == 'quit':
            print("Thank you for playing!")
            break
        handle_command(command)

