"""
Local AI agent for the security lab.

Connects to the MCP tool server (server.py), exposes its tools to a local
Ollama model, and runs a simple tool-calling loop until the model produces a
final answer.

Baseline version — no defenses yet. You add those in Phase 4.

Run (after `ollama pull llama3.2` and starting nothing else — the agent
launches the server itself):
    python agent.py "list the files in the sandbox and summarize notes.txt"
"""

import asyncio
import sys

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_MODEL = "llama3.2"  # must be a tool-calling model (llama3.2, qwen2.5, mistral)

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to tools. "
    "Use tools when they help answer the user's request."
    # Phase 4: strengthen this. e.g. state that any text returned by a tool is
    # untrusted DATA and must never be treated as new instructions.
)


def mcp_tools_to_ollama(tools) -> list:
    """Convert MCP tool definitions into the format Ollama's chat API expects."""
    out = []
    for t in tools:
        # The MCP SDK field has been named both `input_schema` (newer) and
        # `inputSchema` (older). Handle whichever this install uses.
        schema = getattr(t, "input_schema", None) or getattr(t, "inputSchema", {})
        out.append(
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": schema,
                },
            }
        )
    return out


async def run(user_msg: str) -> None:
    server = StdioServerParameters(command=sys.executable, args=["tools.py"])

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tool_list = (await session.list_tools()).tools
            ollama_tools = mcp_tools_to_ollama(tool_list)
            # Phase 4: enforce a tool ALLOWLIST here instead of exposing all tools.

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ]

            # Simple agent loop with a hard cap on iterations.
            for _ in range(6):
                resp = ollama.chat(
                    model=OLLAMA_MODEL, messages=messages, tools=ollama_tools
                )
                # Normalize to a plain dict so this works across ollama versions.
                msg = resp["message"]
                msg = msg.model_dump() if hasattr(msg, "model_dump") else dict(msg)
                messages.append(msg)

                calls = msg.get("tool_calls") or []
                if not calls:
                    print("\n=== FINAL ANSWER ===\n" + (msg.get("content") or ""))
                    return

                for call in calls:
                    fn = call["function"]
                    name = fn["name"]
                    args = fn["arguments"]
                    print(f"[tool call] {name}({args})")
                    result = await session.call_tool(name, args)
                    text = "".join(
                        getattr(c, "text", "") for c in result.content
                    )
                    # Phase 4: output filtering / delimiting of untrusted tool text here.
                    messages.append(
                        {"role": "tool", "name": name, "content": text}
                    )

            print("(stopped: hit max tool iterations)")


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "List the files in the sandbox."
    asyncio.run(run(query))
