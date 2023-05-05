import io

with io.open('static/object_data.json') as f:
    data = f.read().rstrip()
with io.open('static/story_template.json') as f:
    template = f.read().rstrip()

out = f"""const staticData = true;
var allData = {data};
var allOptions = Object.keys(allData);
var storyTemplate = {template};
"""
with io.open('static/data.js', 'wt') as f:
    f.write(out)

print('Done')
