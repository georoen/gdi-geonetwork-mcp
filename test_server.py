"""Run: uv run python test_server.py [--live]. No test framework required."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch
from xml.etree.ElementTree import Element

from defusedxml.common import DefusedXmlException

import server

SAMPLE = b'''<csw:GetRecordsResponse xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
 xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dct="http://purl.org/dc/terms/"
 xmlns:ows="http://www.opengis.net/ows">
 <csw:SearchResults numberOfRecordsMatched="2" numberOfRecordsReturned="1" nextRecord="2">
 <csw:Record><dc:identifier>id-1</dc:identifier><dc:title>Noise &amp; heat</dc:title>
 <dct:abstract>Example</dct:abstract><dc:subject>Noise</dc:subject>
 <dc:URI protocol="OGC:WMS">https://example.org/wms</dc:URI>
 <ows:BoundingBox crs="EPSG:4326"><ows:LowerCorner>11 48</ows:LowerCorner>
 <ows:UpperCorner>12 49</ows:UpperCorner></ows:BoundingBox>
 </csw:Record></csw:SearchResults></csw:GetRecordsResponse>'''


def offline():
    assert server.text_constraint("Lärm Ingolstadt") == "AnyText LIKE '%Lärm%' AND AnyText LIKE '%Ingolstadt%'"
    assert server.text_constraint("O'Brien") == "AnyText LIKE '%O''Brien%'"
    for call in [lambda: server.search_records(" "), lambda: server.search_records("x", 51),
                 lambda: server.search_records("x", start=0), lambda: server.get_record("")]:
        try:
            call()
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid input accepted")
    root = server.parse_xml(SAMPLE)
    with patch.object(server, "request_xml", return_value=root) as request:
        found = server.search_records("noise", limit=1, start=2)
        assert request.call_args.args == ("GetRecords",)
        assert request.call_args.kwargs["constraint"] == "AnyText LIKE '%noise%'"
        assert request.call_args.kwargs["startPosition"] == 2
        assert found["source"] == server.CSW_URL
        assert "search_mode" not in found
        assert found["matched"] == 2 and found["next_record"] == 2
        record = found["records"][0]
        assert record["title"] == "Noise & heat"
        assert record["links"][0]["url"] == "https://example.org/wms"
        assert record["bounding_boxes"][0]["lower"] == "11 48"
    details = Element("{" + server.NS["csw"] + "}GetRecordByIdResponse")
    details.append(root.find("csw:SearchResults/csw:Record", server.NS))
    with patch.object(server, "request_xml", return_value=details):
        assert server.get_record("id-1")["record"]["id"] == "id-1"
    for data, error in [
        (b'<ExceptionReport><ExceptionText>Bad filter</ExceptionText></ExceptionReport>', ValueError),
        (b'<!DOCTYPE x [<!ENTITY e "unsafe">]><x>&e;</x>', DefusedXmlException),
    ]:
        try:
            server.parse_xml(data)
        except error:
            pass
        else:
            raise AssertionError("Unsafe XML / service exception accepted")
    with patch.object(server.httpx, "Client") as client, patch.object(server, "MAX_BYTES", 2):
        response = client.return_value.__enter__.return_value.stream.return_value.__enter__.return_value
        response.iter_bytes.return_value = [b"12", b"3"]
        try:
            server.request_data(server.CSW_URL, {})
        except ValueError:
            pass
        else:
            raise AssertionError("Response size limit not enforced")
    print("PASS: validation, CQL escaping, CSW metadata/links/bbox, paging, XML safety, response size limit")


async def live():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(command=sys.executable,
        args=[str(Path(__file__).with_name("server.py"))],
        env={"CSW_URL": server.CSW_URL})
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            assert {tool.name for tool in tools} == {"search_records", "get_record"}
            assert all(tool.annotations.readOnlyHint for tool in tools)
            first = await session.call_tool("search_records", {"query": "Lärm Ingolstadt", "limit": 2})
            assert not first.isError, first.content
            result = first.structuredContent
            assert result and result["returned"] == 2 and result["matched"] >= 2
            identifier = result["records"][0]["id"]
            details = await session.call_tool("get_record", {"record_id": identifier})
            assert not details.isError, details.content
            assert details.structuredContent["record"]["id"] == identifier
            page = await session.call_tool("search_records", {
                "query": "Lärm Ingolstadt", "limit": 2, "start": result["next_record"]})
            assert not page.isError, page.content
            assert page.structuredContent["records"][0]["id"] != identifier
            bad = await session.call_tool("search_records", {"query": "noise", "limit": 0})
            assert bad.isError
            print(f"PASS: actual MCP stdio, CSW, 2 read-only tools, {result['matched']} live matches, record retrieval, pagination, tool error")
            print("Example:", result["records"][0]["title"], identifier)


if __name__ == "__main__":
    offline()
    if "--live" in sys.argv:
        asyncio.run(live())
