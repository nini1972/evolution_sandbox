"""HTML render for the bridge. Imports the parts above and writes index.html."""
import sys
sys.path.insert(0, ".")

# Re-execute the segments in order so all globals are defined
exec(open("_seg_inventory.py").read())
exec(open("_seg_roster.py").read())
exec(open("_seg_picks.py").read())

H = []
