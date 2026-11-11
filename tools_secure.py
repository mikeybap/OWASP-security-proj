"""
HARDENED MCP tool server (Phase 4).

Same tools as tools.py, with three defenses added. Run the same attack tests
against this version to get your "after" numbers.

Defenses here:
  1. PATH CONFINEMENT  — read_file/list_dir reject any path that resolves
     outside ./sandbox/ (kills the ../ traversal, Test C).
  2. LEAST PRIVILEGE   — fetch_text (the outbound-network tool) is removed;
     a file-summarizing agent doesn't need network access (Test D).

Run:  python tools_secure.py
"""

from pathlib import Path
from fastmcp import FastMCP

SANDBOX = (Path(__file__).parent / "sandbox").resolve()
SANDBOX.mkdir(exist_ok=True)

mcp = FastMCP("agent-security-lab-secure")


def _resolve_in_sandbox(name: str) -> Path:
    """Resolve `name` and confirm it stays inside SANDBOX, or raise."""
    target = (SANDBOX / name).resolve()
    # is_relative_to is Python 3.9+. target == SANDBOX allows the dir itself.
    if target != SANDBOX and not target.is_relative_to(SANDBOX):
        raise ValueError("path escapes the sandbox")
    return target


@mcp.tool()
def list_dir(subpath: str = ".") -> str:
    """List files inside the sandbox directory."""
    try:
        target = _resolve_in_sandbox(subpath)
    except ValueError:
        return "DENIED: path is outside the sandbox."
    if not target.exists():
        return f"(no such path: {subpath})"
    return "\n".join(sorted(p.name for p in target.iterdir()))


@mcp.tool()
def read_file(filename: str) -> str:
    """Read a text file from inside the sandbox and return its contents."""
    try:
        target = _resolve_in_sandbox(filename)
    except ValueError:
        return "DENIED: path is outside the sandbox."
    try:
        return target.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"(could not read {filename}: {e})"


# NOTE: fetch_text is intentionally GONE. Removing an unneeded capability is a
# defense in itself (least privilege) — the agent can no longer be steered into
# making outbound network calls.


if __name__ == "__main__":
    mcp.run()
