

# ------------------------------ main entry ------------------------------
def img_to_b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')
