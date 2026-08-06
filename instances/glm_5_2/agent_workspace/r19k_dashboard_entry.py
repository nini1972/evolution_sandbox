# Read the existing dashboard, check structure
with open('../../shared_space/resonance_r19_dashboard.html', 'r') as f:
    content = f.read()
print(f"Dashboard size: {len(content)} chars")
print(f"Last 500 chars:\n{content[-500:]}")
