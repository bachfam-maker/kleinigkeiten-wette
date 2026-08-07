#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kleinigkeiten-Wette - Datenaktualisierung

Holt:
  Premier League  -> Fantasy-Premier-League-API (frei, kein Key)
  Bundesliga      -> OpenLigaDB (frei, kein Key)
  BVB-Vorlagen    -> data/manual.json (von Hand gepflegt)

Schreibt: data.json im Projektstamm.

Bricht bei Fehlern hart ab, damit eine kaputte Antwort niemals
eine gute data.json ueberschreibt.
"""

import json
import math
import os
import random
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------- Konfiguration

SAISON_LABEL = "2026/27"
OLDB_SAISON = "2026"          # OpenLigaDB-Saisonschluessel (Startjahr)
FAKTOR_BL = 38 / 34           # 1.1176470588... Angleichung 34 -> 38 Spiele

PL_SPIELE = 38
BL_SPIELE = 34

TRIKOT_TEAM = "Chelsea"
TRIKOT_START = 10.0           # Startwahrscheinlichkeit in Prozent

PL_VEREIN = "Liverpool"
PL_STUERMER = "Isak"

BL_VEREIN_SUCHE = "Dortmund"
BL_STUERMER = "Guirassy"

SIMULATIONEN = 30000
PRIOR_SPIELE = 8.0            # Staerke des Vorwissens fuer die Punkte-pro-Spiel
PRIOR_PPS = 1.36              # Liga-Durchschnitt Punkte pro Spiel
UNENTSCHIEDEN_ANTEIL = 0.25

FPL_BASE = "https://fantasy.premierleague.com/api"
OLDB_BASE = "https://api.openligadb.de"

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUAL_PFAD = os.path.join(WURZEL, "data", "manual.json")
AUSGABE_PFAD = os.path.join(WURZEL, "data.json")


# ---------------------------------------------------------------- Hilfsmittel

def hole(url):
    """GET auf eine JSON-Schnittstelle. Wirft bei jedem Problem."""
    anfrage = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kleinigkeiten-wette/1.0 (+github pages hobby project)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(anfrage, timeout=45) as antwort:
            return json.loads(antwort.read().decode("utf-8"))
    except urllib.error.HTTPError as fehler:
        raise SystemExit(f"HTTP {fehler.code} bei {url}") from fehler
    except Exception as fehler:  # noqa: BLE001
        raise SystemExit(f"Abruf fehlgeschlagen bei {url}: {fehler}") from fehler


def schluessel(name):
    """Namen vergleichbar machen: ohne Akzente, ohne Punkte, klein."""
    ohne_akzente = "".join(
        zeichen
        for zeichen in unicodedata.normalize("NFKD", name or "")
        if not unicodedata.combining(zeichen)
    )
    gesaeubert = "".join(
        zeichen if zeichen.isalnum() or zeichen.isspace() else " "
        for zeichen in ohne_akzente
    )
    return " ".join(gesaeubert.lower().split())


def nachname(name):
    teile = schluessel(name).split()
    return teile[-1] if teile else ""


def runde1(wert):
    return round(wert + 1e-9, 1)


# ---------------------------------------------------------------- Premier League

def premier_league():
    """Liefert (spieler_daten, tabelle, spieltag) fuer die Premier League."""
    stamm = hole(f"{FPL_BASE}/bootstrap-static/")
    spiele = hole(f"{FPL_BASE}/fixtures/")

    vereine = {v["id"]: v for v in stamm.get("teams", [])}
    if not vereine:
        raise SystemExit("FPL: keine Vereine in bootstrap-static gefunden.")

    def verein_id(gesucht):
        for kennung, verein in vereine.items():
            if schluessel(verein.get("name", "")) == schluessel(gesucht):
                return kennung
        raise SystemExit(f"FPL: Verein '{gesucht}' nicht gefunden.")

    lfc_id = verein_id(PL_VEREIN)

    # --- Tabelle aus beendeten Spielen rechnen (die FPL-Tabellenfelder sind leer)
    tabelle = {
        kennung: {"name": verein["name"], "spiele": 0, "punkte": 0, "diff": 0}
        for kennung, verein in vereine.items()
    }
    for spiel in spiele:
        if not spiel.get("finished"):
            continue
        heim, aus = spiel.get("team_h"), spiel.get("team_a")
        tore_h, tore_a = spiel.get("team_h_score"), spiel.get("team_a_score")
        if tore_h is None or tore_a is None:
            continue
        if heim not in tabelle or aus not in tabelle:
            continue
        tabelle[heim]["spiele"] += 1
        tabelle[aus]["spiele"] += 1
        tabelle[heim]["diff"] += tore_h - tore_a
        tabelle[aus]["diff"] += tore_a - tore_h
        if tore_h > tore_a:
            tabelle[heim]["punkte"] += 3
        elif tore_a > tore_h:
            tabelle[aus]["punkte"] += 3
        else:
            tabelle[heim]["punkte"] += 1
            tabelle[aus]["punkte"] += 1

    spieltag = max((eintrag["spiele"] for eintrag in tabelle.values()), default=0)

    # --- Liverpool-Spieler
    lfc_spieler = []
    for spieler in stamm.get("elements", []):
        if spieler.get("team") != lfc_id:
            continue
        anzeige = spieler.get("web_name") or spieler.get("second_name") or "?"
        lfc_spieler.append(
            {
                "name": anzeige,
                "voll": f"{spieler.get('first_name','')} {spieler.get('second_name','')}".strip(),
                "tore": int(spieler.get("goals_scored") or 0),
                "vorlagen": int(spieler.get("assists") or 0),
            }
        )
    if not lfc_spieler:
        raise SystemExit("FPL: keine Liverpool-Spieler gefunden.")

    return lfc_spieler, tabelle, spieltag


# ---------------------------------------------------------------- Bundesliga

def bundesliga():
    """Liefert (bvb_tore_je_spieler, spieltag) aus OpenLigaDB."""
    partien = hole(f"{OLDB_BASE}/getmatchdata/bl1/{OLDB_SAISON}")
    if not isinstance(partien, list) or not partien:
        raise SystemExit("OpenLigaDB: keine Spieldaten fuer die Saison erhalten.")

    def ist_bvb(verein):
        return BL_VEREIN_SUCHE.lower() in (verein.get("teamName") or "").lower()

    tore = {}
    spieltag = 0
    bvb_partien = 0

    for partie in partien:
        beendet = bool(partie.get("matchIsFinished"))
        gruppe = partie.get("group") or {}
        if beendet:
            spieltag = max(spieltag, int(gruppe.get("groupOrderID") or 0))

        team1 = partie.get("team1") or {}
        team2 = partie.get("team2") or {}
        bvb_ist_team1 = ist_bvb(team1)
        bvb_ist_team2 = ist_bvb(team2)
        if not (bvb_ist_team1 or bvb_ist_team2):
            continue
        if not beendet:
            continue
        bvb_partien += 1

        stand1, stand2 = 0, 0
        for treffer in sorted(
            partie.get("goals") or [], key=lambda g: (g.get("goalID") or 0)
        ):
            neu1 = treffer.get("scoreTeam1")
            neu2 = treffer.get("scoreTeam2")
            if neu1 is None or neu2 is None:
                continue
            bvb_hat_getroffen = (
                (neu1 > stand1 and bvb_ist_team1) or (neu2 > stand2 and bvb_ist_team2)
            )
            stand1, stand2 = neu1, neu2
            if not bvb_hat_getroffen:
                continue
            if treffer.get("isOwnGoal"):
                continue  # Eigentor zaehlt dem Schuetzen nicht als Tor
            name = (treffer.get("goalGetterName") or "").strip()
            if not name:
                continue
            tore[name] = tore.get(name, 0) + 1

    if bvb_partien == 0 and spieltag > 2:
        raise SystemExit(
            "OpenLigaDB: kein einziges beendetes BVB-Spiel gefunden, "
            "obwohl die Saison laeuft. Vereinsname pruefen."
        )

    return tore, spieltag, bvb_partien


# ---------------------------------------------------------------- Chelsea-Modell

def meisterwahrscheinlichkeit(tabelle, ziel_id):
    """
    Monte-Carlo auf Basis des aktuellen Tabellenstands, danach gegen den
    Startwert gewichtet: je mehr Spiele noch offen sind, desto naeher
    bleibt das Ergebnis an TRIKOT_START.
    """
    gespielt_max = max((e["spiele"] for e in tabelle.values()), default=0)
    if gespielt_max == 0:
        return TRIKOT_START, TRIKOT_START

    kennungen = list(tabelle.keys())
    verteilungen = []
    for kennung in kennungen:
        eintrag = tabelle[kennung]
        gespielt = eintrag["spiele"]
        offen = max(PL_SPIELE - gespielt, 0)

        # Punkte pro Spiel, zum Ligaschnitt hin gedaempft
        pps = (eintrag["punkte"] + PRIOR_SPIELE * PRIOR_PPS) / (gespielt + PRIOR_SPIELE)
        pps = min(max(pps, 0.05), 2.95)

        p_sieg = min(max((pps - UNENTSCHIEDEN_ANTEIL) / 3.0, 0.0), 1.0 - UNENTSCHIEDEN_ANTEIL)
        erwartung = 3 * p_sieg + UNENTSCHIEDEN_ANTEIL
        zweites_moment = 9 * p_sieg + UNENTSCHIEDEN_ANTEIL
        varianz_je_spiel = max(zweites_moment - erwartung**2, 1e-6)

        verteilungen.append(
            {
                "id": kennung,
                "basis": eintrag["punkte"],
                "mittel": erwartung * offen,
                "streuung": math.sqrt(varianz_je_spiel * offen),
            }
        )

    if all(v["streuung"] == 0 for v in verteilungen):
        # Saison zu Ende: reine Tabelle entscheidet
        beste = max(tabelle.values(), key=lambda e: (e["punkte"], e["diff"]))
        ziel = tabelle[ziel_id]
        modell = 100.0 if (ziel["punkte"], ziel["diff"]) == (beste["punkte"], beste["diff"]) else 0.0
        return modell, modell

    zufall = random.Random(20262027)
    treffer = 0.0
    for _ in range(SIMULATIONEN):
        bestwert = None
        beste_ids = []
        for verteilung in verteilungen:
            wert = verteilung["basis"]
            if verteilung["streuung"] > 0:
                wert += zufall.gauss(verteilung["mittel"], verteilung["streuung"])
            else:
                wert += verteilung["mittel"]
            if bestwert is None or wert > bestwert + 1e-9:
                bestwert = wert
                beste_ids = [verteilung["id"]]
            elif abs(wert - bestwert) <= 1e-9:
                beste_ids.append(verteilung["id"])
        if ziel_id in beste_ids:
            treffer += 1.0 / len(beste_ids)

    modell = 100.0 * treffer / SIMULATIONEN
    gewicht = min(max(gespielt_max / PL_SPIELE, 0.0), 1.0)
    gemischt = gewicht * modell + (1 - gewicht) * TRIKOT_START
    return gemischt, modell


# ---------------------------------------------------------------- Zusammenbau

def lade_manuell():
    if not os.path.exists(MANUAL_PFAD):
        return {}, None
    with open(MANUAL_PFAD, "r", encoding="utf-8") as datei:
        inhalt = json.load(datei)
    vorlagen = inhalt.get("bvb_vorlagen") or {}
    sauber = {}
    for name, anzahl in vorlagen.items():
        try:
            sauber[name.strip()] = int(anzahl)
        except (TypeError, ValueError):
            continue
    return sauber, inhalt.get("stand_spieltag")


def top_drei(kandidaten, ausschluss_nachname):
    """Sortiert nach Scorerpunkten und gibt hoechstens drei Eintraege zurueck."""
    gefiltert = [
        eintrag
        for eintrag in kandidaten
        if ausschluss_nachname not in (nachname(eintrag["name"]), nachname(eintrag.get("voll", "")))
    ]
    gefiltert.sort(key=lambda e: (-(e["tore"] + e["vorlagen"]), -e["tore"], schluessel(e["name"])))
    return gefiltert[:3]


def als_zeilen(eintraege, faktor):
    zeilen = []
    for stelle, eintrag in enumerate(eintraege):
        roh = eintrag["tore"] + eintrag["vorlagen"]
        zeilen.append(
            {
                "name": eintrag["name"],
                "tore": eintrag["tore"],
                "vorlagen": eintrag["vorlagen"],
                "roh": roh,
                "wert": runde1(roh * faktor),
                "zaehlt": stelle == 0,
            }
        )
    return zeilen


def main():
    print("Premier League abrufen ...")
    lfc_spieler, pl_tabelle, pl_spieltag = premier_league()

    print("Bundesliga abrufen ...")
    bvb_tore, bl_spieltag, bvb_partien = bundesliga()

    manuelle_vorlagen, manueller_stand = lade_manuell()

    # ---- Hendrik (Premier League)
    isak = None
    for spieler in lfc_spieler:
        if nachname(spieler["voll"]) == schluessel(PL_STUERMER) or schluessel(
            spieler["name"]
        ) == schluessel(PL_STUERMER):
            isak = spieler
            break
    isak_tore = isak["tore"] if isak else 0

    lfc_top = top_drei(lfc_spieler, schluessel(PL_STUERMER))
    hendrik_zeilen = als_zeilen(lfc_top, 1.0)
    hendrik_punkte = runde1(isak_tore + (hendrik_zeilen[0]["wert"] if hendrik_zeilen else 0.0))

    # ---- Marvin (Bundesliga)
    guirassy_tore = 0
    bvb_kandidaten = []
    namen_gesehen = set()

    for name, tore in bvb_tore.items():
        if nachname(name) == schluessel(BL_STUERMER):
            guirassy_tore = tore
            continue
        vorlagen = 0
        for manuell_name, manuell_wert in manuelle_vorlagen.items():
            if schluessel(manuell_name) == schluessel(name) or nachname(manuell_name) == nachname(name):
                vorlagen = manuell_wert
                break
        namen_gesehen.add(nachname(name))
        bvb_kandidaten.append({"name": name, "voll": name, "tore": tore, "vorlagen": vorlagen})

    # Spieler, die nur Vorlagen haben und daher in keiner Torschuetzenliste stehen
    for manuell_name, manuell_wert in manuelle_vorlagen.items():
        if nachname(manuell_name) == schluessel(BL_STUERMER):
            continue
        if nachname(manuell_name) in namen_gesehen:
            continue
        bvb_kandidaten.append(
            {"name": manuell_name, "voll": manuell_name, "tore": 0, "vorlagen": manuell_wert}
        )

    bvb_top = top_drei(bvb_kandidaten, schluessel(BL_STUERMER))
    marvin_zeilen = als_zeilen(bvb_top, FAKTOR_BL)
    marvin_stuermer_wert = runde1(guirassy_tore * FAKTOR_BL)
    marvin_punkte = runde1(
        marvin_stuermer_wert + (marvin_zeilen[0]["wert"] if marvin_zeilen else 0.0)
    )

    # ---- Trikot-Wette
    chelsea_id = None
    for kennung, eintrag in pl_tabelle.items():
        if schluessel(eintrag["name"]) == schluessel(TRIKOT_TEAM):
            chelsea_id = kennung
            break
    if chelsea_id is None:
        raise SystemExit(f"FPL: '{TRIKOT_TEAM}' nicht in der Tabelle gefunden.")

    print("Meisterwahrscheinlichkeit simulieren ...")
    wahrscheinlichkeit, modellwert = meisterwahrscheinlichkeit(pl_tabelle, chelsea_id)

    sortiert = sorted(
        pl_tabelle.items(), key=lambda paar: (-paar[1]["punkte"], -paar[1]["diff"], paar[1]["name"])
    )
    platz = next(
        (stelle + 1 for stelle, (kennung, _) in enumerate(sortiert) if kennung == chelsea_id),
        None,
    )
    spitzenreiter = sortiert[0][1] if sortiert else None
    chelsea = pl_tabelle[chelsea_id]
    rueckstand = (
        spitzenreiter["punkte"] - chelsea["punkte"] if spitzenreiter and chelsea["spiele"] else None
    )

    # ---- Duellstand
    differenz = runde1(hendrik_punkte - marvin_punkte)
    if differenz > 3:
        lage = {"hendrik": "vorne", "marvin": "hinten"}
    elif differenz < -3:
        lage = {"hendrik": "hinten", "marvin": "vorne"}
    else:
        lage = {"hendrik": "knapp", "marvin": "knapp"}

    daten = {
        "generiert": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "saison": SAISON_LABEL,
        "faktor_bl": round(FAKTOR_BL, 10),
        "trikot": {
            "verein": TRIKOT_TEAM,
            "startwert": TRIKOT_START,
            "wahrscheinlichkeit": round(wahrscheinlichkeit, 1),
            "modellwert": round(modellwert, 1),
            "platz": platz if chelsea["spiele"] else None,
            "punkte": chelsea["punkte"],
            "spiele": chelsea["spiele"],
            "rueckstand": rueckstand,
            "spitzenreiter": spitzenreiter["name"] if spitzenreiter and chelsea["spiele"] else None,
        },
        "ligen": {
            "bl": {"spieltag": bl_spieltag, "gesamt": BL_SPIELE, "partien_verein": bvb_partien},
            "pl": {"spieltag": pl_spieltag, "gesamt": PL_SPIELE},
        },
        "marvin": {
            "liga": "Bundesliga",
            "verein": "Borussia Dortmund",
            "stuermer": {
                "name": "Guirassy",
                "tore": guirassy_tore,
                "wert": marvin_stuermer_wert,
            },
            "scorer": marvin_zeilen,
            "punkte": marvin_punkte,
            "lage": lage["marvin"],
        },
        "hendrik": {
            "liga": "Premier League",
            "verein": "Liverpool",
            "stuermer": {
                "name": "Isak",
                "tore": isak_tore,
                "wert": runde1(isak_tore),
            },
            "scorer": hendrik_zeilen,
            "punkte": hendrik_punkte,
            "lage": lage["hendrik"],
        },
        "differenz": differenz,
        "vorlagen_stand": manueller_stand,
    }

    with open(AUSGABE_PFAD, "w", encoding="utf-8") as datei:
        json.dump(daten, datei, ensure_ascii=False, indent=2)
        datei.write("\n")

    print(f"\ndata.json geschrieben.")
    print(f"  Marvin  {marvin_punkte}  |  Hendrik  {hendrik_punkte}  |  Differenz {differenz}")
    print(f"  Chelsea {daten['trikot']['wahrscheinlichkeit']} % (Modell roh: {daten['trikot']['modellwert']} %)")
    if bvb_tore:
        print("\n  BVB-Torschuetzen laut OpenLigaDB (exakte Schreibweise fuer das Formular):")
        for name, tore in sorted(bvb_tore.items(), key=lambda paar: -paar[1]):
            print(f"    {tore:>3}  {name}")


if __name__ == "__main__":
    sys.exit(main())
