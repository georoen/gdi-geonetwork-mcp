<p align="center">
  <a href="https://jstaab.de/news/gdi-mcp/">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
      <img alt="GDI Catalogue MCP" src="assets/logo-light.svg" width="480">
    </picture>
  </a>
</p>

<h3 align="center">Geodata by prompt — Germany's geodata catalogue for AI agents</h3>

<p align="center">
  <a href="README.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-30363D?style=for-the-badge"></a>
  <a href="README.en.md"><img alt="English" src="https://img.shields.io/badge/English-2563EB?style=for-the-badge"></a>
</p>

<p align="center">
  <img alt="MCP: stdio" src="https://img.shields.io/badge/MCP-stdio-2563EB?style=for-the-badge&labelColor=555555">
  <img alt="CSW: 2.0.2" src="https://img.shields.io/badge/CSW-2.0.2-0891B2?style=for-the-badge&labelColor=555555">
  <img alt="Access: read-only" src="https://img.shields.io/badge/Access-read--only-16A34A?style=for-the-badge&labelColor=555555">
  <img alt="Python: ≥ 3.11" src="https://img.shields.io/badge/Python-%E2%89%A5_3.11-CA8A04?style=for-the-badge&labelColor=555555">
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-6E7781?style=for-the-badge&labelColor=555555">
</p>

<p align="center">
  <a href="#installation">Installation</a> · <a href="#configure-the-mcp-client">Client setup</a> · <a href="#tools">Tools</a> · <a href="#endpoint">Endpoint</a> · <a href="#tests-and-limitations">Tests</a> · <a href="#security-and-terms-of-use">Security</a> · <a href="https://jstaab.de/news/gdi-mcp/">Blog post ↗</a>
</p>

---

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
