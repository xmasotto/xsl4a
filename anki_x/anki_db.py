#!/usr/bin/env python2
import sys
import os
import json
from anki_util import int_time

p = os.path.dirname(os.path.realpath(__file__))
sys.path.append(p + "/..")
import sqlite_server

def init(db):
    sqlite_server.load(os.path.abspath(db), "db")

# Load deck from db.
def get_deck(deckname):
    decks_json = sqlite_server.query("select decks from db.col")[0][0]
    decks = json.loads(decks_json)
    for deck in decks.values():
        if deck["name"] == deckname:
            return deck
    return None

# Create deck in db if it doesn't already exist.
def create_deck(deckname):
    decks_json = sqlite_server.query("select decks from db.col")[0][0]
    decks = json.loads(decks_json)
    for deck in decks.values():
        if deck["name"] == deckname:
            return deck

    deck_id = str(int_time(1000))
    new_deck = decks["1"].copy()
    new_deck["name"] = deckname
    new_deck["id"] = deck_id
    decks[deck_id] = new_deck

    sqlite_server.query("update db.col set decks=?;", json.dumps(decks))
    return new_deck

# Add a card (tuple of two strings, front/back) to the given deck.
# Returns the note id of the new card.
def add_card(deck, card):
    # Find the basic model
    models_json = sqlite_server.query("select models from db.col")[0][0]
    models = json.loads(models_json)
    nid = int_time(1000)
    did = deck["id"]
    mid = -1
    for model in models.values():
        if model["name"] == "Basic":
            mid = model["id"]

    # Insert note and card into database
    flds = card[0] + "\x1f" + card[1]
    sqlite_server.query(
        "insert into db.notes values (?,?,?,?,?,?,?,?,?,?,?)",
        nid,
        str(int_time(1000))[-5:],
        mid,
        int_time(1),
        -1,
        "",
        flds,
        card[0],
        0,
        0,
        "");
    sqlite_server.query(
        "insert into db.cards values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        int_time(1000),
        nid,
        did,
        0,
        int_time(1),
        -1,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "")
    return nid

# Delete the given card (tuple of two strings, front/back)
def delete_card(nid):
    sqlite_server.query("delete from db.notes where id=?", nid)
    sqlite_server.query("delete from db.cards where nid=?", nid)

# Get a list of note id's belonging to the default deck (which should be empty)
def get_default_cards():
    result = sqlite_server.query(
        "select nid from db.cards where did='1'")
    print(result)
    return [x[0] for x in result]

# Since Anki sometimes randomly changes the deck_id to 1, occasionally
# we have to fix the deck_id.
# Changes the deck_id of the card with the given node_id.
def fix_deck_id(note_id, deck_id):
    sqlite_server.query(
        "update db.cards set did=? where nid=?",
        deck_id,
        note_id)
