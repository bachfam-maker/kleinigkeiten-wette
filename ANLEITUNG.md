# Anleitung: von null zur laufenden Seite

Geschrieben für jemanden, der GitHub zum ersten Mal benutzt. Du brauchst keinen API-Schlüssel, keine Kreditkarte und keine Software auf dem Rechner — alles läuft im Browser. Rechne mit 20 bis 30 Minuten.

Wenn irgendwo etwas anders aussieht als beschrieben: GitHub ändert die Oberfläche gelegentlich. Die Namen der Knöpfe bleiben aber fast immer gleich, such nach dem Wort statt nach der Position.

---

## Was hier eigentlich passiert

Bevor du klickst, das Modell in vier Sätzen — damit du später weißt, wo du suchen musst, wenn etwas klemmt.

GitHub Pages kann nur fertige Dateien ausliefern. Es kann kein Programm laufen lassen, es kann nichts nachladen, es kann nicht rechnen. Deine Seite ist deshalb dumm: sie liest eine Datei namens `data.json` und zeigt an, was darin steht.

Das Rechnen übernimmt **GitHub Actions**. Das ist ein Server bei GitHub, der zu festgelegten Zeiten einen kleinen Computer hochfährt, dein Python-Skript ausführt, die Daten bei der Premier League und bei OpenLigaDB abholt, `data.json` neu schreibt und die Datei zurück ins Repository legt. Danach schaltet sich der Computer wieder ab.

Zwei getrennte Dinge also: **Actions rechnet, Pages zeigt an.** Wenn die Seite falsche Zahlen zeigt, liegt der Fehler fast immer bei Actions.

---

## Schritt 1: GitHub-Konto anlegen

Hast du schon eins, überspring das.

1. Geh auf `github.com` und klick oben rechts auf **Sign up**.
2. E-Mail, Passwort, Benutzername. Der Benutzername wird Teil deiner Webadresse — bei `hendrik-mk` heißt die Seite später `hendrik-mk.github.io/kleinigkeiten-wette`. Wähl also etwas, das du Marvin schicken magst.
3. Bestätige die E-Mail.

Das kostenlose Konto reicht vollständig aus. Actions und Pages sind für öffentliche Repositories gratis.

---

## Schritt 2: Repository anlegen

Ein Repository ist ein Projektordner mit eingebautem Änderungsprotokoll.

1. Oben rechts auf das **+** klicken, dann **New repository**.
2. **Repository name:** `kleinigkeiten-wette`
3. **Description:** kannst du leer lassen.
4. **Public** auswählen. Das ist wichtig: nur öffentliche Repositories bekommen im kostenlosen Konto unbegrenzte Actions-Minuten und Pages. Es bedeutet auch, dass Marvin jede Änderung sehen kann — bei einer Wette ist das ein Vorteil, kein Nachteil.
5. Haken bei **Add a README file** — sonst ist das Repository leer und der nächste Schritt zeigt eine andere Oberfläche.
6. **Create repository**.

---

## Schritt 3: Dateien hochladen

Du hast von mir einen Ordner mit dieser Struktur bekommen:

```
index.html                          die Seite selbst
data.json                           der aktuelle Stand (wird automatisch überschrieben)
data/manual.json                    deine BVB-Vorlagen
assets/avatars/                     die sechs Bilder
scripts/update.py                   holt die Daten und rechnet
scripts/vorlagen.py                 trägt deine Vorlagen ein
.github/workflows/aktualisieren.yml der Zeitplan
.github/workflows/vorlagen.yml      das Eingabeformular
```

**Die Ordnerstruktur muss exakt so bleiben.** `index.html` gehört direkt in die oberste Ebene, nicht in einen Unterordner. Verschiebst du Dateien, findet die Seite ihre Daten nicht mehr.

So lädst du hoch:

1. Im Repository auf **Add file** → **Upload files**.
2. Zieh den **gesamten Inhalt** des Ordners ins Browserfenster — nicht den Ordner selbst, sondern das, was drin ist. GitHub übernimmt Unterordner beim Ziehen automatisch.
3. Unten steht ein Feld für eine Beschreibung. Schreib `Erste Version` hinein.
4. **Commit changes**.

### Wenn `.github` nicht mitkommt

Ordner, deren Name mit einem Punkt beginnt, blendet Windows und macOS standardmäßig aus. Dann fehlen genau die beiden Workflow-Dateien, und nichts läuft automatisch. Prüf nach dem Upload, ob im Repository ein Ordner `.github` auftaucht.

Fehlt er, leg ihn von Hand an:

