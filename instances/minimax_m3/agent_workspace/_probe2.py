"""Tiny probe: raw Python with quotes inside, written via write_file."""
def hello():
    return "double-quoted string inside a function"
x = {"k": 'single-quoted too', "weird": "she said \"hi\""}
print(hello(), x)