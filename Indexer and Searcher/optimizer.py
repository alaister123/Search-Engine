from collections import defaultdict
import json
import sys
import time
import math

# parses the lines from saved data structure
def parse_line(line):
    data = line.rstrip("\n").split(",")
    word = data[0]
    return (word,data[1:-1])

# extract information such as tf-idf, position, etc
# save in a dictionary with 2 score, position

# [position, lenght of document, important_word]
def extract_info(data):
    

    # fetching data
    temp = defaultdict(list)
    for info in data:
        sp = info.split("->")
        temp[int(sp[0])].append(sp[1:])

    # creating summary
    information = defaultdict(dict)

    for key in temp.keys():
        temp_posting = dict()
        temp_posting["term_freq"] = int()
        temp_posting["doc_freq"] = int()
        temp_posting["is_important"] = int()
        temp_posting["positions"] = list()

        data = temp[key]

        temp_posting["term_freq"] = len(data)
        temp_posting["doc_freq"] = len(temp.keys())
        temp_posting["is_important"] = int(data[0][2])

        idx = list()
        for index in data:    
            idx.append(int(index[0]))
        
        temp_posting["positions"] = idx

        information[key] = temp_posting
    
    
    return information

# does a scoring for each of the posting
def score(information,rank):
    final = defaultdict(dict)


    for key in information.keys():
        temp_posting = dict()
        temp_posting["score"] = int()
        temp_posting["positions"] = list()

        # computing tf-idf
        tf = 1+math.log(information[key]["term_freq"],10)
        idf = math.log(56000/information[key]["doc_freq"],10)



        # score
        try:
            temp_posting["score"] = round(tf * idf,3) + information[key]["is_important"] + round(rank[str(key)],3)
        except KeyError:
            temp_posting["score"] = round(tf * idf,3) + information[key]["is_important"]
        
        temp_posting["doc_freq"] = idf
        temp_posting["term_freq"] = tf
        temp_posting["positions"] = information[key]["positions"]

        final[key] = temp_posting
    return final

def save_to_file(final):

    
    data = json.dumps(final) + "\n"

    file = open("final_index.txt","a")
    file.write(data)
    file.close()

    return len(data.encode("utf-8"))

def save_mapper(mapper):

    file = open("map_index_position.txt",'w')
    file.write(json.dumps(mapper))
    file.close()

if __name__ == "__main__":
    
    file = open("rank.txt")
    rank = json.loads(file.read())
    file.close()

    file = open("temp5.txt")
    

    mapper = defaultdict(int)
    line = file.readline()

    position = 0


    counter = 0
    while(len(line) != 0):
    
        word, data = parse_line(line)
        temp_dict = extract_info(data)
        
        final = score(temp_dict,rank)
        mapper[word] = position

        position += save_to_file(final) + 1
        line = file.readline()

        counter += 1
        print(counter)

    save_mapper(mapper)