<p align="center">
  <a href="README.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-2ea44f?style=for-the-badge"></a>
  <a href="README.en.md"><img alt="English" src="https://img.shields.io/badge/English-555555?style=for-the-badge"></a>
</p>

# GDI Catalogue MCP

Kleiner, lesender MCP-Connector für **Geodatenkatalog.de / GDI-DE**. Nutzt ausschließlich **CSW 2.0.2** mit Dublin-Core-Ausgabe und das offizielle Python-MCP-SDK über **stdio**. Kein offizieller GDI-DE-/BKG-Dienst.

## Installation

Voraussetzungen: Python ≥3.11 und [uv](https://docs.astral.sh/uv/).

Repository klonen und im Projektverzeichnis ausführen:

```bash
uv sync --frozen
uv run --frozen python test_server.py
```

`uv.lock` enthält die aufgelösten Abhängigkeiten.

## MCP-Client konfigurieren

Im MCP-Client den Python-Interpreter und das Skript mit absoluten Pfaden registrieren:

```json
{
  "mcpServers": {
    "gdi-de": {
      "command": "/absolute/path/gdi-geonetwork-mcp/.venv/bin/python",
      "args": ["/absolute/path/gdi-geonetwork-mcp/server.py"]
    }
  }
}
```

Der Client startet den Prozess über stdio; kein Docker oder Port erforderlich. Bei Verschieben des Projekts Pfade aktualisieren.

Beispielprompt:

> Suche im GDI-DE-Katalog nach Lärm in Ingolstadt. Zeig mir anschließend die Metadaten und Ressourcenlinks eines Treffers.

## Tools

| Tool | Eingaben | Ausgabe |
|---|---|---|
| `search_records` | `query`, `limit` (1–50), `start` (ab 1) | Quelle, Trefferzahl, nächste Seite, Metadaten |
| `get_record` | `record_id` aus einem Treffer | Dublin-Core-Metadaten, Themen, Rechte, Ressourcenlinks, Metadaten-Bounding-Boxes |

`search_records` nutzt CSW `GetRecords`, `get_record` nutzt `GetRecordById`. `query` ist eine Wortsuche, keine rohe CQL-Abfrage. Wörter werden per AND und `AnyText LIKE` kombiniert; CQL-Wildcards `%` und `_` bleiben wirksam. `next_record=0` bedeutet Ende.

Ressourcenlinks werden **nicht** automatisch geöffnet. Ein Metadaten-Footprint beweist keine lokale Datenabdeckung. Keine Downloads, Kartenanalyse, räumliche Suchparameter, Schreibfunktionen, Uploads oder Harvesting.

## Endpunkt

Standard: `https://gdk.gdi-de.org/gdi-de/srv/ger/csw`.

Für einen anderen CSW-Katalog `CSW_URL` in der Prozessumgebung setzen (im obigen Client-Beispiel über `env`). Die URL wird ausschließlich vom Betreiber konfiguriert, nicht als Tool-Parameter angeboten. Andere Kataloge sind nicht getestet; CSW 2.0.2 und Dublin-Core-Ausgabe müssen unterstützt werden.

## Tests und Einschränkungen

Offline-Tests prüfen Eingabevalidierung, CQL-Escaping, Metadaten, Pagination, XML-Sicherheit und Antwortgrößenlimit.

```bash
uv run --frozen python test_server.py --live
```

`--live` startet einen echten MCP-Prozess und prüft Suche, Record-Abruf, Pagination und Toolfehler; Internet nötig. Timeouts oder andere Anbieterfehler werden nicht als Erfolg gewertet.

**Livetest bestanden:** GDI-DE-CSW-Suche „Lärm Ingolstadt“ mit 17 Treffern, Record-Abruf, Pagination und Toolfehler über MCP stdio geprüft. Frühere Tests liefen zeitweise in CSW-Suchtimeouts; die Verfügbarkeit hängt vom Anbieter ab. Es gibt keinen alternativen Suchpfad oder automatischen Fallback.

## Sicherheit und Nutzungsbedingungen

HTTP-Zeitlimit 30 Sekunden, maximal 5 MiB Antwort, keine automatischen Redirects oder Wiederholungen. Sichere XML-Verarbeitung ohne DTD/Entities. Katalogfehler und ungültige Eingaben erscheinen als MCP-Toolfehler. Keine Credentials erforderlich oder gespeichert; geschützte Kataloge werden nicht unterstützt.

GDI-DE stellt die Kataloginhalte [über standardisierte Schnittstellen zur freien Verfügung](https://www.gdi-de.org/praxis-projekte/servicefunktionen/geodatenkatalog-de). Daraus folgt keine pauschale Freigabe der verlinkten Geodaten. Für deren Nutzung gelten die jeweiligen Anbieterbedingungen; Quellenvermerke und rechtliche Hinweise beachten. Leere Rechtefelder sind keine Nutzungserlaubnis.
