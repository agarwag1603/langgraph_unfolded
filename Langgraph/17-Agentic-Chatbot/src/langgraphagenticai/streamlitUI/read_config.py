import json
#import src.langgraphagenticai.streamlitUI
import os

# Get the absolute path of the current file
current_file = os.path.abspath(__file__)
current_dir=os.path.dirname(current_file)
folder_path = os.path.join(current_dir, "config.json")
print(folder_path)

with open(folder_path, "r") as f:
    data = json.load(f)

print_title=data["PAGE TITLE"]
company=data["Company"]
models=data["Models"]
