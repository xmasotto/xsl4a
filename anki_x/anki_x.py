#!/usr/bin/env python2
import sys
import os
import json
import gdata.docs.service

import anki_db
import anki_cards
import anki_util

sys.path.append(os.path.abspath('..'))
import xandroid

if xandroid.HAS_ANDROID:
    ANKI_DIR = "/sdcard/AnkiDroid"
else:
    ANKI_DIR = "AnkiDroid"

ANKI_DB = os.path.join(ANKI_DIR, "collection.anki2")


def main():
    username = xandroid.get_saved_input("anki.py_google_username")
    password = xandroid.get_saved_password("anki.py_google_password")

    print("Logging in as %s..." % username)

    decks = find_anki_decks(username, password)
    xandroid.save("anki.py_google_username", username)
    xandroid.save("anki.py_google_password", password)

    print("Logged in, %d decks found." % len(decks))

    anki_db.init(ANKI_DB)
    for name, text in decks:
        new = list(set([x.strip() for x in text.splitlines()]))
        deck_main(name, new)

def deck_main(deckname, new):
    # deck_data:
    #  lines, nid2did, url2img, line2nid
    deck_data = anki_util.load_deck_data(deckname)
    old = deck_data['lines']

    # update the decks
    deck = anki_db.get_deck(deckname)
    if deck == None:
        print("Creating deck: %s" % deckname)
        deck = anki_db.create_deck(deckname)
        for line in new:
            insert_card(deck, line, deck_data)
    else:
        print("Syncing deck: %s" % deckname)
        inserted, deleted = findInsertedDeleted(new, old)
        for line in deleted:
            delete_card(deck, line, deck_data)
        for line in inserted:
            insert_card(deck, line, deck_data)

    # fix corrupted decks
    for nid in anki_db.get_default_cards():
        if nid in deck_data['nid2did']:
            anki_db.fix_deck_id(
                nid, deck_data['nid2did'])
            print("Fixed %s" % nid)

    deck_data['lines'] = new
    anki_util.save_deck_data(deckname, deck_data)

def insert_card(deck, line, deck_data):
    card = anki_cards.process_card(line)
    if card != None:
        def expand_image(url):
            filename = anki_util.save_image(ANKI_DIR, url)
            deck_data['url2img'][url] = filename
            return '<img src="%s"/>' % filename

        front = anki_util.expand_macro(card[0], "[img:", "]", expand_image)
        back = anki_util.expand_macro(card[1], "[img:", "]", expand_image)
        nid = anki_db.add_card(deck, (front, back))
        deck_data['line2nid'][line] = nid
        print(front, back)
        print("Added card: %s" % line)

def delete_card(deck, line, deck_data):
    nid = deck_data['line2nid'][line]
    anki_db.delete_card(nid)
    print("Deleted card: %s" % line)

def find_anki_decks(username, password):
    result = []
    client = gdata.docs.service.DocsService()
    client.ssl = True
    client.ClientLogin(username, password)
    for doc in client.GetDocumentListFeed().entry:
        title = doc.title.text
        if title[:5].lower() == "anki:":
            uri = doc.GetMediaURL() + "&format=txt"
            text = client.GetMedia(uri).file_handle.read()[3:]
            result.append( (title[5:], text) )
    return result

def findInsertedDeleted(new, old):
    inserted, deleted = [], []
    new = set(new)
    old = set(old)
    for line in new:
        if line not in old:
            inserted.append(line)
    for line in old:
        if line not in new:
            deleted.append(line)
    return inserted, deleted

if __name__ == '__main__':
    main()