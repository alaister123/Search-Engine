import os
import json
from urllib.parse import urldefrag
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
import numpy as np
from nltk.stem import PorterStemmer


def remove_stem(token):
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in token]

# returns a list of relative paths for the saved pages
def return_path(path):
    directories = list()
    for data in os.walk(path):
        for website in data[2]:
            directories.append(os.path.join(data[0], website))
    return directories

# parse json file for further processing
def parse_json(file):
    return json.loads(file.read())

# parsing the html part
# return a bunch of tokens in lowered case
def parse_html(page):
    soup = BeautifulSoup(page,"html.parser")
    content = soup.get_text("|")

    information = content.split("|")
    
    tokenizer = RegexpTokenizer(r'[A-Za-z0-9]+')

    token = list()
    for text in information:
        for t in tokenizer.tokenize(text):
            token.append(t)


   
    
    temp = list()
    for word in token:
        temp.append(word.lower())

    return temp

# mergesort implementation
# used to merge 2 sorted document into 1
# only uses 2 lines in memory, very efficient
def merge(doc1,doc2,des):


    file1 = open(doc1)
    file2 = open(doc2)
    file3 = open(des,'a')




    raw1 = file1.readline()
    raw2 = file2.readline()

    while(len(raw1) != 0 and len(raw2) != 0):
        line1 = raw1.rstrip("\n").split(",")
        line2 = raw2.rstrip("\n").split(",")

        word1 = line1[0]
        word2 = line2[0]


        if(word1 < word2):
            file3.write(raw1)
            raw1 = file1.readline()

        elif(word1 > word2):
            file3.write(raw2)
            raw2 = file2.readline()

        elif(word1 == word2):
            temp1 = defaultdict(list)
            temp1[word1] = line1[1:-1]
        

            temp1[word2] += line2[1:-1]

            file3.write(word1)
            file3.write(",")
            for values in temp1[word1]:
                file3.write(str(values))
                file3.write(",")
            file3.write("\n")

            raw1 = file1.readline()
            raw2 = file2.readline()
    
    if(len(raw1) != 0):
        file3.write(raw1)
        raw1 = file1.readline()
        
    if(len(raw2) != 0):
        file3.write(raw2)
        raw2 = file2.readline()

    file1.close()
    file2.close()
    file3.close()

    print("Merge Complete")

# save the index sorted by the key value
# sorting is important for the merge step
def save_index(name,data):

    file = open(name,"w")
    for key in sorted(data.keys()):
        file.write(key)
        file.write(",")


        for values in data[key]:
            file.write(str(values))
            file.write(",")
        file.write("\n")
    
    file.close()


# parses the json files
def partial_parse(path,name,mapper):
    
    # create index default dict
    index = defaultdict(list)
    counter = 0
    
    # loop the assigned paths
    for p in path:

        # debug
        token_len = 0

        if(check_path(p) == True):


            file = open(p)
            
            
            # parse the raw file into json
            parsed = parse_json(file)


            # tokenize the page
            token = parse_html(parsed['content'])
            
            # debug
            token_len = len(token)


            if(len(token) < 10000 and len(token) > 40 and check_similarity(token) == False):
                # get token, unigram, bigram, trigram
                token = remove_stem(token)
                important = get_important_text(parsed['content'])
                
                bigram = get_bigrams(token)
                trigram = get_trigram(token)

                # unigram
                if(len(token) != 0):
                    for word in range(len(token)):
                        if(str(word) in important):
                            result = str(mapper[p]) + "->" + str(word) + "->" + str(len(token)) + "->" + str(1)
                        else:
                            result = str(mapper[p]) + "->" + str(word) + "->" + str(len(token)) + "->" + str(0)
                        index[token[word]].append(result)
                
                # bigram
                if(len(bigram) != 0):
                    for word in range(len(bigram)):
                        if(str(word) in important):
                            result = str(mapper[p]) + "->" + str(word) + "->" + str(len(bigram)) + "->" + str(1)
                        else:
                            result = str(mapper[p]) + "->" + str(word) + "->" + str(len(bigram)) + "->" + str(0)
                        index[bigram[word]].append(result)

                # trigram
                if(len(trigram) != 0):
                    for word in range(len(trigram)):
                        if(str(word) in important):
                            result = str(mapper[p]) + "->" + str(word) + "->" + str(len(trigram)) + "->" + str(1)
                        else:
                            result = str(mapper[p]) + "->" + str(word) + "->" + str(len(trigram)) + "->" + str(0)
                        index[trigram[word]].append(result)

            

            file.close()


        # tracker
        counter += 1
        print(str(counter) + " " + str(token_len))

        
    
    
    # save to file
    save_index(name,index)

