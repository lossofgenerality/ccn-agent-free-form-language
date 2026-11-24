# Agent script — 7. Implementation specification

*Interim draft for comment, 21 November 2026.*

How the design in file 6 is built. Wolfram code is delivered as notebooks (`.nb`), never `.wl` files: libraries and APIFunctions for you to CloudSave and CloudDeploy. Nothing here uses a fixed disk path, and no file name carries a version number.

## 1. Proposed repo layout

```
agents/                      the scripts (if they live here: question 7 in file 5)
  ccn-base.agent
  eye-witness.agent
  tutu-cat.agent
daemons/                     daemon scripts, CCN only (file 9)
  kernel-watch.agent
  weekly-update.agent
systems/                     CCN's systems and their components, which daemons attach to
  eye-witness.agent
compiler/
  AgentScript.nb             Wolfram: read, merge layers, compile, report
  agent_script/              Python: the same reader and compiler
policy/
  policy.schema.json         the compiled policy, shared by both targets
kernel/
  AgentKernel.nb             the Wolfram target: one APIFunction with modes
host/
  python/                    the Python target: a small web service
nets/
  NetSpec.nb                 own nets: description → NetChain, training, ONNX
  netspec.py                 own nets: description → torch.nn, training, ONNX
tests/
  AgentScriptTest.nb         Wolfram tests, with stand-ins for cloud, Claude and GitHub
  test_agent_script.py       the same cases, in Python
  cases/                     behaviour tests written once, run on both targets
```

Scripts end in `.agent`. They are plain UTF-8 text, so Arabic and Japanese lines work as written.

## 2. The reader

The grammar stays as small as file 2 promises. Indentation makes blocks; everything else is read line by line:

```
script     = { line } ;
line       = comment | setting | heading | step | item | free ;
comment    = "--" text ;                         (also allowed at the end of a line)
setting    = keyword ":" value ;                 speaks: English, Arabic
heading    = words ":" newline indented-block ;  knows, in this order:
step       = "step" quoted "," "in" ("Wolfram" | "Python") ":" newline code-block ;
item       = value ;                             a line inside a block
value      = quoted | list | "yes" | "no" | ref | text ;
list       = text { "," text } ;
quoted     = '"' text '"' ;                       exact wording
ref        = "file" quoted | "step" quoted | block-name ;
free       = text ;                              anything else: guidance
```

- **Code blocks are kept exactly as written.** The reader takes the indented lines under `step …:` verbatim and doesn't parse them. Wolfram code is checked with `SyntaxQ`, and Python code with `ast.parse`.
- **Key words are matched with some give.** Case, plurals and a short list of alternative wordings are accepted (`can search the web:` reads as `may search the web:`). Anything still unmatched is kept as guidance, and the compile report says so.
- **There are two readers and one answer.** The Wolfram and Python readers must give the same parse. A shared set of golden files (`tests/cases/*.agent` → `*.policy.json`) is checked by both, byte for byte, after both outputs are written in canonical JSON (sorted keys, no spaces).

## 3. Compiling

```
read → match key words → take out code steps → merge layers → check → write
```

1. **Merge layers:** CCN base, then agent, then customer, then page. Anything that tries to loosen a layer above it is an error, not a warning.
2. **Check:**
   - each code step parses, and its `check with:` cases pass (on both languages when both are given);
   - each `own net:` has a trained net whose test score meets its `must score:` line (file 8);
   - every Claude purpose used by the script is in its `uses Claude:` list.
3. **Write three things:**
   - `policy.json`, which follows `policy.schema.json` and is the same for both targets;
   - `guidance.md`, the spoken lines and the voice, given to Claude as its instructions;
   - the compile report.
4. **Free lines** that look like rules but don't match a key word are first offered to the line-reader net (file 8). If it isn't sure, they go to Claude with the purpose `compile`, and the call goes in the ledger. Whatever either one suggests is shown in the report for the author to accept. Nothing is turned into a rule silently.

The policy file, in outline:

