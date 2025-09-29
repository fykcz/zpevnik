#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://forums.scribus.net/index.php/topic,3279.msg15474.html#msg15474
# import pip

# pip.main(["install", "pandas"])

import locale
import os

import scribus  # pylint: disable=import-error

# import pandas as pd

# items = getPageItems()
# atts = getObjectAttributes('Text165')
# print(atts)

p_count = pageCount()
page_offset = 16
song_names = []
authors = []
page_nums = []
songs = []
toc_text_page = 0
abc_text_page = 0
author_text_page = 0

TOC_TEXT_OBJECT = "TableOfContent"
ABC_TEXT_OBJECT = "ABCIndex"
AUTHOR_TEXT_OBJECT = "AuthorIndex"


class Song:
    def __init__(self, name, author, author_sort, pgnum):
        self.name = name
        self.author = author
        self.author_sort = author_sort
        self.pgnum = pgnum

scribus.setRedraw(False)
scribus.progressTotal(p_count + 1)
scribus.progressSet(0)
for i in range(1, p_count + 1):
    gotoPage(i)
    items = getPageItems()
    for item in items:
        item_name = item[0]
        if item_name == TOC_TEXT_OBJECT:
            toc_text_page = i
        if item_name == ABC_TEXT_OBJECT:
            abc_text_page = i
        if item_name == AUTHOR_TEXT_OBJECT:
            author_text_page = i
        if item_name[:4] == "Text":
            atts = getObjectAttributes(item_name)
            nm = list(filter(lambda x: x["Name"] == "TOC", atts))
            if len(nm) > 0:
                song_name = nm[0]["Value"]
                author = list(filter(lambda x: x["Name"] == "Autor", atts))[0]["Value"]
                author_sort = author
                if len(list(filter(lambda x: x["Name"] == "AutorSort", atts))) > 0:
                    author_sort = list(filter(lambda x: x["Name"] == "AutorSort", atts))[0]["Value"]
                page_num = i - page_offset
                songs.append(Song(name = song_name, author = author, author_sort = author_sort, pgnum = page_num))
                # print(f"{song_name}|{author}|{page_num}")
        scribus.progressSet(i)

locale.setlocale(locale.LC_ALL, "cs_CZ.UTF-8")
scribus.progressTotal(len(songs))
scribus.progressSet(0)

i = 0
toc = ""
if toc_text_page > 0:
    songs.sort(key=lambda x: x.pgnum)
    for song in songs:
        toc += f"{song.name} ({song.author})\t{song.pgnum}\n"
        scribus.progressSet(i)
        i += 1
    gotoPage(toc_text_page)
    setText(toc, TOC_TEXT_OBJECT)
    setParagraphStyle("Obsah", TOC_TEXT_OBJECT)

scribus.progressSet(0)
i = 0
toc = ""
if abc_text_page > 0:
    songs.sort(key=lambda x: locale.strxfrm(x.name))
    for song in songs:
        toc += f"{song.name} ({song.author})\t{song.pgnum}\n"
        scribus.progressSet(i)
        i += 1
    gotoPage(abc_text_page)
    setText(toc, ABC_TEXT_OBJECT)
    setParagraphStyle("Obsah", ABC_TEXT_OBJECT)

scribus.progressSet(0)
i = 0
toc = ""
if author_text_page > 0:
    songs.sort(key=lambda x: locale.strxfrm(f"{x.author_sort}#{x.name}"))
    current_author = ""
    for song in songs:
        if song.author_sort != current_author:
            toc += f"{song.author_sort}\n"
            current_author = song.author_sort
        toc += f"\t{song.name}\t{song.pgnum}\n"
        scribus.progressSet(i)
        i += 1
    gotoPage(author_text_page)
    setText(toc, AUTHOR_TEXT_OBJECT)
    setParagraphStyle("Obsah pro authory", AUTHOR_TEXT_OBJECT)

scribus.progressReset()
scribus.docChanged(True)
saveDoc()
filename = os.path.splitext(scribus.getDocName())[0]
pdf = scribus.PDFfile()
pdf.thumbnails = 1
pdf.file = filename + ".pdf"
pdf.save()
scribus.setRedraw(True)
scribus.statusMessage("Done")
