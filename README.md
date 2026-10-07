# GDI Catalogue MCP

<details name="lang" open>
<summary><b>🇩🇪 Deutsch</b></summary>

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

</details>

<details name="lang">
<summary><b>🇬🇧 English</b></summary>

Small, read-only MCP connector for **Geodatenkatalog.de / GDI-DE**. Uses only **CSW 2.0.2** with Dublin Core output and the official Python MCP SDK over **stdio**. Not an official GDI-DE/BKG service.

## Installation

Requirements: Python ≥3.11 and [uv](https://docs.astral.sh/uv/).

Clone the repository and run in the project directory:

```bash
uv sync --frozen
uv run --frozen python test_server.py
```

`uv.lock` contains the resolved dependencies.

## Configure the MCP client

Register the Python interpreter and the script in the MCP client using absolute paths:

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

The client starts the process over stdio; no Docker or port required. Update the paths if you move the project.

Example prompt:

> Search the GDI-DE catalogue for noise in Ingolstadt. Then show me the metadata and resource links of one result.

## Tools

| Tool | Inputs | Output |
|---|---|---|
| `search_records` | `query`, `limit` (1–50), `start` (from 1) | Source, match count, next page, metadata |
| `get_record` | `record_id` from a search result | Dublin Core metadata, subjects, rights, resource links, metadata bounding boxes |

`search_records` uses CSW `GetRecords`, `get_record` uses `GetRecordById`. `query` is a word search, not a raw CQL query. Words are combined with AND and `AnyText LIKE`; the CQL wildcards `%` and `_` remain active. `next_record=0` means end of results.

Resource links are **not** opened automatically. A metadata footprint does not prove local data coverage. No downloads, map analysis, spatial search parameters, write functions, uploads or harvesting.

## Endpoint

Default: `https://gdk.gdi-de.org/gdi-de/srv/ger/csw`.

For a different CSW catalogue, set `CSW_URL` in the process environment (via `env` in the client example above). The URL is configured only by the operator and is not offered as a tool parameter. Other catalogues are untested; they must support CSW 2.0.2 and Dublin Core output.

## Tests and limitations

Offline tests check input validation, CQL escaping, metadata, pagination, XML safety and the response size limit.

```bash
uv run --frozen python test_server.py --live
```

`--live` starts a real MCP process and checks search, record retrieval, pagination and tool errors; requires internet. Timeouts or other provider errors are not counted as success.

**Live test passed:** GDI-DE CSW search "Lärm Ingolstadt" (noise Ingolstadt) with 17 results, record retrieval, pagination and tool errors verified over MCP stdio. Earlier tests occasionally ran into CSW search timeouts; availability depends on the provider. There is no alternative search path or automatic fallback.

## Security and terms of use

HTTP timeout of 30 seconds, maximum 5 MiB response, no automatic redirects or retries. Safe XML processing without DTDs/entities. Catalogue errors and invalid inputs are reported as MCP tool errors. No credentials required or stored; protected catalogues are not supported.

GDI-DE makes the catalogue contents [freely available via standardised interfaces](https://www.gdi-de.org/praxis-projekte/servicefunktionen/geodatenkatalog-de). This does not imply a blanket licence for the linked geodata. Their use is governed by the respective provider's terms; observe attributions and legal notices. Empty rights fields do not grant permission to use the data.

</details>
