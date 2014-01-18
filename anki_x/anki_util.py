#!/usr/bin/env python2

import time
import os
import pickle
import urllib2

# Timestamp in ms.
def int_time(scale=1):
    return int(time.time()*scale)

def load_deck_data(deckname):
    if not os.path.isdir(".anki"):
        os.makedirs(".anki")
    filename = os.path.join(".anki", deckname + ".p")
    if os.path.isfile(filename):
       deck_data = pickle.load(open(filename))
    else:
        deck_data = {}
        deck_data['lines'] = []
        deck_data['nid2did'] = {}
        deck_data['url2img'] = {}
        deck_data['line2nid'] = {}
    return deck_data

def save_deck_data(deckname, data):
    if not os.path.isdir(".anki"):
        os.makedirs(".anki")
    filename = os.path.join(".anki", deckname + ".p")
    pickle.dump(data, open(filename, "wb"))

def expand_macro(txt, macro_start, macro_end, f):
    second = 0
    while True:
        first = txt.find(macro_start, second)
        second = txt.find(macro_end, first + len(macro_start))
        if first >= 0 and second >= 0:
            middle = f(txt[first+len(macro_start):second])
            txt = txt[:first] + middle + txt[second+len(macro_end):]
            second = first + len(middle)
        else:
            break
    return txt

def is_prefix(txt, prefix):
    return txt[:len(prefix)].lower() == prefix.lower()

# saves the image to the local media directory, and returns
# the new filename.
def save_image(anki_dir, url):
    media_dir = os.path.join(anki_dir, "collection.media")
    if not os.path.isdir(media_dir):
        os.makedirs(media_dir)

    filename = "img" + str(int_time(1000))
    f = open(os.path.join(media_dir, filename), "wb")
    f.write(urllib2.urlopen(url).read())
    return filename
