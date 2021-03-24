import os
import json
from collections import defaultdict
from urllib.parse import urldefrag,urlparse,urljoin
from bs4 import BeautifulSoup
import copy


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

    temp = list()
    
    for link in soup.find_all('a'):
        temp.append(link.get('href'))
        
    
    defragged = list()

    for link in temp:
        url = urldefrag(link)[0]
        if(len(url) > 1):
            defragged.append(url)

    return defragged


def check_redirection(current_node,forward_node):
    parse1 = urlparse(current_node)
    parse2 = urlparse(forward_node)

    p1 = parse1.path.split("/")
    p2 = parse2.path.split("/")

    if(len(p1) < 2 or len(p2) < 2):
        return False
    
    if(p1[1]==p2[1]):
        return True
    
    return False


def to_edges(current_node,forward_node,mapper):

    temp = list()

    for nodes in forward_node:
        try:
            if(check_redirection(current_node,nodes) == False):
                forward = mapper[nodes]
                edge = (int(mapper[current_node]),int(forward))
                temp.append(edge)
        except KeyError:
            pass
    return temp

# correct links
def correct_links(links,url):

    corrected = list()
    for L in links:
        if(type(L) == str):
            if(len(L) > 1):
                if(is_absolute_path(L)):
                    corrected.append(L)
                else:
                    corrected.append(urljoin(url,L))

    return corrected

# if url is absolute or not
def is_absolute_path(url):
    parsed = urlparse(url)
    if(len(parsed.netloc) == 0 or len(parsed.scheme) == 0):
        return False
    return True

def check_link_length(links):
    temp = list()
    for l in links:
        if(len(l) < 70):
            temp.append(l)

    return temp


def parse_file():
    
    counter = 0

    file = open("inverse_map.json")
    mapper = json.loads(file.read())
    file.close()

    mapper = {v:k for k,v in mapper.items()}

    file = open("map.json")
    path = json.loads(file.read())
    file.close()

    path = {v:k for k,v in path.items()}
    val = [k[1] for k in mapper.items()]


    edges = list()

    for p in val:
        file = open(path[int(p)])

        # parse the raw file into json
        parsed = parse_json(file)
        links = parse_html(parsed['content'])
        
        
        current_url = urldefrag(parsed['url'])[0]
        links = correct_links(links,current_url)
        links = check_link_length(links)
        #print(links)


        edges += to_edges(current_url,links,mapper)
        print(counter)
        counter += 1
    return edges

def store_edges(edges):
    with open("edges.txt", "w") as outfile:  
        json.dump(edges, outfile) 


def load_edges(file_name):
    file = open(file_name)
    edges = json.loads(file.read())
    file.close()

    return edges

def edges_to_graph(edges):

    graph = defaultdict(dict)

    for E in edges:
        current, outgoing = E
        
        # no self redirection
        if(current != outgoing):
            graph[current][outgoing] = dict()

    return graph

# Citation: https://networkx.org/documentation/networkx-1.10/_modules/networkx/algorithms/link_analysis/pagerank_alg.html#pagerank
# I understood their code and built my own pagerank from scratch
def page_ranker(G):
    

    alpha = 0.85
    iteration = 10

    # create weighed graph
    W = stochastic_graph(G)

    # number of nodes
    N = len(G)


    x = dict.fromkeys(W,1.0/N)

    new = dict()

    # edge case
    # if node doesnt have forward edge
    for n in x:
        for nbr in W[n]:
            new[nbr] = 1.0/N


    for k,v in new.items():
        x[k] = v

    N = len(x)
    for key in x.keys():
        x[key] =  1.0/N


    # important pages manually set to a number higher than ordinary pages
    x[54613] = 0.1
    x[45156] = 0.1
    x[21503] = 0.1
    x[55378] = 0.1

    p = copy.deepcopy(x)

    # actual matrix mutiplcation part
    # since the matrix is mostly sparse
    # we just use dictionaries to mutiple non zero entries
    # the iteration is used for calculating eigenvector for each node
    for _ in range(iteration):
        xlast = x
        x = dict.fromkeys(xlast.keys(), 0)
        for n in x:
            for nbr in W[n]:
                # multiplication of matrix and alpha, the damping factor
                # X.T = alpha * xlast.T * W
                x[nbr] += alpha * xlast[n] * W[n][nbr]['weight']
                    
            x[n] += (1.0 - alpha) * p[n]

    return x

def stochastic_graph(G):
    graph = copy.deepcopy(G)

    for k in graph.keys():
        len_outgoing = len(graph[k])
        weight = 1/len_outgoing

        for out in graph[k].keys():
            graph[k][out]['weight'] = weight

    return graph

if __name__ == "__main__":
    
    # part 1, computer and store edges
    # I store edges cuz have to iterate 56000 files each time
    # too long
    #edges = parse_file()
    #store_edges(edges)

    #part 2, page rank algorithm
    edges = load_edges("edges.txt")
    G = edges_to_graph(edges)
    

    pr = page_ranker(G)

    file = open("inverse_map.json")
    mapper = json.loads(file.read())
    file.close()

    pagerank = dict()

    total_len = len(pr)


    pos = 0
    for i in sorted(pr.items(), key = lambda x: x[1]):
        pagerank[i[0]] = 1 * ((pos-0)/total_len-0)
        pos += 1
    
    with open("rank.txt", "w") as outfile:  
        json.dump(pagerank, outfile) 
