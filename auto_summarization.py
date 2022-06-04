# pyteaser - ошибка при установке (даже из командной строки)

# Взято со страницы https://gist.github.com/Abhayparashar31/f937cedf16df024f824a3cb2772a484c
import json

from bs4 import BeautifulSoup
import re
import requests
import heapq
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords

# url = str(input("Paste the url"\n"))
# num = int(input("Enter the Number of Sentence you want in the summary"))
num_in_chars=300
# num = int(num)
num = 3 # TODO: Проверить длину 4х предложений

# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
#url = str(input("Paste the url......."))
# res = requests.get(url,headers=headers)
summary = ""
# soup = BeautifulSoup(res.text,'html.parser')
# content = soup.findAll("p")
# for text in content:
#     summary +=text.text

# Пример: example_texts.json
sample = 'example_texts.json'

with open(sample, encoding='utf8' ) as f:
    d = json.load(f)
    summary =d[0]


def clean(text):
    text = re.sub(r"\[[0-9]*\]"," ",text)
    text = text.lower()
    text = re.sub(r'\s+'," ",text)
    text = re.sub(r","," ",text)
    return text
summary = clean(summary)

print("Getting the data......\n")


##Tokenixing
sent_tokens = sent_tokenize(summary)

# summary = re.sub(r"[^a-zA-z]"," ",summary)
word_tokens = word_tokenize(summary)
## Removing Stop words

word_frequency = {}
stopwords = set(stopwords.words("russian"))
# stopwords = set(stopwords.words("english"))


for word in word_tokens:
    if word not in stopwords:
        if word not in word_frequency.keys():
            word_frequency[word]=1
        else:
            word_frequency[word] +=1
maximum_frequency = max(word_frequency.values())
print(maximum_frequency)
for word in word_frequency.keys():
    word_frequency[word] = (word_frequency[word]/maximum_frequency)


print({k: v for k, v in sorted(word_frequency.items(), key=lambda item: item[1], reverse=True)})

sentences_score = {}
for sentence in sent_tokens:
    for word in word_tokenize(sentence):
        if word in word_frequency.keys():
            if (len(sentence.split(" "))) <30:
                if sentence not in sentences_score.keys():
                    sentences_score[sentence] = word_frequency[word]
                else:
                    sentences_score[sentence] += word_frequency[word]

print(max(sentences_score.values()))
def get_key(val):
    for key, value in sentences_score.items():
        if val == value:
            return key
key = get_key(max(sentences_score.values()))
print(key+"\n")
print(sentences_score)

# TODO: Что делаем дальше:
# 1. Реализуем генерацию реферата определенной длины (в символах, а не в предложениях) (см. пункт 5)
# - Находим все предложения в порядке убывания метрики;
# - начинаем прибавлять предложение с максимальной метрикой к "результату"
# - как только длина "результата" становится больше num_in_chars - останавливаемся.
# - если длина предложения СРАЗУ больше num_in_chars - ошибка (надо подумать... Может быть "переписать" (TODO: как "переписать" предложение без потери смысла?))
# 2. Обработка в цикле (все тексты из файла json)
# 3. вывод сгенерированных рефератов в json
# ??? Какая будет оценка на курсе?
# 4. Вариант усечения до 300 символов:
# - вычислить длину "хвоста";
# - вычислить метрики невключенных в реферат предложений, усеченных до длины "хвоста";
# - включить в реферат усеченное предложение с максимамальной метрикой.
# ??? Оценка за такой вариант будет больше?

# 5. Попробовать вариант с длиной > 300 символов.

summary = heapq.nlargest(num,sentences_score,key=sentences_score.get)
print(" ".join(summary))
summary = " ".join(summary)