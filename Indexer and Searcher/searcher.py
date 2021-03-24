from collections import defaultdict
import json
import sys
import time
from nltk.stem import PorterStemmer 
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import numpy as np
import math


def initialization():
    file = open("map_index_position.txt")
    mapper = json.loads(file.read())
    file.close()

    file = open("cached.txt")
    cached = json.loads(file.read())
    file.close()

    file = open("inverse_map.json")
    inverse_map = json.loads(file.read())
    file.close()

    file = open("final_index.txt",'r')

    return (mapper,inverse_map,file,cached)

def search(user_ipt,mapper,inverse_map,file,stemmer,tokenizer,stop_words,cached):
    tic = time.perf_counter()
    
    try:
        result = cached[user_ipt.lower()]
        toc = time.perf_counter()
        print(result)
        time_used = (toc-tic)*1000
        print(f"Took {time_used}ms")
        return
    except KeyError:
        pass

    # tokenize and remove stop words
    phrase_original = tokenizer.tokenize(user_ipt)
    phrase_stemmed = [stemmer.stem(p) for p in phrase_original]
    phrase = [w for w in phrase_stemmed if not w in stop_words]
    


    # exact match
    try:
        if(len(phrase) <= 3):
            phrase_copy = " ".join(phrase)
            file.seek(mapper[phrase_copy])
            data = json.loads(file.readline())
            result = sorted(data.items(), key=lambda item: item[1]["score"], reverse=True)

            toc = time.perf_counter()

            for k in result[0:7]:
                print(inverse_map[k[0]])
            
            time_used = (toc-tic)*1000
            print(f"Took {time_used}ms")
            return
    except KeyError:
        pass


   
    if(len(phrase) != 0):
        posting, word = get_index(phrase,mapper)
    else:
        posting, word = get_index(phrase_stemmed,mapper)

    # if really cannot find anything
    if(len(posting) == 0):
        print("No Results Found")
        toc = time.perf_counter()
        time_used = (toc-tic)*1000
        print(f"Took {time_used}ms")
        return

    # retrieve documents and find intersection
    doc_ids,word = retrieve_union(posting,word)

    # compute necessary stuff for cosine similarity
    query_norm = compute_query_tfidf(word,doc_ids)
    doc_norm = compute_document_tfidf(word,doc_ids,posting)
    
    # compute cosine similarity
    csim = cosine_similarity(query_norm,doc_norm)
    
    data = prepare_for_ranking(doc_ids,csim,posting)

    result = sorted(data.items(), key=lambda item: item[1], reverse=True)
    for k in result[0:7]:
        print(inverse_map[str(k[0])])

    toc = time.perf_counter()
    time_used = (toc-tic)*1000
    print(f"Took {time_used}ms")


def prepare_for_ranking(doc_ids,csim,postings):
    temp = dict()
    for i in range(len(doc_ids)):
        authority = 0
        for p in postings:
            try:
                authority += p[doc_ids[i]]["score"]
            except KeyError:
                authority += 0
        temp[doc_ids[i]] = 0.5 * csim[i] + authority
    
    return temp


def compute_query_tfidf(word,doc_ids):
    temp = list()
    for i in range(len(word)):
       temp.append(math.log(56000/len(doc_ids[i]),10))
    
    temp = np.array(temp)

    normalized = np.linalg.norm(temp)

    return temp/normalized

def compute_document_tfidf(word,doc_ids,postings):
    temp = list()
    for ids in doc_ids:
        temp2 = list()
        for p in postings:
            try:
                temp2.append(p[ids]["term_freq"])
            except KeyError:
                temp2.append(0)
        temp2 = np.array(temp2)
        normalized = np.linalg.norm(temp2)
        temp.append(temp2/normalized)
    
    return np.array(temp)
def cosine_similarity(q_norm,d_norm):

    # special case scenario
    if(q_norm.shape != d_norm[0].shape):
        for _ in range(d_norm[0].shape[0]-q_norm.shape[0]):
            q_norm = np.append(q_norm,[0])

    temp = list()
    for doc in d_norm:
        temp.append(np.dot(q_norm,doc))
    return np.array(temp)

def get_index(phrase,mapper):
    temp = list()
    ordered = list()
    for word in set(phrase):
        try:

            file.seek(mapper[word])
            data = json.loads(file.readline())
            temp.append(data)
            ordered.append(word)
        except KeyError:
            pass
        
    return (temp,ordered)


def retrieve_union(posting,word):
    
    contain = set()
    contain_word = list()


    pos = sorted(posting, key = lambda x: len(x))
    
    contain = set(pos[0].keys())

    for p in range(len(pos)):
        temp = contain.intersection(pos[p].keys())
        if(len(temp) > 7):
            contain = temp
            contain_word.append(word[p])
        else:
            break 
    
    return (list(contain),contain_word)

if __name__ == "__main__":
    print("Initializing Search Engine...")
    mapper,inverse_map,file,cached = initialization()
    tokenizer = RegexpTokenizer(r'[A-Za-z0-9]+')
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))  
    print("Initialization Complete")

    user_ipt = input("Search: ")

    while(user_ipt != "exit"):
        if(user_ipt != ""):
            search(user_ipt,mapper,inverse_map,file,stemmer,tokenizer,stop_words,cached)
        user_ipt = input("Search: ")