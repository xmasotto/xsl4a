#!/usr/bin/env python2

import BeautifulSoup
import urllib2
import json
from anki_util import expand_macro, is_prefix

def process_card(line):
    card = get_card(line)
    if card == None:
        return None
    else:
        front, back = card
        return process_side(front), process_side(back)

def get_card(line):
    line = line.strip()
    if "<" in line and ">" in line:
        return fill_in_blank_card(line)
    if ">" in line:
        return normal_card(line)
    if is_prefix(line, "wiki:"):
        return wiki_card(line[5:])
    if is_prefix(line, "define:"):
        return define_card(line[7:])

def process_side(txt):
    txt = expand_macro(
        txt, "$$", "$$", 
        lambda x: "[img:http://latex.codecogs.com/gif.latex?%s]" % x)
    return txt.strip()

def fill_in_blank_card(line):
    front = expand_macro(
        txt, "<", ">", lambda x: "(...)")
    return front, txt

def normal_card(line):
    return tuple(line.split(">")[:2])

def wiki_card(line):
    url = "http://en.wikipedia.org/wiki/%s" % line.strip()
    try:
        bs = BeautifulSoup.BeautifulSoup(urllib2.urlopen(url).read())
        src = ""
        tables = bs.findAll("table")
        for table in tables:
            if "infobox" in table['class']:
                src = "http:" + table.find("img")["src"]
                break
        front = '[img:%s]' % src
        back = "".join(bs.find("h1").findAll(text=True))
        return front, back
    except:
        raise
        return None

def define_card(line):
    word = line.strip()
    url = ("http://www.google.com/dictionary" + 
           "/json?callback=a&sl=en&tl=en&q=%s" % word)
    try:
        definition_limit = 2

        txt = urllib2.urlopen(url).read()
        txt = txt[2:txt.rindex(",200,null)")]
        obj = json.loads(urllib2.unquote(txt).decode("unicode_escape"))
        back = ""
        for primary in obj['primaries']:
            pos = ""
            for term in primary['terms']:
                if term['type'] == 'text':
                    pos = term['labels'][0]['text']
            back += pos + ":<br>"
            counter = 0
            for entry in primary['entries']:
                if entry['type'] == "meaning" and counter < definition_limit:
                    counter+=1
                    definition = entry['terms'][0]['text']
                    back += ("(%d) "%counter) + definition + "<br>"

        return word, back
    except:
        raise
        return None
