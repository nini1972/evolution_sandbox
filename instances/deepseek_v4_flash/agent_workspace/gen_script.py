import base64, sys
# This script will generate the experiment
b64 = sys.argv[1]
code = base64.b64decode(b64).decode()
with open('experiment.py', 'w') as f:
    f.write(code)
print('Written experiment.py')