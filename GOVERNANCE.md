# Deploying Tool-Using AI Agents: A Security Baseline

*A short governance memo accompanying the "Securing an AI Agent" lab. It generalizes the lab's
hands-on findings into requirements an organization should meet before putting a tool-using AI
agent into production.*

## Context

AI agents are moving from answering questions to taking actions — reading files, calling APIs,
executing workflows — usually through the Model Context Protocol (MCP), which exposes "tools" to
a language model. This shift reintroduces a decades-old security problem in a new form: a
component with the ability to act can be steered into acting against its owner's interests. The
accompanying lab demonstrated this empirically on a minimal local agent: out of four attacks, an
undefended agent failed all four (sandbox escape, prompt injection, and unnecessary network
access). Targeted controls reduced that to one. The requirements below follow directly from which
controls worked and which did not.

## The core principle

**A language model cannot be relied upon to enforce its own security.** In testing, defenses
written as deterministic code (restricting file paths, removing an unneeded tool) were 100%
effective; a defense written as a persuasive system-prompt instruction stopped some attacks but
not a directly adversarial input. Security controls for agents must therefore live **outside the
model**, at the boundary where the agent calls tools — not inside the prompt, where they depend
on the model's cooperation.

## Requirements

**1. Least privilege for tools.** An agent should be given only the tools its task requires.
Every additional capability is attack surface. In the lab, simply removing an unneeded network
tool eliminated an entire class of risk. Review each tool against the agent's actual job and
remove anything not strictly necessary.

**2. Enforce resource boundaries in code.** Any tool that touches files, networks, or other
resources must validate its own inputs and confine itself to an allowed scope — e.g. resolving a
real file path and rejecting anything outside a permitted directory. This is what reliably stopped
sandbox escape. Do not rely on the model to "know" not to go out of bounds.

**3. Treat all external content as untrusted data, never instructions.** Text an agent reads from
a file, a web page, or another tool must be handled as data to be processed, not as commands to be
obeyed. Clearly delimiting untrusted content and instructing the model accordingly measurably
reduced indirect prompt injection in testing. This is necessary but, on its own, not sufficient —
see requirement 6.

**4. Authenticate the tool layer.** The tool server (MCP server) should require authentication so
that only the intended agent can invoke its tools; unauthenticated tool servers are among the most
common real-world weaknesses. (Noted as future work in the lab, which ran fully local.)

**5. Require human approval for consequential actions.** Any action that changes state, moves
money, sends communications, or deletes data should pause for explicit human confirmation rather
than executing autonomously. This bounds the damage any single injection or model error can cause.

**6. Defense in depth — do not trust any single layer.** The lab's starkest result was that
prompt-level defense alone did not stop a direct adversarial user. Combine model-side measures
(untrusted-data handling) with hard controls (scoping, allowlisting, authentication, human gates)
so that one bypassed layer does not mean full compromise.

**7. Vet the tool supply chain.** Third-party MCP tools run with the agent's privileges and can
carry hidden instructions in their descriptions or outputs ("tool poisoning"). Treat adding a tool
like adding a dependency: review its source, pin versions, and limit what it can reach.

**8. Log and monitor agent actions.** Record every tool call and its arguments so that misuse is
detectable after the fact and auditable. An agent that acts without an audit trail cannot be
investigated.

## Summary

Securing an AI agent is less about making the model "smarter" and more about assuming the model
can be fooled and constraining what it is able to do when it is. Scope tools tightly, enforce
boundaries in code, treat outside text as data, authenticate the tool layer, keep a human in the
loop for anything consequential, and never depend on a single control. The empirical lesson from
the lab is simple: the controls that held were the ones the model could not talk its way past.
