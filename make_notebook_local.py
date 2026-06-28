import json

nb_path = "notebooks/04_yoloseg_tracking_pipeline.ipynb"
with open(nb_path, "r") as f:
    nb = json.load(f)

# Cell 1 (imports and models)
source_1 = nb["cells"][1]["source"]
new_source_1 = []
for line in source_1:
    if "google.colab" not in line:
        new_source_1.append(line)
nb["cells"][1]["source"] = new_source_1

# Cell 2 (video paths and processing)
source_2 = nb["cells"][2]["source"]
new_source_2 = []
for line in source_2:
    if "VIDEO_PATH = " in line:
        new_source_2.append("VIDEO_PATH = \"../data/raw/videos/futebol_teste.mp4\"\n")
    elif "OUTPUT_PATH = " in line:
        new_source_2.append("OUTPUT_PATH = \"../data/raw/videos/futebol_rastreado_yoloseg.mp4\"\n")
    elif "json_path = " in line:
        new_source_2.append("json_path = \"../data/raw/videos/trajetorias.json\"\n")
    elif "files.download" not in line:
        new_source_2.append(line)

nb["cells"][2]["source"] = new_source_2

with open(nb_path, "w") as f:
    json.dump(nb, f, indent=1)
