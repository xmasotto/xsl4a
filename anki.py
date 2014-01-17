import sqlite_server
import gdata.docs.service
import os
import json

from anki_utils import *

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

def update_database(db, deckname, new, inserted, deleted):
    sqlite_server.load(db, "db")
    deck = get_deck(deckname)
    if not deck:
        deck = create_deck(deckname)
        for card in new:
            add_card(deck, card)
        print("Inserted %d cards." % len(new))
    else:
        for card in inserted:
            add_card(deck, card)
        for card in deleted:
            delete_card(deck, card)
        print("Inserted %d cards." % len(inserted))
        print("Deleted %d cards." % len(deleted))

def get_deck(deckname):
    decks_json = sqlite_server.query("select decks from db.col")[0][0]
    decks = json.loads(decks_json)
    for deck in decks.values():
        if deck["name"] == deckname:
            print("Syncing Deck: %s" % deckname)
            return deck
    return None

def create_deck(deckname):
    decks_json = sqlite_server.query("select decks from db.col")[0][0]
    decks = json.loads(decks_json)
    deck_id = str(intTime(1000))
    new_deck = decks["1"].copy()
    new_deck["name"] = deckname
    new_deck["id"] = deck_id
    decks[deck_id] = new_deck
    sqlite_server.query("update db.col set decks=?;", json.dumps(decks))
    print("Creating Deck: %s" % deckname)
    return new_deck

def add_card(deck, card):
    models_json = sqlite_server.query("select models from db.col")[0][0]
    models = json.loads(models_json)
    mid = models.keys().pop()
    nid = intTime(1000)
    did = deck["id"]

    flds = card[0] + " " + card[1]
    print("Adding %s | %s" % card)

    # add a note
    sqlite_server.query(
        "insert into db.notes values (?,?,?,?,?,?,?,?,?,?,?)",
        nid,
        str(intTime(1000))[-5:],
        mid,
        intTime(1),
        -1,
        "",
        flds,
        card[0],
        fieldChecksum(flds.split()[0]),
        0,
        "");

    # add a card
    sqlite_server.query(
        "insert into db.cards values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        intTime(1000),
        nid,
        did,
        0,
        intTime(1),
        -1,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "")

def delete_card(deck_id, card):
    flds = card[0] + " " + card[1]
    print("Deleting %s | %s" % card)

    results = sqlite_server.query("select id from db.notes where flds=?", flds);
    for result in results:
        nid = result[0]
        sqlite_server.query("delete from db.notes where id=?", nid)
        sqlite_server.query("delete from db.cards where nid=?", nid)

import android
droid = android.Android()
filename = "/sdcard/sl4a/scripts/.username"
if os.path.isfile(filename):
    username = open(filename).read().strip()
else:
    username = droid.dialogGetInput("Username").result
password = droid.dialogGetPassword("Password").result

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
    update_database("/sdcard/AnkiDroid/collection.anki2", name, new, inserted, deleted)
#    update_database("hello/collection.anki2", name, new, inserted, deleted)

