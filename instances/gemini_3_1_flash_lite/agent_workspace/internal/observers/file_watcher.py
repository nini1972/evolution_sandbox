import os
import time

def list_files():
    files = os.listdir('.')
    with open('file_history.log', 'a') as f:
        f.write(f"{time.ctime()}: {len(files)} files currently in workspace.\n")

if __name__ == '__main__':
    list_files()
