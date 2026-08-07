#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traegt einen Vorlagenwert in data/manual.json ein.

Wird vom Workflow 'Vorlagen eintragen' aufgerufen und liest die Eingaben
aus Umgebungsvariablen. Laesst sich auch lokal benutzen:

    SPIELER="Julian Brandt" VORLAGEN=7 SPIELTAG=12 python scripts/vorlagen.py
"""

import json
import os
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PFAD = os.path.join(WURZEL, "data", "manual.json")


def zahl(text, bezeichnung):
    roh = (text or "").strip().replace(",", ".")
    try:
        wert = int(float(roh))
    except ValueError:
        raise SystemExit(f"'{bezeichnung}' muss eine Zahl sein, war aber: {text!r}")
    if wert < 0:
        raise SystemExit(f"'{bezeichnung}' darf nicht negativ sein.")
    return wert


def main():
    spieler = (os.environ.get("SPIELER") or "").strip()
    if not spieler:
        raise SystemExit("Kein Spielername angegeben.")
    if len(spieler) > 60:
        raise SystemExit("Spielername ist unplausibel lang.")

    loeschen = (os.environ.get("LOESCHEN") or "").strip().lower() in ("true", "1", "ja", "yes")
    spieltag = zahl(os.environ.get("SPIELTAG"), "Spieltag")
    if spieltag > 34:
        raise SystemExit("Die Bundesliga hat 34 Spieltage.")

    with open(PFAD, "r", encoding="utf-8") as datei:
        inhalt = json.load(datei)
    inhalt.setdefault("bvb_vorlagen", {})

    if loeschen:
        entfernt = None
        for vorhanden in list(inhalt["bvb_vorlagen"]):
            if vorhanden.strip().lower() == spieler.lower():
                entfernt = vorhanden
                del inhalt["bvb_vorlagen"][vorhanden]
        print(f"Entfernt: {entfernt}" if entfernt else f"'{spieler}' war gar nicht eingetragen.")
    else:
        vorlagen = zahl(os.environ.get("VORLAGEN"), "Vorlagen")
        if vorlagen > 40:
            raise SystemExit("Mehr als 40 Vorlagen in einer Saison? Bitte nochmal pruefen.")
        # bestehenden Eintrag mit abweichender Schreibweise ersetzen
        for vorhanden in list(inhalt["bvb_vorlagen"]):
            if vorhanden.strip().lower() == spieler.lower():
                del inhalt["bvb_vorlagen"][vorhanden]
        vorher = inhalt["bvb_vorlagen"].get(spieler)
        inhalt["bvb_vorlagen"][spieler] = vorlagen
        print(f"{spieler}: {vorher if vorher is not None else '–'} -> {vorlagen} Vorlagen")

    inhalt["bvb_vorlagen"] = dict(
        sorted(inhalt["bvb_vorlagen"].items(), key=lambda paar: (-paar[1], paar[0]))
    )
    inhalt["stand_spieltag"] = spieltag

    with open(PFAD, "w", encoding="utf-8") as datei:
        json.dump(inhalt, datei, ensure_ascii=False, indent=2)
        datei.write("\n")

    print(f"Stand gepflegt bis Spieltag {spieltag}.")


if __name__ == "__main__":
    sys.exit(main())
