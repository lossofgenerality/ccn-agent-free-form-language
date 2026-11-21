# Agent script — 9. Daemons

*Interim draft for discussion, 21 November 2026.*

## What a daemon is

A **daemon** is a process that runs on its own, without a visitor asking anything. It watches part of CCN's systems, or runs at set times, and when something needs doing it **invokes an agent or some software**. Agents answer people; daemons look after the systems the agents run on.

Daemons are written in the same script language as agents. They use the same spoken lines, key words and code steps, the same layers and ledger, and the same rule that what must hold is enforced in code.

## Daemons are attached to components

CCN's systems are described as **components**, and a system is a set of components:

```
system "eye-witness"
  component "EyeWitnessKernel"      -- a Wolfram Cloud kernel
  component "eye-witness-admin"     -- an app and its repo
  component "eye-witness-builder"   -- the page builder and its template
  component "witness pages"         -- the published pages
  component "freeform/ff/eyewitness/" -- its cloud path
```

A component can be a kernel, an app, a page, a repo, a cloud path, a scheduled task or an agent. Each daemon is **attached** to one component, to several, or to a whole system:

```
daemon: Kernel watch
  attached to: EyeWitnessKernel, TUTUKernel, CameraKernel, MAXITKernel
```

- **The attachment is its reach.** A daemon may read, check and act only on the components it is attached to, and the parts inside them. The kernel enforces this in code: a daemon attached to `TUTUKernel` can't deploy to `EyeWitnessKernel`.
- **One component can have many daemons**, for example a watch daemon and an update daemon on the same kernel.
- **A daemon attached to a system** covers every component the system lists, in the order it lists them.
- **Each component lists its daemons**, so we can always see what is watching it and what may update it. The `ledger` mode can show this, component by component.
- **The descriptions are files** (`systems/`, next to `agents/` and `daemons/`), kept in git like the scripts.

## Three kinds

| Kind | Runs | Example |
|---|---|---|
| **watch** | every few minutes or hours | Is every kernel answering? Is a page's budget nearly used? Has Claude spending jumped? |
| **event** | when something happens | a push to a repo, a failed `ask`, a new eye-witness page, a ledger record over a limit |
| **update** | on a schedule, or when asked | updates one component, or a whole system, to its latest approved state |

## In a script

### A watch daemon

```
daemon: Kernel watch
  attached to: EyeWitnessKernel, TUTUKernel, CameraKernel, MAXITKernel
  every: 15 minutes

  checks:
    each kernel answers its connection check within 10 seconds
    no kernel has more than 5 failed requests in the last hour
    Claude spending today is under the day's limit

  when a check fails:
    check again in 2 minutes          -- one bad minute isn't a failure
    if it still fails:
      call agent "Ops assistant" to write a short report from the ledger
      tell: dara@compclassnotes.com, wayne@compclassnotes.com

  never:
    change, redeploy or restart anything
```

### An update daemon

```
daemon: Weekly update
  attached to: system "eye-witness", AgentKernel
  every: Sunday 03:00, Dublin time
  updates:
    component "EyeWitnessKernel"  from repo "packing-station", folder "kernel"
    component "AgentKernel"       from repo "ccn-agent-free-form-language"
    the rest of system "eye-witness"  -- every component it lists, in order

  for each component:
    take the newest commit on main
    if it is the one already deployed: skip it
    run its tests                     -- the kernel test files, both targets
    deploy it to the trial path, and run the behaviour tests there
    compare the trial with the live one on the same test questions
    then: ask the owner                -- see "Approval" below

  if anything fails:
    leave the live one as it is
    call agent "Ops assistant" to explain what failed
    tell: dara@compclassnotes.com
```

The new key words are `daemon:`, `attached to:`, `system`, `component`, `every:`, `on:` (for events), `checks:`, `updates:`, `call agent "…"`, `run step "…"`, `tell:` and `then: ask the owner`. Anything else in a daemon is read as file 2 describes: what isn't a key word is guidance.

## What a daemon may invoke

- **An agent.** It goes through the kernel's `ask` path, with the Claude purpose `daemon`. The ledger's *why* names the daemon and the script line: for example `daemons/kernel-watch.agent:14 when a check fails`.
- **A code step**, in Wolfram or Python (file 6).
- **Software:** a test run, a deploy, or a `tell:` (an email or alert).
- **Another daemon.** For example, a watch daemon can start the update daemon for one component. The update still waits for approval.

## Approval: what a daemon may do on its own

This is the main question for our discussion. As drafted:

| On its own | Only with the owner's approval |
|---|---|
| read: kernels, the ledger, repos, test results | deploy anything to a live path |
| run tests and connection checks | restart or switch off a kernel or a page |
| deploy to a **trial** path | change a script, a policy, a budget or a key |
| call an agent to write a report | send anything to anyone not on the CCN `tell:` list |
| `tell:` the CCN list (Dara, Wayne) | delete anything |

- **What approval looks like.** The update daemon prepares everything, then sends one message: what would change, the test results, and the trial-versus-live comparison. Nothing goes live until the owner replies "go" (or, in admin, presses Approve). This keeps the "push" and "send" rule: a person says when.
- **Rolling back.** Each live deploy is one git commit, so going back means redeploying the commit before it. No old copies with version numbers in their names are kept.
- **Keys.** A daemon reaches the cloud and GitHub with keys kept privately in the cloud (like `EyeWitness/githubtoken`). They are never in the daemon's script.

## Where daemons run

- **Wolfram:** a `ScheduledTask` deployed to the cloud (`CloudDeploy[ScheduledTask[…, schedule]]`). It calls the libraries directly and writes to the same ledger.
- **Python:** a scheduled job on the Python host (for example a Vercel cron job), or a scheduled GitHub Actions workflow for repo work. The Python host still reaches Claude only through the kernel (file 7).
- **Events:** a GitHub webhook for pushes; for kernel events, the kernel itself wakes the daemon when it writes a matching ledger record.

## Rules for daemons

1. **Only CCN writes daemons.** They live in CCN's layers (`daemons/` next to `agents/`), never in customer or page scripts.
2. **A daemon acts only on what it is attached to.** The kernel checks this in code (see "Daemons are attached to components").
3. **Each daemon has a budget:** how often it may run, how many Claude calls it may make in a day, and a cost limit. When the budget is used up, the daemon stops and tells the CCN list.
4. **Every run goes in the ledger:** when it ran, what it checked, what it invoked, what it changed (in a trial or with approval) and what it cost.
5. **A daemon narrows, too.** It may take something out of service only if its script says so and the owner approved that line. It can never loosen an agent's rules, raise a budget, or switch on a search.
6. **Children's agents are only watched from outside.** A daemon may check that Tutu Cat's kernel answers, but it never reads Tutu Cat's chats.

## Still to discuss

- How to divide CCN's systems into components, and which to attach daemons to first.
- Which systems to watch first, and how often.
- The update daemon's schedule, and which components and systems it covers.
- Whether some small, reversible changes may go live without approval, for example re-running a failed page build.
- Who is on the `tell:` list, and how alerts arrive: email, the admin app, or both.
- Whether the "Ops assistant" is a new agent, or one of today's agents with a daemon layer.

© Computational Classnotes · CC BY-NC-SA 4.0
