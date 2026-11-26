"""Holt die Artikelliste (Preise, Angebote) aus dem Shop von EDEKA Lück Niebüll.

Aufruf:
  python -I shop_holen.py pruefen              -> druckt das letzte Angebotsende im Shop (kurz, 1 Seite)
  python -I shop_holen.py holen ziel.json      -> holt alle Küchen-Kategorien (rund 600 Seiten, ca. 25 Minuten)
  python -I shop_holen.py holen ziel.json Kat  -> nur Kategorien, die 'Kat' im Pfad haben (zum Testen)

Nur Standardbibliothek. Liest nur öffentliche Seiten, ohne Anmeldung. Eine Anfrage nach der anderen,
mit Pause, und mit einem klaren Namen im Anfragekopf.
"""
import html, json, os, re, sys, time, urllib.request

BASIS = "https://lueck-niebuell.edeka.shop"
KOPF = {"User-Agent": "Bestellhilfe-Preisabruf (privates Projekt, 1 Anfrage nach der anderen)"}
PAUSE = 2.0  # robots.txt des Shops: Crawl-delay 2
BILD = "https://olivia3-images.maexware-kundencloud.de/out/pictures/generated/product/1/240_240_75/"  # Bildserver des Shops
hier = os.path.dirname(os.path.abspath(__file__))


def seite(pfad, versuche=4):
    url = pfad if pfad.startswith("http") else BASIS + pfad
    for n in range(versuche):
        try:
            req = urllib.request.Request(url, headers=KOPF)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # Netz kurz weg, Shop träge: warten und neu versuchen
            if n == versuche - 1:
                raise
            time.sleep(5 * (n + 1))


def sauber(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def artikel(block, kat):
    block = block.split("</form>")[0]  # Fußtext der Seite gehört nicht zum Artikel
    m = re.search(r'<a id="productList_[^"]+" href="([^"]+)"[^>]*title="([^"]*)"', block)
    if not m:
        return None
    u = re.sub(r"[?&]force_sid=.*$", "", html.unescape(m.group(1))).replace(BASIS, "")
    t = sauber(m.group(2))
    p = re.search(r'<div class="pricewrap">.*?<span[^>]*>\s*([\d.,]+)\s*€', block, re.S)
    if not p:
        return None
    bis = re.search(r"bis\s+(\d\d\.\d\d\.\d{4})", block)
    ge = re.search(r'id="productPricePerUnit_[^"]*"[^>]*>(.*?)<div', block, re.S)
    g = re.sub(r"/\s+", "/", sauber(ge.group(1))) if ge else ""
    pf = 1 if re.search(r"Pfand", block) else 0
    bio = 1 if re.search(r'(?i)\bbio', t) else 0
    return {"t": t, "c": kat, "p": p.group(1), "g": g,
            "bis": bis.group(1) if bis else "", "kg": 0, "pf": pf, "bio": bio, "u": u}


def kategorie(pfad, kat):
    """Alle Artikel einer Kategorie, Seite für Seite (hört auf, wenn nichts Neues mehr kommt)."""
    erg, urls, pg = [], set(), 0
    while pg < 400:
        t = seite(f"{pfad}?pgNr={pg}")
        teile = t.split('<div class="listDetails">')
        bloecke = teile[1:]
        neu = []
        for k, b in enumerate(bloecke):
            a = artikel(b, kat)
            if not a or a["u"] in urls:
                continue
            # Produktbild steht direkt vor dem Artikelblock (letztes Produktbild im Stück davor)
            bilder = re.findall(r'<img[^>]+src="' + re.escape(BILD) + r'([^"]+)"', teile[k])
            a["b"] = bilder[-1] if bilder else ""
            neu.append(a)
        if not neu:
            break
        urls.update(a["u"] for a in neu)
        erg += neu
        if len(bloecke) < 16:
            break
        pg += 1
        time.sleep(PAUSE)
    return erg


def pruefen():
    """Häufigstes Angebotsende auf der ersten Angebotsseite (kurz und billig), als JJJJ-MM-TT."""
    t = seite("/Angebote/?pgNr=0")
    daten = [f"{d[6:]}-{d[3:5]}-{d[:2]}" for d in re.findall(r"bis\s+(\d\d\.\d\d\.\d{4})", t)]
    return max(set(daten), key=daten.count) if daten else ""


if __name__ == "__main__":
    wie = sys.argv[1]
    if wie == "pruefen":
        print(pruefen())
    elif wie == "holen":
        ziel = sys.argv[2]
        nur = sys.argv[3] if len(sys.argv) > 3 else ""
        kats = json.load(open(os.path.join(hier, "kategorien.json"), encoding="utf-8"))
        alle, gesehen = [], set()
        for i, pfad in enumerate(kats, 1):
            if nur and nur not in pfad:
                continue
            kat = "/".join(pfad.strip("/").split("/")[1:])
            try:
                liste = kategorie(pfad + "/", kat)
            except Exception as e:
                print("FEHLER", pfad, e, flush=True)
                continue
            neu = [a for a in liste if a["u"] not in gesehen]
            gesehen.update(a["u"] for a in neu)
            alle += neu
            print(f"{i}/{len(kats)} {pfad}: {len(neu)} Artikel (gesamt {len(alle)})", flush=True)
            time.sleep(PAUSE)
        json.dump(alle, open(ziel, "w", encoding="utf-8"), ensure_ascii=False)
        print("fertig", len(alle), "->", ziel)
