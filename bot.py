from itertools import combinations
from nltk.tokenize import sent_tokenize, RegexpTokenizer
from nltk.stem.snowball import RussianStemmer
import networkx as nx
import telebot

bot = telebot.TeleBot('7870136037:AAE8W0Dl2DkLQUEEBIAvgNlkprFH0WqhqDM')


def similarity(s1, s2):
    if not len(s1) or not len(s2):
        return 0.0
    return len(s1.intersection(s2)) / (1.0 * (len(s1) + len(s2)))


def textrank(text):
    sentences = sent_tokenize(text)
    tokenizer = RegexpTokenizer(r'\w+')
    lmtzr = RussianStemmer()
    words = [set(lmtzr.stem(word) for word in tokenizer.tokenize(sentence.lower()))
             for sentence in sentences]
    pairs = combinations(range(len(sentences)), 2)
    scores = [(i, j, similarity(words[i], words[j])) for i, j in pairs]
    scores = filter(lambda x: x[2], scores)
    g = nx.Graph()
    g.add_weighted_edges_from(scores)
    pr = nx.pagerank(g)
    return sorted(((i, pr[i], s) for i, s in enumerate(sentences) if i in pr), key=lambda x: pr[x[0]], reverse=True)


def sumextract(text, n=5):
    tr = textrank(text)
    top_n = sorted(tr[:n])
    return ' '.join(x[2] for x in top_n)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Введите текст")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip()
    if not text:
        bot.reply_to(message, "Отправьте непустой текст.")
        return
    try:
        summarized_text = sumextract(text, 3)
        bot.reply_to(message, summarized_text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")


bot.polling(non_stop=True)