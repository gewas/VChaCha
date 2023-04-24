import jieba
from os import path
import os
from wordcloud import WordCloud


def jieba_processing_txt(text, user_dict=[]):
    for word in user_dict:
        jieba.add_word(word)

    mywordlist = []
    seg_list = jieba.cut(text, cut_all=False)
    liststr = "/ ".join(seg_list)

    for myword in liststr.split('/'):
        if len(myword.strip()) > 1:
            mywordlist.append(myword)
    return ' '.join(mywordlist)


def word_cloud(text, savePath, user_dict=[]):
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    font_path = d + '/SourceHanSerifK-Light.otf'
    wc = WordCloud(font_path=font_path, background_color="white", max_words=8000,
                   max_font_size=100, random_state=42, width=1200, height=900, margin=2,)
    wc.generate(jieba_processing_txt(text, user_dict))
    wc.to_file(savePath)

