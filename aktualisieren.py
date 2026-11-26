"""Trägt die aktuellen Angebote aus dem Shop in die Bestellhilfe ein (nur Angebote, nicht das ganze Sortiment).

Ablauf:
 1. Shop fragen: Bis wann gelten die aktuellen Angebote? (1 Seite)
 2. Gleiches Datum wie beim letzten Lauf (stand.json): nichts tun.
 3. Sonst alle Angebotsseiten lesen (rund 70 Seiten, gut 6 Minuten), Angebote in das Sortiment
    (sortiment.json, bleibt unverändert) eintragen, App bauen, als index.html ablegen, stand.json schreiben.
Abgelaufene Angebote behalten ihr altes Datum; die App zeigt dann „Angebot vorbei, Preis prüfen“.

Aufruf:  python -I aktualisieren.py [--erzwingen]
Läuft jeden Mittwoch früh bei GitHub (siehe .github/workflows/preise.yml).
"""
import datetime, json, os, re, shutil, subprocess, sys

hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, hier)
import shop_holen

stand_datei = os.path.join(hier, "stand.json")
alt = json.load(open(stand_datei, encoding="utf-8")) if os.path.exists(stand_datei) else {}
heute = datetime.date.today().isoformat()

bis = shop_holen.pruefen()
print("Angebote im Shop gültig bis:", bis or "(keine gefunden)")
if not bis:
    sys.exit("Keine Angebote im Shop gefunden, nichts geändert (Shop-Seite geändert oder nicht erreichbar?).")
if "--erzwingen" not in sys.argv and alt.get("angebote_bis") == bis:
    print("Nichts Neues: gleiche Angebote wie beim letzten Lauf am", alt.get("stand"))
    sys.exit(0)

angebote = shop_holen.kategorie("/Angebote/", "Angebote")
print(len(angebote), "Angebote gelesen")
if len(angebote) < 300:
    sys.exit(f"Nur {len(angebote)} Angebote gelesen; das sieht nach einer Störung aus, nichts geändert.")


def schluessel(u):
    """Artikel-Kennung aus der Adresse: Angebote stehen unter /Angebote/<Name>.html, im Sortiment unter /<Kategorie>/<Name>.html."""
    return re.sub(r"(-EDEKA)?(-\d+)?\.html$", "", u.rsplit("/", 1)[-1])


neu = {schluessel(a["u"]): a for a in angebote}
sortiment = json.load(open(os.path.join(hier, "sortiment.json"), encoding="utf-8"))
treffer = 0
for x in sortiment:
    a = neu.get(schluessel(x["u"]))
    if a:
        x["p"], x["bis"] = a["p"], a["bis"]
        if a["g"]:
            x["g"] = a["g"]
        treffer += 1
print(treffer, "Angebote im Küchen-Sortiment eingetragen")
if treffer < 200:
    sys.exit(f"Nur {treffer} Angebote passen zum Sortiment; das sieht nach einer Störung aus, nichts geändert.")

liste = os.path.join(hier, "artikelliste_neu.json")
json.dump(sortiment, open(liste, "w", encoding="utf-8"), ensure_ascii=False)
s_datum = alt.get("sortiment", "2026-11-25")
subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(hier, "bauen.py"), liste, heute, s_datum], check=True)
shutil.copy(os.path.join(hier, "bestellhilfe.html"), os.path.join(hier, "index.html"))
os.remove(liste)
json.dump({"sortiment": s_datum, "stand": heute, "angebote_bis": bis, "angebote": len(angebote), "im_sortiment": treffer},
          open(stand_datei, "w", encoding="utf-8"), indent=1)
print("Fertig: Angebote bis", bis)
