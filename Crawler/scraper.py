import re
from urllib.parse import urlparse, urljoin, urlunparse, parse_qsl
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer

def scraper(url, resp):

    # Save URL
    save_url(url)

    # response code is > than 400 means error = no crawl
    if(resp.status >= 400):
        return list()

    # response code is > than 400 means error = no crawl
    if(resp.raw_response.status_code >= 400):
        return list()
    
    # debug purpose
    #if(resp.status >= 600):
    #    print("600ERROR: "+ resp.error + " " + str(url))
    #    return list()
    

    # if link gets redirected to page outside of domain, don't crawl
    if(is_valid(resp.raw_response.url) == False):
        return list()


    
    

            
    if(valid_content(resp.raw_response) == False):
        return list()
    


    
    # Tokenize page and save necessary data locally
    token = tokenize_page(resp.raw_response.content)
    
    # Page similarity detection
    if(is_similar(token) == False):
        # Save words to file
        save_token_to_file(token)



    # Save word length to file
    save_pageword_data(token,resp.raw_response.url)

    # determine if page has low info
    if(low_info(token) == True):
        return list()


    # debug
    # print("----------------------------Extracting URLS from " + url)

    links = extract_next_links(resp.raw_response.url, resp)

    # debug
    #for i in [link for link in links if is_valid(link)]:
    #    print(i)



    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    
    
    # find all new links                                        
    links = find_all_links(resp.raw_response.content)
    
    # correct links                                             
    links  = correct_links(links,url)

    # filter fragments
    links =  filter_fragments(links)

    # remove long query links
    links = remove_long_query(links)

    # filter links already visited
    links = filter_visited(links)
    
    # filter php & index & index.php
    links = remove_index(links)
    
    # filter duplicates
    links = filter_duplicates(links)



    return links

# filter out exact and near webpages (extra credit)
def is_similar(tokens):
    


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

def save_hashed(values):

    if(len(values) != 0):
        file = open("similar.txt",'a',encoding='utf-8')
        for v in values:
            file.write(str(v) + ' ')
        file.write("\n")
        file.close()

# filter out links that have already been visited
def filter_visited(links):
    incoming = set(links)
    visited = set()
    file = open("visited.txt",'r',encoding='utf-8')

    line = file.readline()
    while(len(line) != 0):

        url = line.rstrip('\n')
        visited.add(url)
        line = file.readline()

    temp = list(incoming - visited)
    file.close()

    return temp



# check content type and content length
def valid_content(response):
    
    have_type = True

    try: 
        content_type = response.headers['Content-Type']
        # check if it is a html file. Some directories does not specify .pdf etc files 
        # for example http://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018 is a pdf file but url have no indication
        # http://www.ics.uci.edu/~rickl/rickl-giw is picture file but url have no indicate
        if ("html" not in content_type.lower()):
            return False
    except KeyError:
        have_type = False

    try:
        content_length = response.headers["Content-Length"]
        if(int(content_length) > 50000):
            return False
    except KeyError:
        pass
    
    return have_type


# remove /index and /index.php and .php these are all duplicate pages
# only need 1
def remove_index(links):
    temp = list()
    for url in links:
        text = re.sub("index.php$|index$|.php$|Index$|index.html$","",url)
        temp.append(text)
    
    return temp

# remove long query links
# as well as remove keywords in the query that causes trouble
def remove_long_query(links):
    temp = list()
    for url in links:
        parsed = urlparse(url)
        if (len(parsed.query) <= 50):
            
            arguments = " ".join([i[0] for i in parse_qsl(parsed.query, keep_blank_values=True)])
            
            if(re.search(r"\bshare\b|\bdo\b|\brev\b|\breplytocom\b|\bversion\b|\baction\b|\bformat\b|event_types\[\]",arguments) == None):
                temp.append(url)
    return temp

# find all new links
def find_all_links(page):
    soup = BeautifulSoup(page,"html.parser")
    return [link.get('href') for link in soup.find_all('a')]

# filter duplicates
def filter_duplicates(links):
    temp = set(links)
    return list(temp)

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


# filter stuff outside domain
def filter_domain(url):



    pattern = re.compile(r"^(?!.*(\.ics\.uci\.edu|\.cs\.uci\.edu|\.informatics\.uci\.edu|stat\.uci\.edu)).*$")
    if(pattern.match(url) == None):
        return True
    return False

# save URL to text file
# file is used to for eliminating sites already visited
def save_url(url):

    url = url.rstrip('/')
    file = open("visited.txt",'a',encoding='utf-8')
    file.write(url + '\n')
    file.close()

# eliminate fragments in url
def filter_fragments(links):
    temp = list()
    for url in links:
        parsed = urlparse(url)
        
        joined = (parsed.scheme,parsed.netloc,parsed.path,parsed.params,parsed.query,"")

        temp.append(urlunparse(joined))
    return temp

# filter out calendar
def is_calender(input_str):
    return (re.match(r"^.*((19|20)\d\d[- \.\/](0[1-9]|1[012]|[1-9]))(([- \.\/](0[1-9]|[12][0-9]|3[01]))?)((\/(.*))?)$",input_str) != None)

def low_info(token):
    if (len(token) < 100):
        return True
    else:
        return False 


def is_valid(url):
    try:
        parsed = urlparse(url)
        
    
        # filter stuff not within domain
        # if domain not ics,cs,stats, or today.uci.edu                           
        if(filter_domain(parsed.netloc) == False and "today.uci.edu" not in parsed.netloc):
            return False


        

        if("today.uci.edu" in parsed.netloc):
            if("department/information_computer_sciences" not in parsed.path):
                return False

        if(is_calender(url) == True):
            return False


        # need to be hardcoded for some reason, regex doesnt parse it
        if(".svn" in parsed.path.lower()):
            return False


        
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|py|war|apk|ds_store|ova|bib|java|cpp|svg|m|class|img|test|lisp|svn-base|svn|h|cc|bam|odp|dsp|ppsx|z|sql|bw|c)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


######
######
# tokenize a html page
def tokenize_page(page):
    soup = BeautifulSoup(page,"html.parser")
    text = soup.get_text('|')

    # As did in lecture
    # Find all visible text, and split them according to their tags
    # text larger than len 10 per tag means quality content
    # quality content gets joined then parsed into uni-gram
    # uni-gram is return
    content = list()
    temp = text.split("|")
    for visible in temp:
        if(len(visible) > 10):
            content.append(visible)

    text = " ".join(content)
    tokenizer = RegexpTokenizer(r'\w+')
    token = tokenizer.tokenize(text)
    return token

# save number of words in this page
def save_pageword_data(token,url):
    length = len(token)
    file = open("page_len.txt",'a',encoding='utf-8')
    file.write(str(url) + ' -> ' + str(length) + "\n")
    file.close()

# save all the tokens to a file
def save_token_to_file(token):
    
    file = open("text.txt",'a',encoding='utf-8')
    for t in token:
        file.write(t + " ")
    file.write('\n')
    file.close()