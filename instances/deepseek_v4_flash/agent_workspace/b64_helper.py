import base64, sys

# The full hybrid experiment script encoded in base64
script_b64 = ""

if len(sys.argv) > 1 and sys.argv[1] == "gen":
    # Read the file and print its base64
    with open("hybrid_1_lsystem_rule30.py", "rb") as f:
        data = f.read()
    print(base64.b64encode(data).decode())
