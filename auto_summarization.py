#!/usr/bin/env python3
# coding: utf-8
""" Module for timestamps on screenshots checking.
Copyleft 2021-22 by Roman M. Yudichev (industrialSAST@ya.ru)

Usage:
    auto_summarization.py -i <in_file> -o <out_file>
    auto_summarization.py -h | --help
    auto_summarization.py -v | --version

Options:
    -i            Входной файл со статьями в формате JSON
    -o            Выходной файл с рефератами статей
    -h --help      Show this screen.
    -v --version   Show version.


"""
import docopt
import json
from bs4 import BeautifulSoup
import re
import requests
import heapq
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from loguru import logger
import os

auto_summarization_version = '0.2'

# Задача: Автоматически построить рефераты текстовых документов.
# Ввод: Массив текстов в формате JSON. Примеры текстов можно скачать по этой ссылке.
# Вывод: Массив рефератов в формате JSON (порядок рефератов соответствует порядку текстов во входных данных).
#
# Максимальный размер каждого из рефератов -- 300 символов (включая пробельные). Если размер реферата превышает
# указанный порог, то будут оцениваться только первые 300 символов. Тривиальное решение (первые 300 символов документа)
# допускается, но не приветствуется.
#
# Вы можете кратко описать решение в первой строке загружаемого файла после символа #. Информация будет полезна авторам
# курса, чтобы составить представление об используемых методах и подходах.
#
# Оценка: ROUGE-2 -- близость набору вручную составленных рефератов на основе биграмм слов (значение от 0 до 1).


# Sample Input:
#
# ["Первый текст...", "Второй текст..."]

# Sample Output:
#
# ["Реферат первого текста...", "Реферат второго текста..."]

# pyteaser - ошибка при установке (даже из командной строки)

# Взято со страницы https://gist.github.com/Abhayparashar31/f937cedf16df024f824a3cb2772a484c

# Очистка текста: замена цифр на пробелы, приведение к нижнему регистру,
# все пробельные символы - на пробелы, запятые заменяем пробелами.

def clean(text):
    text = re.sub(r"\[[0-9]*\]", " ", text)
    text = text.lower()
    text = re.sub(r'\s+', " ", text)
    text = re.sub(r",", " ", text)
    return text


def get_key(val, sentences_score):
    for key, value in sentences_score.items():
        if val == value:
            return key


def create_refs(in_file, out_file):
    # url = str(input("Paste the url"\n"))
    # num = int(input("Enter the Number of Sentence you want in the summary"))
    num_in_chars = 300
    # num = int(num)
    num = 3  # TODO: Проверить длину 4х предложений

    summary = ""

    with open(in_file, encoding='utf8') as f:
        d = json.load(f)
        summary = d[0]

    summary = clean(summary)

    logger.info("Getting the data......\n")

    ##Tokenixing
    sent_tokens = sent_tokenize(summary)

    # summary = re.sub(r"[^a-zA-z]"," ",summary)
    word_tokens = word_tokenize(summary)
    ## Removing Stop words

    word_frequency = {}
    sw = set(stopwords.words("russian"))
    # stopwords = set(stopwords.words("english"))

    for word in word_tokens:
        if word not in sw:
            if word not in word_frequency.keys():
                word_frequency[word] = 1
            else:
                word_frequency[word] += 1
    maximum_frequency = max(word_frequency.values())
    logger.debug(maximum_frequency)
    for word in word_frequency.keys():
        word_frequency[word] = (word_frequency[word] / maximum_frequency)

    logger.debug({k: v for k, v in sorted(word_frequency.items(), key=lambda item: item[1], reverse=True)})

    sentences_score = {}
    for sentence in sent_tokens:
        for word in word_tokenize(sentence):
            if word in word_frequency.keys():
                if (len(sentence.split(" "))) < 30:
                    if sentence not in sentences_score.keys():
                        sentences_score[sentence] = word_frequency[word]
                    else:
                        sentences_score[sentence] += word_frequency[word]

    logger.debug(max(sentences_score.values()))

    key = get_key(max(sentences_score.values()), sentences_score)
    logger.debug(key + "\n")
    logger.debug(sentences_score)

    # TODO: Что делаем дальше:
    # 1. вывод сгенерированных рефератов в json (длиной не менее 300 символов, без усечения, без подбора по длине)

    # 2. Обработка в цикле (все тексты из файла json)
    # TODO: Запостить решение в Stepik. Какая будет оценка на курсе?

    # 3. Реализуем генерацию реферата определенной длины (в символах, а не в предложениях) (см. пункт 5)
    # - Находим все предложения в порядке убывания метрики;
    # - начинаем прибавлять предложение с максимальной метрикой к "результату"
    # - как только длина "результата" становится больше num_in_chars - останавливаемся.
    # - если длина предложения СРАЗУ больше num_in_chars - ошибка (надо подумать... Может быть "переписать" (TODO: как "переписать" предложение без потери смысла?))

    # 4. Вариант "честного" усечения до 300 символов:
    # - вычислить длину "хвоста" (остаток до 300 символов от полных предложений (вариант, если n+1 предложение будет уже
    # больше 300 сиволов));
    # - вычислить метрики невключенных в реферат предложений, усеченных до длины "хвоста";
    # - включить в реферат усеченное предложение с максимамальной метрикой.
    # ??? Оценка за такой вариант будет больше?

    # 5. Попробовать вариант с длиной > 300 символов.

    summary = heapq.nlargest(num, sentences_score, key=sentences_score.get)
    logger.info(" ".join(summary))
    summary = " ".join(summary)

    all_summaries = []
    all_summaries.append(summary)
    logger.debug(out_file)
    with open(out_file, 'w+', encoding='utf8') as out_f:
        json.dump(all_summaries, out_f, ensure_ascii=False, indent=4)


def check_arguments(args):
    if args["-i"] and args["<in_file>"] and args["-o"] and args["<out_file>"]:
        if not os.path.exists(args["<in_file>"]):
            logger.info(f"Please point argument 'in_file' correctly (file {args['<in_file>']} is not exist now.")
        else:
            create_refs(args["<in_file>"], args["<out_file>"])
    else:
        logger.debug("Please point all the arguments correctly.")
        logger.debug(args)


###############################################################################
if __name__ == "__main__":
    try:
        arguments = docopt.docopt(__doc__, version=f"auto_summarization version {auto_summarization_version}.")
        logger.debug(arguments)
        check_arguments(arguments)
    except docopt.DocoptExit as e:
        logger.debug(e)
