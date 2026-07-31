import asyncio
import logging
import sys
import os

from probe.mcp.transport.remote import ProcessTransport

logging.basicConfig(level=logging.DEBUG)

async def main():
    try:
        print(f"PATH: {os.environ.get('PATH')}")
        t = ProcessTransport('github', 'npx', ['-y', '@modelcontextprotocol/server-github'])

        print(f"Connected: {t._connected}")
        tools = await t.list_tools()
        print(f"Tools: {tools}")
        await t.close()
    except Exception as e:
        print(f"Failed: {repr(e)}")

asyncio.run(main())
