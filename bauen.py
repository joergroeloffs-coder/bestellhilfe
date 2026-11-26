"""Baut bestellhilfe.html aus vorlage.html und einer Artikelliste (JSON).

Aufruf:  python -I bauen.py "<Artikelliste.json>" [Stand JJJJ-MM-TT]
Die Artikelliste stammt aus dem Shop-Lauf (secondbrain/raw/EDEKA Lück Artikelliste ...json).
"""
import json, re, sys, os

hier = os.path.dirname(os.path.abspath(__file__))
quelle = sys.argv[1]
stand = sys.argv[2] if len(sys.argv) > 2 else re.search(r"\d{4}-\d\d-\d\d", quelle).group(0)
sortiment = sys.argv[3] if len(sys.argv) > 3 else stand  # Tag, an dem das ganze Sortiment gelesen wurde

roh = json.load(open(quelle, encoding="utf-8"))

def sauber(s):
    return re.sub(r"\s+", " ", s).strip()

def bis_iso(s):
    m = re.match(r"(\d\d)\.(\d\d)\.(\d{4})", s or "")
    return f"{m.group(1)}.{m.group(2)}.{m.group(3)}" if m else ""

def zahl(s):
    return float(s.replace(".", "").replace(",", "."))

items = []
for x in roh:
    p = zahl(x["p"])
    g = x["g"].strip()
    gk = 0
    m = re.match(r"([\d.,]+)\s*€\s*/\s*(kg|l)", g)
    if m:
        gk = zahl(m.group(1))
    # Preis pro 100 g (Theke/Gewichtsware): Preis*10 entspricht dem Kilopreis
    # Theke/Gewichtsware: Preis steht pro 100 g (Preis*10 = Kilopreis). Packung mit genau 100 g ist ein Stückpreis.
    wm = re.search(r"(\d+(?:,\d+)?)\s*(kg|g)\b", x["t"])
    w_kg = (zahl(wm.group(1)) / (1000 if wm.group(2) == "g" else 1)) if wm else None
    per100 = bool(m and m.group(2) == "kg" and gk and abs(p * 10 - gk) < 0.2 and p < 4.0
                  and not (w_kg is not None and abs(w_kg - 0.1) < 0.001))
    fl = (1 if per100 else 0) | (2 if x["bio"] else 0) | (4 if x["pf"] else 0)
    it = [sauber(x["t"]), x["c"], p, g, bis_iso(x["bis"]), fl, x["u"]]
    if x.get("b"):
        it.append(x["b"])  # Produktbild (Dateiname auf dem Bildserver des Shops)
    items.append(it)

