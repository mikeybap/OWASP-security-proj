"""
MCP tool server for the AI agent security lab.

This exposes a few small tools to a local LLM agent. In the BASELINE version
(Phases 1-2) the tools are intentionally minimal so you can observe how an
undefended agent behaves. In Phase 4 you will harden each tool and measure
the improvement.

Everything operates inside ./sandbox/ only. No real files, no credentials,
localhost only.

Run:  python tools.py
"""

from pathlib import Path
from fastmcp import FastMCP

# The one directory these tools are ever allowed to touch.
SANDBOX = Path(__file__).parent / "sandbox"
SANDBOX.mkdir(exist_ok=True)

mcp = FastMCP("agent-security-lab")


@mcp.tool()
def list_dir(subpath: str = ".") -> str:
    """List files inside the sandbox directory."""
    target = (SANDBOX / subpath)
    # NOTE (Phase 4): this does not yet confirm `target` stays inside SANDBOX.
    # Adding that check is one of your defenses — see the plan, Phase 4.
    if not target.exists():
        return f"(no such path: {subpath})"
    return "\n".join(sorted(p.name for p in target.iterdir()))


@mcp.tool()
def read_file(filename: str) -> str:
    """Read a text file from the sandbox and return its contents."""
    target = (SANDBOX / filename)
    # NOTE (Phase 4): add path-confinement here so `filename` cannot escape
    # the sandbox (e.g. via '../'). This is deliberately absent in the baseline
    # so you can demonstrate the fix with before/after test results.
    try:
        return target.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"(could not read {filename}: {e})"


@mcp.tool()
def fetch_text(url: str) -> str:
    """
    Fetch text content from a URL. In the lab, point this at LOCAL files you
    control (e.g. a file:// path or a localhost page) that contain test content.
    This is the vector you'll use to study indirect prompt injection: what
    happens when fetched *content* contains instructions?
    """
    # Kept intentionally simple for the lab. Treat all returned text as DATA.
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=5) as r:  # noqa: S310 (lab only)
            return r.read().decode("utf-8", errors="replace")[:4000]
    except Exception as e:
        return f"(could not fetch {url}: {e})"


if __name__ == "__main__":
    # stdio transport: the agent launches this server as a subprocess.
    mcp.run()
