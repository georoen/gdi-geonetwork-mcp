"""Read-only CSW 2.0.2 tools. MCP uses stdio; never print to stdout."""

import os
from urllib.parse import urlsplit
from typing import Any

import httpx
from defusedxml import ElementTree as XML
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

CSW_URL = os.environ.get("CSW_URL", "https://gdk.gdi-de.org/gdi-de/srv/ger/csw")
url = urlsplit(CSW_URL)
if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password or url.fragment:
    raise ValueError("CSW_URL must be an HTTP(S) endpoint without credentials or fragment")

MAX_BYTES = 5 * 1024 * 1024
NS = {
    "csw": "http://www.opengis.net/cat/csw/2.0.2",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dct": "http://purl.org/dc/terms/",
    "ows": "http://www.opengis.net/ows",
}
mcp = FastMCP(
    "GDI Catalogue",
    instructions="Read-only CSW metadata tools. Results are metadata, not downloaded data. Resource links are not fetched or verified.",
)
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)


def parse_xml(data: bytes):
    root = XML.fromstring(data, forbid_dtd=True)
    if root.tag.rsplit("}", 1)[-1] in {"ExceptionReport", "ServiceExceptionReport"}:
        raise ValueError("CSW error: " + " ".join(root.itertext()).strip()[:1000])
    return root


def request_data(endpoint: str, params: dict) -> bytes:
    # Endpoints come from operator configuration, never from tool callers.
    # No automatic redirects, resource downloads, writes, or harvest operations.
    with httpx.Client(timeout=30, follow_redirects=False) as client:
        with client.stream("GET", endpoint, params=params) as response:
            response.raise_for_status()
            data = bytearray()
            for chunk in response.iter_bytes(65536):
                if len(data) + len(chunk) > MAX_BYTES:
                    raise ValueError("Catalogue response exceeds 5 MiB; reduce search limit")
                data.extend(chunk)
    return bytes(data)


def request_xml(operation: str, **params):
    params = {
        "service": "CSW", "version": "2.0.2", "request": operation,
        "outputSchema": NS["csw"], "elementSetName": "full", **params,
    }
    return parse_xml(request_data(CSW_URL, params))


def record_summary(record):
    def values(path):
        return [text for node in record.findall(path, NS) if (text := "".join(node.itertext()).strip())]

    links = []
    for tag in ("dc:URI", "dct:references"):
        for node in record.findall(tag, NS):
            if node.text and node.text.strip():
                links.append({"url": node.text.strip(), **node.attrib})
    boxes = []
    for box in record.findall("ows:BoundingBox", NS) + record.findall("ows:WGS84BoundingBox", NS):
        boxes.append({
            "crs": box.get("crs"),
            "lower": box.findtext("ows:LowerCorner", namespaces=NS),
            "upper": box.findtext("ows:UpperCorner", namespaces=NS),
        })
    return {
        "id": record.findtext("dc:identifier", default="", namespaces=NS),
        "title": record.findtext("dc:title", default="", namespaces=NS),
        "abstract": record.findtext("dct:abstract", default="", namespaces=NS),
        "types": values("dc:type"), "subjects": values("dc:subject"),
        "formats": values("dc:format"), "dates": values("dc:date"),
        "rights": values("dc:rights") + values("dct:accessRights"),
        "links": links, "bounding_boxes": boxes,
    }


def text_constraint(query: str):
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 500:
        raise ValueError("query must contain 1–500 characters")
    # CQL string literals escape apostrophes by doubling them. No raw CQL accepted.
    return " AND ".join("AnyText LIKE '%" + term.replace("'", "''") + "%'" for term in query.split())


@mcp.tool(annotations=READ_ONLY)
def search_records(query: str, limit: int = 10, start: int = 1) -> dict[str, Any]:
    """Search CSW metadata with words (e.g. 'Lärm Ingolstadt'), not raw CQL. limit 1–50, start is 1-based. Use next_record to paginate; zero means end. Call get_record for metadata and links."""
    constraint = text_constraint(query)
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError("limit must be an integer between 1 and 50")
    if type(start) is not int or start < 1:
        raise ValueError("start must be an integer >= 1")
    root = request_xml(
        "GetRecords", typeNames="csw:Record", resultType="results", maxRecords=limit,
        startPosition=start, constraintLanguage="CQL_TEXT",
        constraint_language_version="1.1.0", constraint=constraint,
    )
    results = root.find("csw:SearchResults", NS)
    if results is None:
        raise ValueError("CSW response has no SearchResults")
    return {
        "source": CSW_URL, "query": query,
        "matched": int(results.attrib["numberOfRecordsMatched"]),
        "returned": int(results.attrib["numberOfRecordsReturned"]),
        "next_record": int(results.attrib.get("nextRecord", "0")),
        "records": [record_summary(record) for record in results],
    }


@mcp.tool(annotations=READ_ONLY)
def get_record(record_id: str) -> dict[str, Any]:
    """Retrieve a record's Dublin Core metadata, resource links and metadata bounding boxes by its exact returned ID. Links are not verified/downloaded; a footprint does not prove local data coverage."""
    if not isinstance(record_id, str) or not 1 <= len(record_id.strip()) <= 250:
        raise ValueError("record_id must contain 1–250 characters")
    root = request_xml("GetRecordById", id=record_id.strip())
    record = root.find("csw:Record", NS)
    if record is None:
        raise ValueError("Record not found or unsupported CSW record schema")
    return {"source": CSW_URL, "record": record_summary(record)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
