import io

with io.open('static/object_data.json') as f:
    data = f.read().rstrip()

out = f"""const staticData = true;
var allData = {data};
var allOptions = Object.keys(allData);
"""
with io.open('static/data.js', 'wt') as f:
    f.write(out)

print('Done')