1. **Add file** → **Create new file**.
2. In das Namensfeld tippen: `.github/workflows/aktualisieren.yml` — die Schrägstriche erzeugen die Ordner automatisch.
3. Den Inhalt der Datei aus meinem Ordner hineinkopieren.
4. **Commit changes**.
5. Dasselbe noch einmal für `.github/workflows/vorlagen.yml`.

---

## Schritt 4: Actions das Schreiben erlauben

Das ist der Schritt, an dem die meisten hängenbleiben. Standardmäßig darf Actions nur lesen, nicht schreiben — und dann kann es `data.json` nicht zurücklegen.

1. Im Repository oben auf **Settings**.
2. Links in der Leiste ganz unten: **Actions** → **General**.
3. Runterscrollen bis **Workflow permissions**.
4. **Read and write permissions** auswählen.
5. **Save**.

Ohne diesen Schritt läuft der Workflow durch, scheitert aber im letzten Moment mit `Permission denied`.

---

## Schritt 5: Seite veröffentlichen

1. **Settings** → links **Pages**.
2. Unter **Source**: **Deploy from a branch**.
3. **Branch:** `main`, Ordner: `/ (root)`.
4. **Save**.

Nach ein bis zwei Minuten erscheint oben auf derselben Seite die Adresse, meist in der Form

```
https://DEINBENUTZERNAME.github.io/kleinigkeiten-wette/
```

Ruf sie auf. Du solltest die Seite mit lauter Nullen und beiden Avataren in der Knapp-Pose sehen. Die Saison hat noch nicht begonnen, das ist korrekt.

Siehst du eine 404-Meldung: warte fünf Minuten und lade neu. Der allererste Aufbau dauert manchmal länger.

---

## Schritt 6: Ersten Datenabruf starten

Jetzt prüfen wir, ob die Automatik funktioniert — ohne bis morgen früh zu warten.

1. Oben im Repository auf **Actions**.
2. Beim ersten Besuch fragt GitHub: *„Workflows aren't being run on this forked repository"* oder ähnlich, mit einem grünen Knopf. Klick ihn, um Workflows zu aktivieren.
3. Links in der Liste **Stand aktualisieren** anklicken.
4. Rechts erscheint ein grauer Kasten mit **Run workflow**. Draufklicken, dann im aufklappenden Menü noch einmal auf den grünen **Run workflow**.
5. Nach ein paar Sekunden die Seite neu laden. Es erscheint ein Eintrag mit einem gelben Punkt (läuft) und wird nach etwa einer Minute grün (fertig) oder rot (Fehler).

Klick den Eintrag an und dann auf **aktualisieren**, um die Ausgabe zu sehen. Bei Erfolg steht dort unter anderem eine Zeile wie

```
Marvin 0.0 | Hendrik 0.0 | Differenz 0.0
Chelsea 10.0 % (Modell roh: 10.0 %)
```

Wenn die Saison läuft, listet die Ausgabe außerdem **alle BVB-Torschützen mit der exakten Schreibweise auf**, die OpenLigaDB benutzt. Die brauchst du gleich.

### Wenn der Lauf rot wird

| Meldung | Ursache | Lösung |
|---|---|---|
| `Permission denied` oder `403` beim Push | Schritt 4 vergessen | Workflow permissions auf *Read and write* |
| `HTTP 404 bei .../getmatchdata/bl1/2026` | OpenLigaDB hat die Saison noch nicht angelegt | ein paar Tage warten, das passiert kurz vor Saisonstart |
| `FPL: Verein 'Liverpool' nicht gefunden` | die FPL-API ist zwischen den Saisons kurz leer | nach dem 1. Spieltag erneut versuchen |
| `Abruf fehlgeschlagen` | vorübergehende Störung | Workflow von Hand neu starten |

Wichtig: bei einem roten Lauf bleibt die alte `data.json` unverändert stehen. Ein Fehler kann die Seite also nicht kaputtmachen, sie zeigt dann nur einen veralteten Stand.

---

## Schritt 7: BVB-Vorlagen eintragen

Das ist der Teil, den du regelmäßig machst — etwa alle ein bis zwei Spieltage, zwei Minuten pro Mal.

1. **Actions** → links **Vorlagen eintragen** → **Run workflow**.
2. Vier Felder:
   - **spieler** — Name wie bei kicker.de, zum Beispiel `Julian Brandt`
   - **vorlagen** — die **Gesamtzahl der Saison**, nicht der Zuwachs. Hatte er 5 und legt eine auf: `6` eintragen, nicht `1`.
   - **spieltag** — bis zu welchem Bundesliga-Spieltag der Wert stimmt
   - **loeschen** — nur ankreuzen, wenn du einen Spieler wieder rauswerfen willst
