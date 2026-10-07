# Jason Vaughan projects: fit for NUIAK, TTR, and Big Dog

Research date: 2026-10-06, America/Los_Angeles.

## Decision summary

**Evaluate TangleClaw first, but do not replace our current coordination system yet.**

TangleClaw addresses our problems with agent sessions, shared context, and work visibility. It also introduces powerful execution and Git features.
Those features need limits before we connect our repositories.

TangleBrain deserves a smaller, separate trial for local language-model routing. It does not schedule PyTorch training or improve focus classification directly.

PortHub offers a useful port-management idea. Its standalone server needs security changes and real tests before use.

Medusa has relevant messaging features. Its inspected authentication design does not meet our requirements for separate worker identities and protected requests.

The private UCI project may offer useful lessons for human review and feedback. Public evidence does not support adoption or an integration estimate.

No project receives approval for installation, network exposure, repository access, or private data through this document.

### Recommended order

| Priority | Project or action | Potential benefit | Decision |
|---|---|---|---|
| 1 | TangleClaw, isolated trial | Less manual coordination and better session visibility | Test with a disposable repository and fake jobs |
| 2 | Ask Jason about UCI and operational failures | Better review records, recovery rules, and measured readiness | Request examples and contracts, not a deployment |
| 3 | TangleBrain, local trial | Route suitable text tasks to existing local models | Measure accepted results and total cost |
| 4 | PortHub design review | Fewer port conflicts | Borrow the design only after security and test changes |
| 5 | Medusa protocol review | Cross-agent messaging | Resolve identity, request integrity, and replay risks first |
| Defer | ClawBridge | Remote access to Claude Code sessions | Poor fit for our current Codex-based plan |
| Do not adopt now | Archived tools and unrelated products | Little benefit to current model work | Keep as references only |

## Scope and evidence limits

The review covers all 23 public repositories returned by Jason's GitHub API during this review.
It also covers named products, agents, skills, and infrastructure on the website.
Some entries describe the same product in different forms.
This inventory cannot cover unpublished private work.

