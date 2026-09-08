from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from mcp import Client


ROOT = Path(__file__).resolve().parents[1]


def _structured(result: object) -> dict[str, str]:
    payload = getattr(result, "structuredContent", None)
    if payload is None:
        content = getattr(result, "content", ())
        payload = json.loads(content[0].text)
    if "result" in payload and isinstance(payload["result"], dict):
        payload = payload["result"]
    return payload


def _annotations(tool: object) -> dict[str, bool]:
    value = tool.annotations
    return (
        value.model_dump(by_alias=True, exclude_none=True)
        if hasattr(value, "model_dump")
        else value
    )


class McpContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_in_memory_frozen_readonly_contract(self) -> None:
        from src.mcp_server import mcp

        async with Client(mcp, raise_exceptions=True) as client:
            listed = await client.list_tools()
            self.assertEqual([tool.name for tool in listed.tools], ["get_service_status"])
            tool = listed.tools[0]
            self.assertEqual(tool.input_schema["required"], ["user_id", "product_id"])
            self.assertEqual(
                set(tool.input_schema["properties"]), {"user_id", "product_id"}
            )
            self.assertEqual(
                _annotations(tool),
                {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False,
                },
            )

            result = await client.call_tool(
                "get_service_status",
                {"user_id": "readonly-demo", "product_id": "smart-assist"},
            )
            self.assertEqual(
                set(_structured(result)),
                {"product_id", "name", "service_status", "status_message"},
            )

            for arguments in (
                {"user_id": "unknown-demo", "product_id": "smart-assist"},
                {"user_id": "readonly-demo", "product_id": "missing-product"},
                {
                    "user_id": "readonly-demo",
                    "product_id": "smart-assist",
                    "role": "admin",
                },
            ):
                with self.subTest(arguments=arguments):
                    result = await client.call_tool("get_service_status", arguments)
                    self.assertTrue(result.is_error)
                    self.assertIsNone(result.structured_content)

    async def test_stdio_exposes_same_single_tool(self) -> None:
        from mcp import StdioServerParameters

        server = StdioServerParameters(
            command=sys.executable,
            args=[str(ROOT / "src" / "mcp_server.py")],
            cwd=str(ROOT),
        )
        async with Client(server, raise_exceptions=True) as client:
            listed = await client.list_tools()
            self.assertEqual([tool.name for tool in listed.tools], ["get_service_status"])
            result = await client.call_tool(
                "get_service_status",
                {"user_id": "readonly-demo", "product_id": "smart-assist"},
            )
            self.assertEqual(
                set(_structured(result)),
                {"product_id", "name", "service_status", "status_message"},
            )


if __name__ == "__main__":
    unittest.main()
