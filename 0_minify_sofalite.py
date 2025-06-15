"""
cd /home/g/projects && uv run --with jsmin "/home/g/projects/sofastats/0_minify_sofalite.py"
"""

import jsmin

with open("/sofastats/output/js/sofastats.js.uncompressed.js", "r") as f:
    oldjs = f.read()
newjs = jsmin.jsmin(oldjs)
with open("/sofastats/output/js/sofalitedojo_minified.js", "w") as f:
    f.write(newjs)
print("Finished")
