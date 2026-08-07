# Kleinigkeiten-Wette

Scoreboard für die Saisonwette zwischen Marvin und Hendrik, Saison 2026/27.
Statische Seite auf GitHub Pages, Daten von GitHub Actions.

**Einrichtung: siehe [ANLEITUNG.md](ANLEITUNG.md).**

## Die Wetten

**Trikot-Wette** — Chelsea wird Meister. Startwahrscheinlichkeit 10 %, danach
laufend aus Tabellenstand und Restspielen neu geschätzt und gegen den
Startwert gewichtet.

**Duell-Wette** — je Seite zwei Werte:

| | Marvin | Hendrik |
|---|---|---|
| Torschütze | Guirassy (nur Tore) | Isak (nur Tore) |
| Bester Scorer | BVB, ohne Guirassy | LFC, ohne Isak |
| Liga | Bundesliga | Premier League |
| Faktor | ×1,1176 (34 → 38 Spiele) | — |

Es zählt nur der jeweils führende Scorer. Platz 2 und 3 stehen ausgegraut
zur Orientierung daneben. Vorsprung über 3 Punkte entscheidet, welcher
Avatar erscheint.

## Datenquellen

| Wert | Quelle | Schlüssel |
|---|---|---|
| PL-Spieler, PL-Tabelle | Fantasy-Premier-League-API | keiner |
| BVB-Tore, BL-Spieltag | OpenLigaDB | keiner |
| BVB-Vorlagen | `data/manual.json`, von Hand | — |

Es gibt keine kostenlose API für Bundesliga-Vorlagen. Deshalb der Hybrid.

## Aufbau

```
index.html                          Anzeige, liest data.json
data.json                           aktueller Stand, wird automatisch erzeugt
data/manual.json                    BVB-Vorlagen
scripts/update.py                   Abruf und Berechnung
scripts/vorlagen.py                 schreibt manuelle Einträge
.github/workflows/aktualisieren.yml 07:10 und 23:10 deutscher Zeit
.github/workflows/vorlagen.yml      Eingabeformular im Actions-Reiter
assets/avatars/                     sechs Zustandsbilder
```

## Vor der nächsten Saison

`SAISON_LABEL` und `OLDB_SAISON` in `scripts/update.py` hochzählen, Workflow
einmal von Hand starten, Zahlen auf Plausibilität prüfen. Die FPL-API ist
inoffiziell und ändert zwischen Saisons gelegentlich Feldnamen.
