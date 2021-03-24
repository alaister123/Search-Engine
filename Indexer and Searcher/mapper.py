
import os
import json
from collections import defaultdict
from urllib.parse import urldefrag

# returns a list of relative paths for the saved pages
def return_path(path):
    directories = list()
    for data in os.walk(path):
        for website in data[2]:
            directories.append(os.path.join(data[0], website))
    return directories

def mapping(path):
    counter = 0
    doc_id = defaultdict(int)
    inverse_doc_id = defaultdict(str)


    for p in path:
        doc_id[p] = counter

        file = open(p)
        data = json.loads(file.read())
        file.close()

        inverse_doc_id[counter] = urldefrag(data['url'])[0]
        counter += 1
        print(counter)

    save("map.json",doc_id)
    save("inverse_map.json",inverse_doc_id)

def save(name,data):
    with open(name, "w") as outfile:  
        json.dump(data, outfile) 


if __name__ == "__main__":
    paths = return_path("DEV")
    mapping(paths)