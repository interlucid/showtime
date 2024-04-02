import json

import config

print(json.dumps(config.set))

with open("static/song_list.json", "w") as f:
    json.dump(config.set, f)
