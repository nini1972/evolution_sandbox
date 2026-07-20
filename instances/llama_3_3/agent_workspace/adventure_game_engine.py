
# adventure_game_engine.py

# Game World Definition
rooms = {
    'start_room': {
        'description': "You are in a dimly lit chamber. A flickering torch barely illuminates ancient carvings on the walls.",
        'exits': {'north': 'dark_corridor', 'east': 'storage_room'}
    },
    'dark_corridor': {
        'description': "The corridor is cold and damp. You hear a faint dripping sound from further north.",
        'exits': {'south': 'start_room', 'north': 'cavern'}
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
        'location': 'storage_room'
    },
    'torch': {
        'description': "A wooden torch, still flickering.",
        'location': 'start_room'
    }
}

# Player State
player_inventory = []
current_room = 'start_room'

# --- Game Functions (to be implemented later) ---
def display_room_info():
    global current_room, items

    print(f"\n--- {current_room.replace('_', ' ').title()} ---")
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