3. **Run workflow**. Der Rest passiert allein: Eintrag speichern, neu rechnen, Seite aktualisieren.

Für jeden Spieler ein eigener Lauf. Drei Spieler = dreimal ausfüllen.

**Trag jeden BVB-Spieler mit Vorlagen ein, der in die Top 3 kommen könnte — nicht nur die aktuellen Top 3.** Ein Spieler mit null Toren und sechs Vorlagen taucht bei OpenLigaDB überhaupt nicht auf. Trägst du ihn nicht ein, existiert er für die Seite nicht, obwohl er der beste Scorer sein könnte. Die Seite sortiert dann selbst und zeigt automatisch die drei Besten an.

Wo du die Zahlen findest: `kicker.de` → Bundesliga → Statistik → Scorer, oder auf der BVB-Kaderseite von `transfermarkt.de`. Beide führen Tore und Vorlagen getrennt auf.

Vertippt? Einfach denselben Spieler noch einmal mit dem richtigen Wert eintragen. Der alte Eintrag wird überschrieben, nicht addiert.

Steht der Vorlagenstand mehr als zwei Spieltage hinter der Bundesliga zurück, blendet die Seite unten selbst einen gelben Hinweis ein. Du musst also nicht daran denken.

---

## Der laufende Betrieb

Ab jetzt macht die Seite fast alles allein.

- Zweimal täglich, um 7:10 und 23:10 deutscher Zeit, holt Actions neue Daten.
- Änderst du die Vorlagen, rechnet die Seite sofort neu — nicht erst am nächsten Morgen.
- Du kannst jederzeit von Hand nachschieben: **Actions** → **Stand aktualisieren** → **Run workflow**.

Eine Eigenheit von GitHub, die du kennen solltest: **liegt ein Repository 60 Tage lang völlig unberührt, schaltet GitHub die zeitgesteuerten Workflows ab.** Weil hier zweimal täglich ein Commit entsteht, passiert das im Saisonbetrieb nicht. In der Sommerpause schon. Vor der nächsten Saison also einmal in die Actions schauen und gegebenenfalls wieder aktivieren.

---

## Wenn Zahlen falsch aussehen

Geh in dieser Reihenfolge vor:

1. **Actions öffnen.** Ist der letzte Lauf grün? Wenn nicht, ist die Ursache dort beschrieben.
2. **`data.json` im Repository ansehen.** Stehen dort die richtigen Zahlen, die Seite zeigt aber andere? Dann ist es der Browser-Cache — mit `Strg+F5` neu laden.
3. **Stimmen die BVB-Vorlagen?** `data/manual.json` im Repository öffnen und mit kicker vergleichen.
4. **Schreibweise geprüft?** Trägst du `Brand` statt `Brandt` ein, legt das Skript einen zweiten, separaten Spieler an. In der Ausgabe des Workflows siehst du die exakten OpenLigaDB-Schreibweisen.

Und einmal im Juli, vor der nächsten Saison: `SAISON_LABEL` und `OLDB_SAISON` oben in `scripts/update.py` hochzählen, sonst holt das Skript weiter die alte Saison. Dann den Workflow einmal von Hand starten und prüfen, ob die Zahlen plausibel sind — die Premier-League-API ist inoffiziell und ändert zwischen Saisons gelegentlich Feldnamen.

---

## Wie die Chelsea-Wahrscheinlichkeit gerechnet wird

Damit du Marvin antworten kannst, wenn er fragt.

Aus der Premier-League-Tabelle wird für jeden Verein eine Punkte-pro-Spiel-Rate geschätzt, die zu Saisonbeginn stark zum Ligadurchschnitt hin gedämpft wird — sonst würde ein 3:0 am ersten Spieltag eine 114-Punkte-Saison hochrechnen. Damit werden 30.000 Saisonverläufe durchgespielt und gezählt, wie oft Chelsea oben steht.

Dieses Modellergebnis wird anschließend gegen den Startwert von 10 Prozent gemischt, gewichtet nach gespielten Spielen: nach 10 von 38 Spielen zählt das Modell zu gut einem Viertel, der Rest bleibt bei 10 Prozent. Am 38. Spieltag zählt nur noch das Modell, und das kennt dann das Ergebnis — die Anzeige landet zwangsläufig bei 0 oder 100 Prozent.

Was das Modell **nicht** kann: Verletzungen, Trainerwechsel, Restprogramm, Transfers, Europapokalbelastung. Es sieht ausschließlich Punkte und Tordifferenz. Für eine Wette unter Freunden ist das ehrlich genug, für eine Wettquote wäre es zu grob.