# Stammartikel NUR aus echten Rechnungen (bisher: 15.07., 02.09., 16.09., 18.11.2026; siehe Wiki 'Rechnungsvergleich 2026'): Name, Menge, Suchmuster.
# Beispiel-Warenkörbe der KI zählen nicht (Jörg, 2026-11-25). Weitere Rechnungen hier ergänzen.
# Wo ein Artikel im Shop nicht mehr existiert, steht ein Ersatzartikel (Kartoffeln, Skyr).
STAMM = [
    ("Vollmilch (H-Milch 1 l)", 12, r"^GUT&GÜNSTIG H-Vollmilch 1 l$"),
    ("Eier 10 Stück", 10, r"^GUT&GÜNSTIG Eier aus Bodenhaltung 10"),
    ("Butter 250 g", 6, r"^GUT&GÜNSTIG Deutsche Markenbutter 250"),
    ("Speisequark 500 g", 6, r"^GUT&GÜNSTIG Speisequark Magerstufe 500g"),
    ("Skyr Natur 500 g", 4, r"^EDEKA Herzstücke Skyr Natur Laktosefrei 500"),
    ("Joghurt mild", 1, r"^GUT&GÜNSTIG Fettarmer Joghurt mild 500"),
    ("Käseaufschnitt", 5, r"^GUT&GÜNSTIG Käseaufschnitt 250"),
    ("Hinterkochschinken", 4, r"^GUT&GÜNSTIG Hinterkochschinken 200"),
    ("Salami", 2, r"^GUT&GÜNSTIG Salami 200"),
    ("Geflügel-Fleischwurst", 1, r"^GUT&GÜNSTIG Geflügel-Fleischwurst 500"),
    ("Hackfleisch gemischt (kg)", 2, r"^Gutfleisch Gemischtes Hackfleisch 1 kg"),
    ("Hähnchen-Geschnetzeltes", 4, r"^GUT&GÜNSTIG Hähnchen Geschnetzeltes 400"),
    ("Hähnchen-Minutenschnitzel", 3, r"^GUT&GÜNSTIG Hähnchen Minutenschnitzel 400"),
    ("Pangasiusfilet", 4, r"^GUT&GÜNSTIG Pangasiusfilets 475"),
    ("Kartoffeln festkochend 2,5 kg", 12, r"^GUT&GÜNSTIG Kartoffeln vorwiegend festkochend 2,5kg"),
    ("Zwiebeln 2 kg", 1, r"^GUT&GÜNSTIG Zwiebeln Klasse\s*II 2kg"),
    ("Salatgurken", 3, r"^GUT&GÜNSTIG Salatgurken Klasse\s*I$"),
    ("Eisbergsalat", 2, r"^GUT&GÜNSTIG Eisbergsalat"),
    ("Champignons 400 g", 3, r"^GUT&GÜNSTIG Champignons"),
    ("Blattspinat 1 kg", 2, r"^GUT&GÜNSTIG Blattspinat 1000"),
    ("Apfelrotkohl", 4, r"^GUT&GÜNSTIG Apfelrotkohl 400"),
    ("Sauerkraut", 5, r"^GUT&GÜNSTIG Wein-Sauerkraut 520"),
    ("Passierte Tomaten", 4, r"^GUT&GÜNSTIG Tomaten, passiert"),
    ("Bananen (Stück; zuletzt 2,6 kg)", 20, r"^EDEKA Bananen$"),
    ("Spaghetti 500 g", 4, r"^EDEKA Herzstücke Spaghetti 500"),
    ("Reis 1 kg", 1, r"^ORYZA Ideal-Reis 1 kg"),
    ("Weizenmischbrot", 2, r"^GUT&GÜNSTIG Weizenmischbrot 500"),
    ("Buttertoast", 2, r"^GUT&GÜNSTIG Buttertoast 500"),
    ("Rapsöl 1 l", 2, r"^GUT&GÜNSTIG Pflanzenöl aus Raps 1 l"),
    ("Zucker", 1, r"^GUT&GÜNSTIG Feiner Zucker"),
    ("Jodsalz", 1, r"^GUT&GÜNSTIG Jodsalz"),
    ("Kaffee Bohnen 1 kg", 2, r"^Tchibo Caff. Crema Vollmundig ganze Bohnen 1"),
    ("Katenschinken 200 g", 2, r"^Abraham Katenschinken geräuchert 200"),
    ("Französischer Weichkäse", 2, r"^GUT&GÜNSTIG Französischer Weichkäse"),
    ("Frischkäse Pur 300 g", 2, r"^GUT&GÜNSTIG Frischkäse Pur"),
    ("Hirtenkäse", 1, r"^GUT&GÜNSTIG Hirtenkäse"),
    ("Geflügelsalat", 2, r"^EDEKA Herzstücke Feinster Geflügelsalat"),
    ("Fruchtjoghurt 1 kg", 1, r"^Weideglück Fruchtjoghurt mild Pfirsich"),
    ("Shrimps Dillsauce", 2, r"^GUT&GÜNSTIG Shrimps in Dillsauce"),
    ("Shrimps Knoblauchsauce", 2, r"^GUT&GÜNSTIG Shrimps in Knoblauchsauce"),
    ("Schinkenwürfel", 1, r"^GUT&GÜNSTIG Schinkenwürfel"),
    ("Wiener Würstchen", 2, r"^GUT&GÜNSTIG Wiener Würstchen"),
    ("Sonnenblumenkernbrot", 2, r"^GUT&GÜNSTIG Sonnenblumenkernbrot"),
    ("Mehrkornbrot", 2, r"^GUT&GÜNSTIG Mehrkornbrot"),
    ("Tortilla-Wraps", 3, r"^GUT&GÜNSTIG Tortilla-Weizen-Wraps"),
    ("Salatmayonnaise", 2, r"^GUT&GÜNSTIG Salatmayonnaise"),
    ("Röstzwiebeln", 1, r"^GUT&GÜNSTIG Röstzwiebeln"),
    ("Paniermehl", 1, r"^Leimer Paniermehl"),
]
stamm = []
for name, m, mu in STAMM:
    hit = next((i for i, it in enumerate(items) if re.search(mu, it[0], re.I)), None)
    if hit is None:
        print("NICHT GEFUNDEN:", name)
    else:
        stamm.append({"k": name, "i": hit, "m": m})

daten = {"stand": stand, "sortiment": sortiment, "basis": "https://lueck-niebuell.edeka.shop",
         "bild": "https://olivia3-images.maexware-kundencloud.de/out/pictures/generated/product/1/240_240_75/", "items": items, "stamm": stamm}
vorlage = open(os.path.join(hier, "vorlage.html"), encoding="utf-8").read()
js = json.dumps(daten, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
ziel = os.path.join(hier, "bestellhilfe.html")
open(ziel, "w", encoding="utf-8").write(vorlage.replace("__DATEN__", js))
print(len(items), "Artikel,", len(stamm), "Stammartikel,", sum(1 for i in items if i[5] & 1), "nach Gewicht,",
      sum(1 for i in items if i[4]), "Angebote ->", ziel, round(os.path.getsize(ziel) / 1e6, 2), "MB")
