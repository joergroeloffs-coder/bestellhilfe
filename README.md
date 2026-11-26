# Bestellhilfe

Kleine Hilfe für die Wochenbestellung der Schiffsküche bei EDEKA Lück in Niebüll.

- [Bedienungsanleitung (PDF)](Bedienungsanleitung.pdf)
- Wünsche tippen oder sprechen, die App ordnet sie Artikeln aus dem Shop zu und rechnet die Summe.
- Per Lesezeichen den Warenkorb im Shop füllen. Das Handy dient nur als Mikrofon für Ideen.
- **Die App bestellt nichts.** Der Warenkorb wird im Shop geprüft und von Hand bestellt.
- Die Artikelliste mit Preisen stammt aus dem öffentlichen Shop (Stand steht oben in der App). Es sind keine persönlichen Daten enthalten. Die Einkaufsliste bleibt im Browser des Geräts gespeichert.

## Automatische Aktualisierung

Jeden Mittwoch früh (bestellt wird meist Mittwoch und Donnerstag) holt eine geplante Aufgabe in Windows auf Jörgs PC die aktuellen Angebote: `wochenlauf.ps1` holt den neuesten Stand, `aktualisieren.py` liest nur die öffentlichen Angebotsseiten (eine Anfrage alle 2 Sekunden, wie in der robots.txt des Shops verlangt), trägt sie in das Sortiment (`sortiment.json`, Stand 25.11.2026) ein und baut die App neu (`bauen.py` aus `vorlage.html`); danach wird sie hochgeladen. Der Stand steht in `stand.json`. Mehrere PCs sind möglich: Wer zuerst läuft, holt die Angebote, die anderen merken das am `stand.json` und tun nichts. Einrichten auf einem PC: `einrichten.ps1`.

Bei GitHub selbst geht das nicht, weil der Shop Anfragen von GitHub-Servern ablehnt.

Prototyp. Preise und Angebote sind eine Momentaufnahme und vor dem Bestellen im Shop zu prüfen.