Sources include the [website](https://www.jasonvaughan.com/), its source, public repository files, release records, and recent workflow records.
The [public repository inventory](https://api.github.com/users/Jason-Vaughan/repos?per_page=100) provides repository status and license metadata.

The review uses 3 evidence levels:

- **Inspected:** source or metadata supports the statement.
- **Reported:** Jason's documentation describes the feature or result.
- **Estimated:** this review predicts effort or benefit for our workflow.

I inspected selected implementation files for the most relevant tools. I did not perform a complete security audit.
I did not install dependencies, start these services, run their tests, or connect them to our machines.
Recent successful CI does not prove security or compatibility with our workflow.
Marketing statistics do not establish independent adoption, correctness, or savings.

Some UTC records have a 2026-10-07 date during this local 2026-10-06 review.
The commit references below identify the inspected versions.

## Effort scale

LOE means level of effort. Estimates use focused engineer-days, not elapsed calendar days.
They include implementation, tests, and a short handoff. They exclude upstream fixes, waiting, and unrelated infrastructure.

- **Review:** read source and resolve a specific question.
- **Trial:** test one isolated workflow without real credentials or production authority.
- **Integration:** connect the tool to our existing contracts and verify failure cases.

Estimates have medium or low confidence. No runtime measurements support them yet.
For unrelated or private products, “not estimated” is intentional. A number would imply a defined integration that does not exist.

## Public repository inventory

### Coordination and developer tools

| Project | What it does | Maturity evidence | Fit and main limit | Estimated effort |
|---|---|---|---|---|
| [TangleClaw](https://github.com/Jason-Vaughan/TangleClaw) | Runs persistent coding sessions with roles, dashboards, messages, and project controls | Active source; v5.31.0 release; successful test workflow at inspected commit | High fit for Mac coordination. macOS requirement and broad execution features need controls | Trial: 2–4 days. Integration: 10–20+ days |
| [TangleBrain](https://github.com/Jason-Vaughan/TangleBrain) | Routes text requests across local and hosted model backends | v0.25.0 release; recent successful CI, not at the inspected commit | Medium fit for text work. Not a GPU training scheduler | Trial: 1–2 days. Integration: 3–7 days |
| [Medusa](https://github.com/Jason-Vaughan/Medusa) | Connects agents through MCP, messaging, and peer coordination | Release name v1.0.0-rc2; website calls it beta | Relevant concept. Current authentication is insufficient for our worker controls | Review: 1–2 days. Integration: 5–10+ days after fixes |
| [PortHub](https://github.com/Jason-Vaughan/PortHub) | Tracks ports through leases, a daemon, and a dashboard | Package v0.1.1; no GitHub release found; test commands are placeholders | Useful local idea. Network API and missing tests prevent direct adoption | Trial: 0.5–1 day. Hardened local integration: 3–6 days |
| [ClawBridge](https://github.com/Jason-Vaughan/ClawBridge) | Exposes Claude Code terminal sessions and permission prompts through HTTP | v2.0.1 release; implementation and security design available | Low fit for current Codex work. Adds another execution interface | Review: 1 day. Integration: 5–10+ days if a need appears |
| [prawduct](https://github.com/Jason-Vaughan/prawduct) | Provides a planning and review workflow for coding agents | Public fork of brookstalley/prawduct | Borrow selected checks. Do not add a second task authority | Review: 0.5–1 day. Selective adaptation: 1–2 days |
| [CLiTS](https://github.com/Jason-Vaughan/CLiTS) | Collects Chrome diagnostic information | Archived; README recommends newer browser tooling | Low fit. It does not provide native UIKit labels | No adoption. Reference review: 0.5 day |
| [refuctor](https://github.com/Jason-Vaughan/refuctor) | Tracks technical debt with a developer interface | Archived | Duplicates our task queue without solving model problems | No adoption. Reference review: 0.5 day |

### Applications and integrations

| Project | What it does | Maturity evidence | Fit and main limit | Estimated effort |
|---|---|---|---|---|
| [ScrapeGoat](https://github.com/Jason-Vaughan/ScrapeGoat) | Converts PDF information into calendar events | README labels v0.7.0 beta and warns about production readiness | Low fit. Review UI ideas may help; AI processing adds an external data path | Review: 0.5–1 day. No integration proposed |
| [notse-releases](https://github.com/Jason-Vaughan/notse-releases) | Distributes Notse, a network teleprompter for presentation notes | Downloadable commercial releases; implementation is not public here | Low fit. Binary availability does not permit a source security review | Not estimated |
| [TiLT-showcase](https://github.com/Jason-Vaughan/TiLT-showcase) | Describes time and pay tracking for IATSE contracts | Website reports a live commercial product | Audit-trail ideas may help. Showcase is not reusable application source | Review: 0.5 day. Integration not estimated |
| [cierre-sensei](https://github.com/Jason-Vaughan/cierre-sensei) | Supplies reference data for Mexican closing-cost assistance | Public data repository; website also describes a web product | No model-training fit. Public data is not the full product | No integration proposed |
| [CasaJirafa-Website](https://github.com/Jason-Vaughan/CasaJirafa-Website) | Implements a property website with Next.js | Recent source; template-style README; test command exists | Low fit. Useful only as a web UI reference | No integration proposed |
| [openclaw-ebay-research](https://github.com/Jason-Vaughan/openclaw-ebay-research) | Reads eBay listings and market information | Public plugin source and README | Not relevant to native focus work. API credentials still require protection | No integration proposed |
| [openclaw-ebay-seller](https://github.com/Jason-Vaughan/openclaw-ebay-seller) | Reads inventory and supports listing changes with approval steps | Public plugin; documentation describes a 2-step write gate | Approval design may help. Do not connect a seller account for this research | Review: 0.5 day. No integration proposed |
| [openclaw-google-oauth](https://github.com/Jason-Vaughan/openclaw-google-oauth) | Gives agents direct Google Workspace access | Public plugin source; documented OAuth setup | Not needed for SMB coordination. Broad account access adds risk | No integration proposed |
| [clock8002](https://github.com/Jason-Vaughan/clock8002) | Runs an OSC-controlled HDMI clock on Raspberry Pi hardware | Public fork; platform-specific implementation | Low fit. It is not an Apple UI generator or worker scheduler | No integration proposed |

### Supporting repositories

| Repository | Purpose | Relevance and limits | Estimated effort |
|---|---|---|---|
| [.github](https://github.com/Jason-Vaughan/.github) | Shared community and project guidance | Reference only. Our repository rules remain authoritative | Review: 0.5 day at most |
| [Jason-Vaughan](https://github.com/Jason-Vaughan/Jason-Vaughan) | Profile information | Discovery source, not an executable tool | None |
| [jasonvaughan.com](https://github.com/Jason-Vaughan/jasonvaughan.com) | Portfolio application and project catalog | Primary inventory source. Product claims still need verification | Completed in this review |
| [project-assets](https://github.com/Jason-Vaughan/project-assets) | Logos, screenshots, and published project statistics | Not an approved training corpus. Asset reuse rights remain unresolved | Rights review required before any reuse |
| [barcoach-assets](https://github.com/Jason-Vaughan/barcoach-assets) | Assets and references for BarCoach | Not a native UI dataset. Referenced manuals can have separate rights | No integration proposed |
| [volta-stats](https://github.com/Jason-Vaughan/volta-stats) | Publishes operational statistics for Volta | Useful reporting example. Statistics are self-reported | Review: 0.5 day |

## Other products and systems on the website

These entries extend the repository inventory. Public descriptions do not establish reusable code or deployment readiness.

| Name | Published purpose and state | Relevance | Feasibility and next check |
|---|---|---|---|
| UCI: Unified Comms Intelligence | In development. Reviews draft replies across communication channels and records human corrections | High conceptual fit for case review and feedback | Ask for schemas, calibration methods, and failure records. Integration effort is unknown |
| Monad-1 | Local GPU inference infrastructure for Jason's agents | Useful example for resource accounting and worker reporting | Hardware differs from Big Dog. Review configurations before estimating reuse |
| Volta | Experimental orchestration on Monad-1; project details remain private | Coordination and operational reporting may help | Ask for job contracts and recovery evidence. Public statistics are not enough |
| TiLTClaw | Reported production support agent for TiLT, accessed through a private Discord app | Escalation and review patterns may help | Ask for redacted examples. No public implementation assessment |
| RentalClaw | Private-beta rental management agent | Low direct fit; approval patterns may help | No adoption proposal |
| Kobold | Private video-engineering assistant with voice and hardware control | Low direct fit; edge-worker design may help | “Offline” operation needs clarification when inference uses another machine |
| Google Workspace Operator | Published skill for Workspace tools | No current need | Inspect exact package and permissions only if a need appears |
| Airbnb Gateway | Published skill for guarded rental operations | Low fit | Do not grant account access for a coordination experiment |
| DecomTangle | Published skill that separates procedures into individual observable tool actions | Potential value for precise failure reporting | Review: 0.5 day. Preserve batch jobs; do not add a model turn for every trivial action |
| BarCoach | Custom GPT for Barco Event Master guidance | Example of domain reference access, not focus detection | No integration proposed |
| BarCoach Gen 2 | Beta GPT using external reference material | Reference-version management may help | Review references and rights before reuse |
| Cierre Sensei GPT | Original closing-cost assistant, preceding the web product | No direct fit | No integration proposed |
| En-Genius4Dummies | GPT for an EnGenius access point | No direct fit | No integration proposed |
| LensJester | GPT for projector lens recommendations | No direct fit | No integration proposed |

Sources: [pipeline](https://github.com/Jason-Vaughan/jasonvaughan.com/blob/0820cc90ac48d53925c5d908c01ebbc24cd4f8ba/src/components/Pipeline.jsx),
[agent catalog](https://github.com/Jason-Vaughan/jasonvaughan.com/blob/0820cc90ac48d53925c5d908c01ebbc24cd4f8ba/src/components/OpenClawFleet.jsx),
[skills catalog](https://github.com/Jason-Vaughan/jasonvaughan.com/blob/0820cc90ac48d53925c5d908c01ebbc24cd4f8ba/src/components/ClawHub.jsx),
[GPT catalog](https://github.com/Jason-Vaughan/jasonvaughan.com/blob/0820cc90ac48d53925c5d908c01ebbc24cd4f8ba/src/components/GPTs.jsx),
and [infrastructure](https://github.com/Jason-Vaughan/jasonvaughan.com/blob/0820cc90ac48d53925c5d908c01ebbc24cd4f8ba/src/components/Infrastructure.jsx).

## Detailed assessments

### TangleClaw: strongest candidate, with important boundaries

TangleClaw combines persistent terminal sessions, project roles, shared documents, and agent messages.
It includes a Medusa switchboard and PortHub integration. These integrations are not proof that standalone versions have identical security behavior.

This could reduce manual handoffs between NUIAK and TTR on a Mac.
Its macOS and launchd requirements prevent treating it as a direct Linux replacement for Big Dog's worker.

The inspected security documentation describes loopback defaults and password-based sessions.
The control-route source distinguishes verified sessions from operator requests without verified identity.
These are useful controls, not evidence of unrestricted anonymous access by default.

Important limits remain:

- Accounts do not have separate permission levels in the documented model.
- The optional machine token is shared, rather than scoped to each worker.
- Token handling includes sensitive configuration and database storage.
- Local processes form part of the trust boundary.
- Agent modes include broad permission options that we should not enable.
- Git automation conflicts with our prohibition on agent Git writes.
- Generated guidance can conflict with our repository instructions.
- Upload secret scanning reports findings but does not guarantee blocking or redaction.
- Stored transcripts can contain private prompts, paths, or credentials.

The source includes stronger checks for control routes. We should not reduce its security assessment to one token setting.
However, those checks do not establish our required permissions across every endpoint and worker.

Test these requirements before adoption:

1. Keep the service local during the trial.
2. Use fake tasks in a disposable repository.
3. Disable Git writes and broad permission modes.
4. Verify that generated instructions preserve repository rules.
5. Test duplicate messages, stale sessions, restart, cancellation, and interrupted results.
6. Verify that one project cannot control another project.
7. Check transcript retention and secret handling.
8. Measure operator interventions against our existing workflow.

The inspected commit has a successful [Tests workflow](https://github.com/Jason-Vaughan/TangleClaw/actions/runs/37568078601).
This supports active testing, not our runtime qualification.

Sources: [README](https://github.com/Jason-Vaughan/TangleClaw/tree/8dee6707495384f7080d2fb75b0f5db3f442ee47),
[security policy](https://github.com/Jason-Vaughan/TangleClaw/blob/8dee6707495384f7080d2fb75b0f5db3f442ee47/SECURITY.md),
and [control authentication](https://github.com/Jason-Vaughan/TangleClaw/blob/8dee6707495384f7080d2fb75b0f5db3f442ee47/lib/control-auth.js).

### TangleBrain: useful routing, not training coordination

TangleBrain selects language-model backends. Its core Python package has a small dependency set, with optional MCP support.
It can help route suitable text work to existing local models.
It does not replace data admission, a training queue, or Core ML checks.

The security design deliberately keeps its unauthenticated HTTP interface on loopback.
Do not expose that interface to the LAN to connect Macs with Big Dog.
Remote use needs a separately designed authentication boundary.

The documentation separates paid API use from local or logged-in CLI backends.
That reduces accidental paid use, but it does not prove that provider terms permit every routing arrangement.

The reviewed security model records several limitations:

- Configuration can redirect prompts to a different backend.
- Loose credential-file permissions produce warnings rather than guaranteed refusal.
- Error output can expose prompt content.
- An optional classifier can see the request before the selected backend.
- Estimated avoided cost is not measured financial savings.

A useful trial uses public text and existing backends only.
Measure accepted output, retries, latency, memory, and actual paid usage.
Do not compete with Big Dog's active GPU training without a scheduling rule.

Sources: [security model](https://github.com/Jason-Vaughan/TangleBrain/blob/b5c252894d96db4e037dd9228bb9d5e3373769ce/docs/design/security-model.md),
[router](https://github.com/Jason-Vaughan/TangleBrain/blob/b5c252894d96db4e037dd9228bb9d5e3373769ce/tanglebrain/router.py),
and [releases](https://github.com/Jason-Vaughan/TangleBrain/releases).

### Medusa: messaging needs stronger request protection

Medusa offers agent messages, peer discovery, and task coordination.
The repository includes a Node.js hub and Python services. The website describes it as beta.

The inspected Python verifier signs a timestamp and request path.
It does not include the method, body, or claimed client identity in that signature.
It accepts timestamps within 300 s. That verifier does not record used nonces.

These facts matter because a shared-secret signature does not prove which worker made a request.
A timestamp limit alone does not prevent replay within that limit.
The repository also documents a default shared secret and a legacy secret check.

This review did not test an exploit or prove that every endpoint uses this verifier.
These are specific design concerns that require resolution before connecting trusted workers.

Required changes or external controls include:

- Separate credentials for each worker.
- Signed method, path, body digest, timestamp, and unique request ID.
- Rejection of repeated request IDs.
- Explicit permissions for each operation.
- Protected transport between machines.
- Credential rotation and worker revocation.
- No execution authority from an incoming message alone.

A PIN can help enroll a worker. A shared PIN is not enough to authenticate later commands.
Keep human approval separate from message delivery.

Sources: [verifier](https://github.com/Jason-Vaughan/Medusa/blob/c55548a42b31e5f759333855ac83b83d64c23c9f/src/a2a_node/app/core/security.py)
and [security policy](https://github.com/Jason-Vaughan/Medusa/blob/c55548a42b31e5f759333855ac83b83d64c23c9f/SECURITY.md).

### PortHub: useful idea, unsafe to assume production readiness

PortHub tracks port leases and exposes registry operations through HTTP.
This can reduce accidental port reuse. It cannot prove which Fixture process owns an endpoint.
An advisory lease cannot stop another process from opening a port.

The standalone source has concrete concerns:

- The REST server calls `listen(port)` without an explicit loopback address.
- The inspected REST handler has no authentication check.
- It sets a wildcard cross-origin policy.
- It accumulates request bodies without a visible size limit in that handler.
- Package test commands print placeholder messages and return success.
- Its documented port 8080 conflicts with our common Fixture endpoint.

Do not deploy the standalone server on our LAN as supplied.
If we need it, first add local binding, access checks, request limits, and actual tests.
Test restart behavior because an in-memory registry is not a durable job record.

Sources: [REST server](https://github.com/Jason-Vaughan/PortHub/blob/ea0fb53e7ef8d5a0d5d2319daa117032be9be622/src/daemon/restAPI.ts),
[registry](https://github.com/Jason-Vaughan/PortHub/blob/ea0fb53e7ef8d5a0d5d2319daa117032be9be622/src/core/registry.ts),
and [package scripts](https://github.com/Jason-Vaughan/PortHub/blob/ea0fb53e7ef8d5a0d5d2319daa117032be9be622/package.json).

### ClawBridge: additional execution power with limited benefit here

ClawBridge starts Claude Code through a terminal interface and exposes HTTP controls.
Its native `node-pty` dependency and terminal parsing add maintenance requirements.

The inspected server refuses startup without a token unless an explicit unauthenticated option is set.
It also binds to `0.0.0.0`. Authentication therefore does not make its default network reachability local-only.

The inspected `isAllowedDir` function uses string-prefix checks after path resolution.
That is not a directory-boundary check and does not resolve symbolic links.
The export-file checks also use prefix comparisons.
These checks need targeted tests before they protect our filesystem boundary.

We already have a proposed Codex worker path. Adding a Claude-specific bridge now creates another execution and permission system.
Use it only if a measured Claude-specific requirement justifies that cost.

Source: [server implementation](https://github.com/Jason-Vaughan/ClawBridge/blob/946f41961fe6acf2bc046a792b46733c82c3f494/bridge/server.js).

### UCI and review workflows: borrow the process, not the claims

UCI describes a review queue with approvals, corrections, rejection reasons, and an audit record.
Those concepts match our need to review hard images and record why labels change.

The website also describes confidence scores, learning, and readiness for autonomous replies.
Public descriptions do not establish calibrated confidence, a working training process, or safe autonomy.
Human corrections can support supervised learning without reinforcement learning.

Ask Jason for a redacted case from input through review, correction, evaluation, and a later decision.
For NUIAK, retain original labels and model predictions separately. A human correction must not erase the original experiment result.

Source: [UCI description](https://github.com/Jason-Vaughan/jasonvaughan.com/blob/0820cc90ac48d53925c5d908c01ebbc24cd4f8ba/src/components/Pipeline.jsx).

## Licenses, dependencies, and privacy

The public repository inventory reports MIT for TangleClaw, TangleBrain, Medusa, PortHub, ClawBridge, ScrapeGoat, and the 3 OpenClaw plugins.
It also reports MIT for prawduct. That project is a fork, so preserve upstream attribution.

Two metadata inconsistencies require care:

- CLiTS has an MIT license file, although its README badge indicates BSD.
- refuctor has MIT terms plus an addendum that explicitly says it does not change those terms.

clock8002 reports GPL-2.0. Check the applicable obligations before distributing modified code.
Notse uses commercial terms. Its public release repository does not make its implementation open source.
Several supporting repositories have no detected license. Do not treat public access as permission to redistribute their contents.

Code licenses do not automatically cover included screenshots, manuals, branding, or third-party assets.
None of these repositories supplies an approved NUIAK training corpus through this review.

Dependency review remains incomplete:

- TangleClaw's small Node dependency surface does not remove external CLI and service risks.
- TangleBrain adds backend tools and optional MCP dependencies beyond its core package.
- Medusa combines JavaScript and Python services.
- PortHub includes Node packages and a dashboard toolchain.
- ClawBridge includes a native terminal dependency.
- ScrapeGoat combines browser PDF processing with an optional Gemini workflow through a proxy.

For ScrapeGoat, browser-side PDF parsing does not prove that extracted text stays local during AI use.
Verify the exact request payload before using private documents.

Before any installation, pin a release and inspect its lockfiles, install scripts, licenses, and advisories.
This review does not establish that dependencies are free of known vulnerabilities.

## Fit with our current coordination plan

Our recent [coordination review](../reports/work/COORD-REVIEW-241/review.md) identifies permissions, recovery, and result verification as requirements.
Jason's tools overlap with parts of that plan. They do not remove those requirements.

| Our requirement | Potential contribution | What remains ours |
|---|---|---|
| See active work and blockers | TangleClaw dashboard and sessions | Tasks.md remains the approved queue |
| Deliver messages | TangleClaw switchboard or Medusa | Authentication, permissions, acknowledgment, and acceptance |
| Avoid duplicate jobs | Session and assignment controls | Stable job IDs and tests for repeated delivery |
| Recover interrupted work | Persistent sessions | Decide whether an operation happened before retrying |
| Assign work to Big Dog | Routing concepts | GPU scheduling, resource limits, and immutable inputs |
| Reduce language-model cost | TangleBrain | Quality checks and actual cost measurement |
| Avoid endpoint conflicts | PortHub | Verify the exact simulator, process, and endpoint |
| Review difficult images | UCI design patterns | Label authority, data roles, and independent evaluation |
| Protect repositories | Authentication and project controls | Local enforcement and no agent Git writes |

Do not run two independent dispatchers for the same jobs.
Do not add Temporal, TangleClaw, Medusa, and a second task database merely because each offers coordination features.
First test the smallest component that addresses a measured failure.

These tools can improve throughput indirectly. They do not establish better focus accuracy, better annotations, or valid evaluation splits.
Continue model work while assessing coordination tools.

## Proposed bounded trials

These are recommendations, not new assignments or installation approvals.

### Trial 1: TangleClaw coordination without real authority

**Outcome:** decide whether TangleClaw reduces manual work without weakening our controls.

Use 3 fake jobs: a report, an interrupted computation, and a result with a wrong hash.
Use a disposable repository and synthetic metadata. Do not expose screenshots or credentials.

Test these cases:

- Deliver the same job twice.
- Restart the session before the result returns.
- Cancel a job while it runs.
- Reject a result with a wrong hash.
- Deny a request from another project.
- Preserve repository instructions.
- Refuse Git writes.
- Keep failed and uncertain results visible.

Record setup time, interventions, duplicate effects, lost messages, and recovery time.
Compare with the existing SMB process. Accept adoption only if the trial shows a useful improvement.

### Trial 2: TangleBrain for low-risk text tasks

**Outcome:** measure whether local routing saves useful time or paid usage.

Use 20 public-text tasks with predefined acceptance checks.
Include summaries, structured extraction, and simple report formatting.
Use existing backends only. Do not download models as part of the research approval.

Record accepted results, retries, latency, peak memory, and actual charges where available.
Test a failed backend and a request that must stay local.
Reject a configuration that silently sends that request elsewhere.

### Trial 3: source-level fixes before a messaging trial

**Outcome:** resolve Medusa and PortHub blockers without touching our live workflow.

Ask Jason whether newer branches already address the findings.
Request regression tests for body signatures, duplicate requests, worker identity, local binding, and path boundaries.
Do not fork a second coordination platform before reviewing his response.

## Questions for Jason

1. Which released versions do you run daily, and which features remain experimental?
2. Which failures required manual recovery during the last month?
3. Can TangleClaw enforce no Git writes and preserve an existing AGENTS.md?
4. Can each worker receive separate credentials and operation permissions?
5. Which assignment and message records survive process or machine restarts?
6. How do you prevent duplicate effects after an uncertain timeout?
7. Does Linux support exist beyond plans or prototypes?
8. Are standalone Medusa and the TangleClaw switchboard separate supported products?
9. Do newer versions fix the inspected signature, binding, and path-boundary issues?
10. Can UCI provide a redacted review record and its evaluation method?
11. Which assets and private components can we legally reuse?
12. Which benefits have measured baselines rather than estimated savings?

## Evidence record

The following commits anchor the deeper source review:

| Repository | Inspected commit |
|---|---|
| jasonvaughan.com | `0820cc90ac48d53925c5d908c01ebbc24cd4f8ba` |
| TangleClaw | `8dee6707495384f7080d2fb75b0f5db3f442ee47` |
| TangleBrain | `b5c252894d96db4e037dd9228bb9d5e3373769ce` |
| Medusa | `c55548a42b31e5f759333855ac83b83d64c23c9f` |
| PortHub | `ea0fb53e7ef8d5a0d5d2319daa117032be9be622` |
| ClawBridge | `946f41961fe6acf2bc046a792b46733c82c3f494` |

Other inventory findings use repository metadata and documentation fetched during this review.
Those links can change. Recheck them before adoption.

Recent workflow records require careful interpretation:

- TangleClaw shows successful tests at the inspected commit.
- TangleBrain shows recent successful CI at other commits.
- The recent Medusa, PortHub, ClawBridge, and ScrapeGoat records inspected here update statistics.
- A successful statistics workflow is not a successful application test.

Raw public research copies remain in the ignored `reports/work/JASON-PROJECT-REVIEW/artifacts/` directory.
This document is the review deliverable. No fetched code ran, and no shared status or external project changed.

## Bottom line

Jason has several relevant coordination tools, but they vary substantially in maturity and security.
Start with one isolated TangleClaw trial and a focused discussion with Jason.
Keep TangleBrain optional. Treat Medusa and standalone PortHub as requiring further work before trusted use.
Keep NUIAK's model evaluation, TTR's native capture, and Big Dog's training controls separate from the coordination interface.
