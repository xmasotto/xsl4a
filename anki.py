import sqlite3
import gdata.docs.service
import os
import json
import time

def find_anki_decks(username, password):
    result = []
    client = gdata.docs.service.DocsService()
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
    lastj = 0
    for i in range(len(old)):
        found = False
        for j in range(lastj, len(new)):
            if old[i] == new[j]:
                found = True
                inserted.extend(new[lastj:j])
                lastj = j+1
        if not found:
            deleted.append(old[i])
    inserted.extend(new[lastj:])
    return inserted, deleted

def is_card(line):
    if ">" not in line:
        return False
    a, b = process_card(line)
    return len(a) > 0 and len(b) > 0

def process_card(line):
    a, b = line.split(">")
    return a.strip(), b.strip()

def update_database(filename, deckname, new, inserted, deleted):
    print(inserted)
    print(deleted)
    conn = sqlite3.connect(filename)
    deck_id = get_deck(conn, deckname)
    if not deck_id:
        deck_id = create_deck(conn, deckname)
        for card in new:
            add_card(conn, deck_id, card)
            print("Inserted {} cards.".format(len(new)))
    else:
        for card in inserted:
            add_card(conn, deck_id, card)
        for card in deleted:
            delete_card(conn, deck_id, card)
        print("Inserted {} cards.".format(len(inserted)))
        print("Deleted {} cards.".format(len(deleted)))
    conn.commit()
    conn.close()

def get_deck(conn, deckname):
    decks_json = conn.execute("select decks from col").fetchone()[0]
    decks = json.loads(decks_json)
    for deck in decks.values():
        if deck["name"] == deckname:
            print("Syncing Deck: {}".format(deckname))
            return deck["id"]
    return None

def create_deck(conn, deckname):
    decks_json = conn.execute("select decks from col").fetchone()[0]
    decks = json.loads(decks_json)
    deck_id = str(int(time.time() * 1000))
    new_deck = decks["1"].copy()
    new_deck["name"] = deckname
    new_deck["id"] = deck_id
    decks[deck_id] = new_deck
    conn.execute("update col set decks=?;", [json.dumps(decks)])
    print("Creating Deck: {}".format(deckname))

def add_card(conn, deck_id, card):
    pass

def delete_card(conn, deck_id, card):
    pass

"""
import android
droid = android.Android()
username = f.read().strip() if f else droid.dialogGetInput("Username").result
password = droid.dialogGetPassword("Password").result
"""

username = "xmasotto"
password = "nubnub57"

decks = find_anki_decks(username, password)
print(decks)

if not os.path.isdir(".anki"):
    os.makedirs(".anki")
for name, text in decks:
    filename = ".anki/" + name
    old = []
    if os.path.isfile(filename):
        old = [x.strip() for x in open(filename).readlines()]
    new = text.splitlines()
    open(filename, "w").writelines(text)
    inserted, deleted = findInsertedDeleted(new, old)
    new = [process_card(x) for x in new if is_card(x)]
    inserted = [process_card(x) for x in inserted if is_card(x)]
    deleted = [process_card(x) for x in deleted if is_card(x)]
    update_database("hello/collection.anki2", name, new, inserted, deleted)

