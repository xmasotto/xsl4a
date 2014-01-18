import BeautifulSoup
import urllib2
import json

def embed_latex(txt):
    second = 0
    while True:
        first = txt.find("$$", second)
        second = txt.find("$$", first+2)
        if first >= 0 and second >= 0:
            latex = urllib.quote_plus(
                txt[first+2:second].replace(" ",""))
            middle = ('<img src="http://latex.codecogs.com/gif.latex?%s" />' 
                      % latex)
            txt = txt[:first] + middle + txt[second+2:]
            second = first + len(middle)
        else:
            break
    return txt

def process_cards(lines):
    result = []
    for line in lines:
        line = line.strip()
        card = process_card(line)
        if card != None:
            print(card)
            result.append((
                    embed_latex(card[0].strip()),
                    embed_latex(card[1].strip())))
    return result

def process_card(line):
    if "<" in line and ">" in line:
        return fill_in_blank_card(line)
    if ">" in line:
        return front_back_card(line)
    if line[:5] == "wiki:":
        return wikipedia_card(line[5:])
    if line[:7] == "define:":
        return definition_card(line[7:])
    return None

def front_back_card(line):
    return tuple(line.split(">")[:2])

def fill_in_blank_card(line):
    txt = line
    second = 0
    while True:
        first = txt.find("<", second)
        second = txt.find(">", first+1)
        if first >= 0 and second >= 0:
            middle = "(...)"
            txt = txt[:first] + middle + txt[second+1:]
            second = first + len(middle)
        else:
            break
    line = line.replace("<", "")
    line = line.replace(">", "")
    return txt, line

def wikipedia_card(line):
    url = "http://en.wikipedia.org/wiki/%s" % line.strip()
    try:
        bs = BeautifulSoup.BeautifulSoup(urllib2.urlopen(url).read())
        src = "http:" + bs.find("img")["src"]
        front = '<img src="%s" />' % src
        print(bs.find("title"))
        print(bs.find("h1"))
        back = "".join(bs.find("h1").findAll(text=True))
        return front, back
    except:
        raise
        return None

def definition_card(line):
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
            back += pos + ":\n"
            counter = 0
            for entry in primary['entries']:
                if entry['type'] == "meaning" and counter < definition_limit:
                    counter+=1
                    definition = entry['terms'][0]['text']
                    back += ("(%d) "%counter) + definition + "\n"

        return word, back
    except:
        raise
        return None