# index the files 
def parse_file(path):
    
    # mapper from path -> doc_id
    file = open("map.json","r")
    mapper = json.loads(file.read())
    file.close()

    path1 = path[0:20000]
    path2 = path[20000:40000]
    path3 = path[40000:-1]
    partial_parse(path1,"temp1.txt",mapper)
    partial_parse(path2,"temp2.txt",mapper)
    partial_parse(path3,"temp3.txt",mapper)


# check if path is json file
def check_path(path):
    if ".json" in path:
        return True
    return False

# bigram (extra credit)
def get_bigrams(token):
    temp = list()
    
    if(len(token) <= 1):
        return list()
    
    for i in range(len(token) - 1):
        token1 = token[i]
        token2 = token[i+1]
        final = token1 + " " + token2
        temp.append(final)
    
    return temp

# trigram
def get_trigram(token):
    temp = list()
    
    if(len(token) <= 2):
        return list()

    for i in range(len(token) - 2):
        token1 = token[i]
        token2 = token[i+1]
        token3 = token[i+2]
        final = token1 + " " + token2 + " " + token3
        temp.append(final)

    return temp

# check file similarity (bonus points)
# fingerprint method
def check_similarity(tokens):
    
    # get fingerprint for current doc
    fingerprintA = list()
    for word in tokens:
        h_value = hash(word)
        if (h_value % 4 == 0):
            fingerprintA.append(h_value)

    f1 = set(fingerprintA)
    

    try:
        file = open("similar.txt",'r',encoding='utf-8')
        line = file.readline()
        while(len(line) != 0):
            fingerprintB = list()
            data = line.rstrip("\n").split(" ")
            for number in data:
                if(len(number) != 0):
                    fingerprintB.append(int(number))

            f2 = set(fingerprintB)

            similarity = len(f1.intersection(f2))/len(f1.union(f2))
            if(similarity > 0.9):
                file.close()
                return True

            line = file.readline()
    except FileNotFoundError:
        pass
    
    save_hashed(f1)

    return False

# helper function for checking similarlity
def save_hashed(values):

    counter = 0
    if(len(values) != 0):
        file = open("similar.txt",'a',encoding='utf-8')
        for v in values:
            file.write(str(v) + ' ')
            counter += 1
            if(counter > 200):
                break
        file.write("\n")
        file.close()

# get important text like title, h1,h2,h3,strong etc
def get_important_text(page):
    
    important = str()

    soup = BeautifulSoup(page,"html.parser")
    if(soup.title != None):
        if(soup.title.string != None):
            important += soup.title.string + " "

    for headers in soup.find_all(["h1","h2","h3",'b','strong']):
        if(headers != None):
            important += headers.text.strip() + " "
    
    important = important.lower()

    tokenizer = RegexpTokenizer(r'[A-Za-z0-9]+')
    tokens = tokenizer.tokenize(important)
    
    tokens = remove_stem(tokens)

    return " ".join(tokens)

# main program
if __name__ == "__main__":
    paths = return_path("DEV")
    parse_file(paths)
    merge("temp1.txt","temp2.txt","temp4.txt")
    merge("temp3.txt","temp4.txt","temp5.txt")


