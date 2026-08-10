import json
c=json.load(open("corpus.json"))
print("TOP KEYS:",list(c.keys()))
for k,v in c.items():
    print("\n---",k,"---")
    print(json.dumps(v,indent=1)[:600])