```json
{
  "agent": "Tutu Cat",
  "layers": ["ccn-base", "tutu-cat"],
  "targets": ["Wolfram", "Python"],
  "languages": ["en", "ja"],
  "data": [{"file": "tutu-world.md", "trust": 1}],
  "topics": ["cats", "Tutu", "puzzles", "numbers", "shapes"],
  "web": {"allowed": false},
  "never": [{"text": "talk about: violence", "checked": "kernel"}],
  "offTopicReply": "Nya! Tutu only knows about puzzles…",
  "answers": {"maxSentences": 3, "speak": true},
  "budget": {"perDay": null, "perMonth": null},
  "claude": {"model": "claude-sonnet-5-5", "purposes": ["answers"]},
  "keepQuestions": "never",
  "steps": [{"name": "today's puzzle", "languages": ["Wolfram", "Python"], "seconds": 10}],
  "nets": [{"name": "topic gate", "file": "tutu-cat/topic-gate", "sureAbove": 0.9}]
}
```

## 4. The Wolfram target: `AgentKernel`

This is one APIFunction, deployed like `CameraKernel`, with the same key check on every request. Its modes:

| Mode | Who may use it | What it does |
|---|---|---|
| `wolfram` | CCN | evaluates code (as in Composite Eye) |
| `chat` | CCN, Python host | forwards a Claude request, and writes the ledger record |
| `ask` | pages | one visitor question, run through the policy (as `ewAsk` does today) |
| `compile` | admin | compiles a script and returns the policy, guidance and report |
| `try` | admin | the "Try it" box: `ask` with an unsaved script, nothing kept |
| `net` | kernel, Python host | runs an own net on one input |
| `train` | owner only | trains or retrains an own net in Wolfram |
| `ledger` | owner only | reads the ledger: totals by agent, purpose, page and day |
| `daemon` | owner only | lists the daemons on each component, their last runs, and approvals waiting (file 9) |

Keys live in private Cloud objects (`<Agent>/apikey`, `<Agent>/secret`, as with `EyeWitness/…` today), never in a script, repo or page. Compiled policies, nets and the ledger sit next to the scripts under the master path. That path is `freeform/ff/eyewitness/` for eye-witness; a shared path for all agents is still to be agreed.

A question goes through `ask` like this:

1. Load the merged policy for the page, which is cached and rebuilt when a script changes.
2. Check the budget and the language.
3. Run the topic-gate net if there is one. If it is sure the question is off topic, return the `offTopicReply` and write a ledger record with Claude *not* used.
4. Run the code steps the matching `when …:` line asks for.
5. Call Claude through the same path as `chat` (purpose `answers`), with the guidance, the data the policy allows, and the search tool only if the policy allows it.
6. Check the reply: length, language, clip ids, `never:` lines checked in code, and source marks. Then return it.

## 5. The Python target

The Python host is a small web service (Vercel works, as in the CCN Action Gateway) with the same `ask`, `try` and `net` routes. It:

- loads the same `policy.json` and `guidance.md` from the cloud;
- runs Python code steps in a separate process with a time limit, and runs Wolfram steps through the kernel's `wolfram` mode;
- runs own nets from their ONNX files (with `onnxruntime`), so it doesn't need PyTorch at run time;
- calls Claude **only** through the kernel's `chat` mode, so the Claude key stays in the cloud and the call goes in the one ledger. Its own key for the kernel is set as a Vercel environment setting, never in the repo.

## 6. Tests

- **Wolfram:** `AgentScriptTest.nb`, with stand-ins for the cloud, Claude and GitHub as in today's eye-witness kernel tests. Open it and evaluate it; its last cell shows the results.
- **Python:** `pytest`, with the same stand-ins.
- **Both targets:** each file in `tests/cases/` holds a script, a question, the stand-in reply, and the expected outcome (blocked, answered, which rule applied, the ledger record). Both runtimes must give the same outcome.
- **First acceptance test:** today's eye-witness assistant written as `ccn-base.agent` plus `eye-witness.agent` must give exactly today's behaviour on the current kernel tests (file 4, step 1).

## 7. Delivery

- **Wolfram:** notebooks only. `AgentScript.nb` and `NetSpec.nb` are libraries you CloudSave, and `AgentKernel.nb` is an APIFunction you CloudDeploy. Each has its deploy steps in its first cells, as Composite Eye's kernel has them at the top.
- **Python:** a package with a `requirements.txt`: `onnxruntime` for the host, and `torch` and `onnx` only for training.
- **Each agent folder** gets a README in the Composite Eye layout.

© Computational Classnotes · CC BY-NC-SA 4.0
