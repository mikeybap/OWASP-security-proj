# Deploying Tool-Using AI Agents: A Security Baseline

*A short memo that takes the findings from this lab and turns them into a checklist of what an
organization should have in place before putting a tool-using AI agent into production.*

## Background

AI agents are shifting from answering questions to taking actions: reading files, calling APIs,
running multi-step workflows. Most of this happens through the Model Context Protocol (MCP),
which hands a language model a set of "tools" it can invoke. The security problem that comes with
that is an old one wearing new clothes. Any component that can act can be talked into acting
against its owner.

My lab showed this on a deliberately minimal agent. Undefended, it failed all four attacks I threw
at it: it escaped its sandbox, obeyed instructions hidden in a file, let a user override its task
outright, and happily made network calls it had no reason to make. Adding a handful of targeted
controls dropped that to one. The recommendations below come straight out of which controls held
and which didn't.

## The one thing to understand first

A language model can't be trusted to enforce its own security. In my testing, the defenses I wrote
as plain code (restricting file paths, deleting an unneeded tool) worked every single time. The
defense I wrote as a firmly worded instruction in the system prompt worked against sneaky injected
content but folded the moment a user told the agent directly to ignore it. So the controls that
matter belong outside the model, at the point where it calls a tool, not inside the prompt where
they rely on the model choosing to cooperate.

## What to require

**Give each agent only the tools it needs.** Every extra capability is one more thing an attacker
can reach for. In my lab, deleting a single network tool the agent never actually needed wiped out
a whole category of risk on its own. Go through the tool list and cut anything the job doesn't
strictly require.

**Enforce boundaries in code, not in prose.** Any tool that touches files, the network, or other
resources has to check its own inputs and stay inside an allowed scope. For a file tool that means
resolving the real path and refusing anything outside the permitted directory. This is what
reliably stopped the sandbox escape. Don't count on the model to "know" where the line is.

**Treat everything the agent reads as data, never as commands.** Text that comes back from a file,
a web page, or another tool should be processed, not obeyed. Wrapping that content clearly and
telling the model it isn't authoritative measurably cut down indirect injection in my tests. It
helps, but it isn't enough by itself, which is the whole reason for the next few points.

**Authenticate the tool layer.** The MCP server should require authentication so only the intended
agent can call its tools. Unauthenticated tool servers are one of the most common weaknesses people
are finding in real deployments. My lab ran fully local, so I've flagged this as the obvious next
build rather than something I implemented.

**Put a human in front of anything consequential.** Actions that change state, move money, send
messages, or delete data should wait for a person to approve them instead of firing on their own.
That one gate caps how much damage any single bad instruction or model slip can do.

**Don't trust any single layer.** The sharpest result from the lab was that prompt-level defense
alone did not stop a directly adversarial user. Stack the model-side measures together with the
hard controls (scoping, allowlists, authentication, human approval) so that getting past one layer
doesn't hand over the whole system.

**Vet third-party tools like dependencies.** An MCP tool you pull in runs with your agent's
privileges, and it can smuggle instructions through its description or its output. Review the
source, pin the version, and limit what it can reach, the same way you'd treat any other package
you didn't write.

**Log every action.** Record each tool call and its arguments. If an agent can act without leaving
a trail, you can't investigate it when something goes wrong, and you can't prove it behaved when it
went right.

## Bottom line

Securing an agent isn't really about making the model smarter. It's about assuming it can be
fooled and limiting what it can do when it is. The pattern from the lab was consistent: the
controls that held up were the ones the model couldn't talk its way around.
