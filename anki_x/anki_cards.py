#!/usr/bin/env python2

import BeautifulSoup
import urllib2
import json
import re
import traceback
from anki_util import expand_macro, is_prefix

def process_cards(line):
    cards = get_cards(line)
    result = []
    for card in cards:
        front, back = card
        result.append((process_side(front), process_side(back)))
    return result

def get_cards(line):
    line = line.strip()
    if "{" in line and "}" in line:
        return enum_card(line)
    if "<" in line and ">" in line:
        return fill_in_blank_card(line)
    if ">" in line:
        return normal_card(line)
    if is_prefix(line, "wiki:"):
        return wiki_card(line[5:])
    if is_prefix(line, "define:"):
        return define_card(line[7:])
    if is_prefix(line, "python:"):
        return python_cards(line[7:])
    return []

def process_side(txt):
    txt = expand_macro(
        txt, "$$", "$$", 
        lambda x: "[img:http://latex.codecogs.com/gif.latex?%s]" % x)
    return txt.strip()

def fill_in_blank_card(line):
    front = expand_macro(
        line, "<", ">", lambda x: "(...)")
    back = expand_macro(
        line, "<", ">", lambda x: x)
    return [(front, back)]

def enum_card(line):
    try:
        result = []
        items = []
        def extract_items(x):
            items.extend(x.split(","))
            return "%s"
        line = line.replace("%","")
        line = expand_macro(line, "{", "}", extract_items)
        n = len(items)
        if n > 1:
            k = (3 if n > 3 else n-1)
            for i in range(n-k):
                front = items[:i]
                middle = [" ___ "]*k
                end = items[i+k:]
                items2 = front + middle + end
                front = line % (', '.join(items2))
                back = ', '.join(items[i:i+k])
                result.append((front, back))
        return result
    except:
        print ("Exception: %s" % line)
        traceback.print_exc()
        return []

def normal_card(line):
    return [tuple(line.split(">")[:2])]

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
        return [(front, back)]
    except:
        print("Exception: %s" % line)
        traceback.print_exc()
        return []

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

        return [(word, back)]
    except:
        print("Exception: %s" % line)
        traceback.print_exc()
        return []

import __builtin__

def python_cards(line):
    line = line.strip()
    if line in dir(__builtin__):
        return python_dir_cards(line, getattr(__builtin__, line))

    if '.' in line:
        ind = line.rfind(".")
        try:
            module = __import__(line[:ind])
            obj = getattr(module, line[ind+1:])
            if type(obj) == type:
                return python_dir_cards(line, obj)
        except:
            print("Exception: %s" % line)
            traceback.print_exc()

    try:
        module = __import__(line)
        return python_dir_cards(line, module)
    except:
        print("Exception: %s" % line)
        traceback.print_exc()

    return []

def python_dir_cards(line, module):
    try:
        result = []
        for attr in dir(module):
            obj = getattr(module, attr)
            if not hasattr(obj, '__call__'):
                continue
            if type(obj) == type:
                continue
            if attr[0] == "_" or "__" in attr:
                continue
            if obj.__doc__:
                ds = obj.__doc__.split("\n\n")
                doc_lines = []
                for i, d in enumerate(ds):
                    if d.strip() == "":
                        continue
                    doc_lines.append(d)
                    if attr not in d:
                        break
                doc = "<br>".join(doc_lines)
                doc2 = re.sub(r'\b%s\('%attr, 'function(', doc)
                front = "In module %s ... <br>%s" % (line, doc2) 
                back = "%s.%s()" % (line, attr)
                result.append((front, back))
    except:
        print("Exception: %s" % line)
        traceback.print_exc()
    return result
