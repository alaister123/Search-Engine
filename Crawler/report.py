from urllib.parse import urlparse
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer


# # Question 2
# file = open("page_len.txt")

# line = file.readline()
# longest = 0
# page = ""

# while(len(line) != 0):

#     data = int(line.rstrip("\n").split(" -> ")[1])
#     p = line.rstrip("\n").split(" -> ")[0]
#     if (data > longest and "evoke" not in p):
#         longest = data
#         page = p
#     line = file.readline()
# print(longest)
# print(page)


# # Question 3
# file = open("text.txt", errors="replace")
# line = file.readline()

# common = defaultdict(int)

# stopwords = stopwords.words('english')

# count = 0
# while(len(line) != 0):
#     data = line.rstrip("\n")
#     tokenizer = RegexpTokenizer(r'\w+')
#     token = tokenizer.tokenize(data)
#     for word in token:
#         if(word.lower() not in stopwords and len(word) > 2):
#             common[word.lower()] += 1
#     count += 1
#     print(count)
#     line = file.readline()

# count = 0
# for top in sorted(common,key=common.get,reverse=True):
#     print(top)
#     count += 1
#     if(count >= 50):
#         break

# Question 4
# file = open("page_len.txt",errors='ignore')

# line = file.readline()

# unique = defaultdict(int)

# while(len(line) != 0):
#     parsed = urlparse(line.rstrip("\n").split(" -> ")[0])

#     domain = parsed.netloc
#     if(domain != "ics.uci.edu" and "ics.uci.edu" in domain and "www.informatics.uci.edu" not in domain):
#         unique[domain]+=1
#     line = file.readline()


# for s in sorted(unique.items(),key=lambda x: x[0]):
#     print(str(s[0]) + " " + str(s[1]))
