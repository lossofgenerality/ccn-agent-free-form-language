# Agent script — 6. Design specification

*Interim draft for comment, 21 November 2026.*

This file sets out what the language is and what it promises, building on files 1 to 3. File 7 says how it is built, and file 8 covers the agent's own neural nets.

## 1. What a script is made of

A script has three kinds of line, and all three can sit in one file:

1. **Spoken lines**, in plain English: `voice: calm, precise, kind`, `then suggest a question about the page`. They work as in file 2.
2. **Key-word blocks**, the small set of headings the compiler knows (`agent:`, `speaks:`, `knows:`, `topics:`, `may search the web:`, `never:`, `when …:`, `answers:`, `budget:`). This file adds three: `target:`, `uses Claude:` and `own net:`.
3. **Code steps**, written in **Wolfram** or **Python**, or in both. A code step is computing that the agent does exactly, where it shouldn't guess.

Spoken lines say *what* the agent should do. A code step says *exactly how* to compute something, and the script's key words say *which rules hold*.

## 2. Code steps

A code step has a name, the language it is written in, and indented code:

```
step "today's puzzle", in Wolfram:
  RandomChoice[Import[file["puzzles.json"], "RawJSON"]]

step "today's puzzle", in Python:
  random.choice(load(file("puzzles.json")))

when the child asks for a puzzle:
  give step "today's puzzle", then say it in Tutu's voice
```

The rules:

- **Its name joins it to the spoken lines.** `give step "…"` runs the step and passes its result to the agent as data, marked as computed.
- **Wolfram, Python, or both.** When a step is written in both, they must agree. A `check with:` line gives test inputs, and the compiler runs both versions on them; if the results differ, the script doesn't compile.
- **Only the inputs it is given.** A step sees only what the script passes in (`the question`, `the page's readings`, `file "…"`), and has a time limit (10 seconds by default). It has no network access unless the script says so, and it can't read the keys.
- **Only CCN writes code.** Code steps are allowed in the CCN base and agent layers only. Customer and page scripts stay in spoken lines and key words, because their authors don't run the kernel. (This is question 8 in file 5.)

```
step "price in euros", in Wolfram:
  QuantityMagnitude@CurrencyConvert[Quantity[#amount, "USDollars"], "Euros"]
check with:
  amount = 10   -- both versions must return the same number, to 2 places
```

## 3. Targets: Wolfram and Python

```
target: Wolfram, Python
```

A script can be compiled for either **target**, or for both:

| Target | Where the agent runs | What it is |
|---|---|---|
| **Wolfram** | the CCN Wolfram Cloud kernel | an APIFunction like `EyeWitnessKernel` and `CameraKernel`, with modes |
| **Python** | a Python host (for example on Vercel, as in the CCN Action Gateway) | a small web service that loads the same compiled policy |

The design keeps the two targets equal:

- **One compiled policy for both.** The policy (file 3) is plain JSON, with nothing in it specific to Wolfram or Python. Both runtimes load the same file and enforce it the same way.
- **Code steps keep to their own language.** On the Wolfram target, Wolfram steps run in the kernel. On the Python target, Python steps run in the host. A step written only in the other language goes over a **bridge**: Python called from Wolfram (`ExternalEvaluate`, where the cloud allows it, or else the Python host over HTTPS), and Wolfram called from Python (the kernel's `wolfram` mode, as in Composite Eye).
- **The same tests for both.** A behaviour test is written once and run against both targets (file 7).

## 4. What we take from CCN Composite Eye

Composite Eye already does a small version of this, and the language keeps its pattern:

- **One kernel with modes.** `CameraKernel` has a `wolfram` mode, which evaluates code, and a `chat` mode, which forwards a Claude request. The agent kernel keeps both and adds `ask`, `compile`, `try`, `net`, `train` and `ledger` (file 7).
- **Keys stay in the cloud.** The Claude key sits in a private Cloud object, and pages send only the kernel's own key. The Python host never holds the Claude key either: it reaches Claude through the kernel's `chat` mode (section 5 says why).
- **Settings come first.** Composite Eye's page begins with one settings block (model, kernel URL). A script begins with its settings in the same way: `agent:`, `target:`, `uses Claude:`.
- **The same document layout.** Each agent folder gets a README laid out like Composite Eye's: what it does, Use, Settings, Kernel, with the authors line and the licence.

## 5. `uses Claude:` — when, where and why

Every agent says what it uses Claude for, and the kernel records every call:

```
uses Claude:
  model: claude-sonnet-5-5
  for: answers, reading free lines at compile time, labelling examples for own nets
  not for: anything else
```

- **Only for the purposes listed.** A Claude call for any other purpose is refused in code. The purposes are a short fixed list: `answers`, `compile`, `try`, `label`, `summary`, `daemon`.
- **Every call goes in the ledger.** The kernel writes a record of each call, so we can always say **when**, **where** and **why** Claude was used:

| Field | What it holds |
|---|---|
| when | the time, in UTC |
| where | agent, layer, customer, page, target (Wolfram or Python), kernel |
| why | the purpose, and the script line that caused the call (for example `agents/tutu-cat.agent:14 when the child asks for a puzzle`) |
| what | model, tokens in and out, web searches, cost, and who it was charged to |
| result | answered, refused, cut short, or failed |
| instead | when an own net handled a question without Claude, the net's name and how sure it was |

- **The visitor's words aren't kept by default.** The ledger keeps a fingerprint (hash) of each question, not its text. A script can keep questions for a set time (`keep questions: 30 days`) only where the CCN base allows it, and **never for Tutu Cat or any agent for children**.
- **There is one ledger.** The Python host calls Claude through the kernel's `chat` mode, so every call, from either target, lands in the same private ledger in the cloud. This fixes the problem at the root: no runtime can call Claude without the call being recorded.

## 6. `own net:` — the agent's own neural nets

An agent can have small neural nets of its own, trained outside Claude ("exogenous"), each for one specific job: deciding whether a question is on topic, recognising the language, reading a free line at compile time. They are trained, and can be retrained, in **both Wolfram and Python** from the same description. File 8 covers them in full. The design rules are:

- **A net can only narrow.** It may answer in place of Claude where it is sure, block something, or send a question on to Claude. It can never remove a `never:` line, switch on a search, or loosen a rule. Safety checks done by a net are **added** to the kernel's checks, never put in their place.
- **When it is unsure, Claude decides.** `used when: sure above 0.9; otherwise ask Claude`. Each time this happens it goes in the ledger as the *why*.
- **One description, two trainers.** The same net description builds a `NetChain` in Wolfram and a `torch.nn` model in Python. Trained weights move between the two as ONNX.

## 7. Daemons

**Daemons** are processes that watch CCN's systems or run at set times, and invoke an agent or some software when something needs doing. Each daemon is **attached** to one or more components of CCN's systems (a kernel, an app, a page, a repo, a cloud path) or to a whole system, and it may act only on what it is attached to. One kind, the **update daemon**, updates specific components or whole systems on a schedule. Daemons are written in the same language, sit only in CCN's layers, and go live with changes only with the owner's approval. File 9 covers them (for discussion).

## 8. What the design promises

1. A script means the same thing on both targets, and the compiled policy is the same file.
2. What must hold is enforced in code (file 3). Code steps, own nets and Claude all work inside that.
3. No Claude call goes unrecorded, and none is made for a purpose the script didn't list.
4. Lower layers narrow; they never loosen. This holds for code steps and nets too.
5. The compile report shows how every line was read: spoken lines, key words, code steps (with their check results), and nets (with their test scores).

© Computational Classnotes · CC BY-NC-SA 4.0
