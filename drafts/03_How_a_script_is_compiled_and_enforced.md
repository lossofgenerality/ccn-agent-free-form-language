# Agent script — 3. How a script is compiled and enforced

*Interim draft for comment, 21 November 2026.*

## From script to agent

1. **Write** the script: in admin for a customer or a page, or as a file for CCN's own agents.
2. **Compile** it on the kernel when it's saved. The compiler reads the key words and turns the script into:
   - a **policy** that the kernel enforces in code;
   - **guidance**: the free lines and the voice, given to the AI as its instructions;
   - a **compile report** for the author.
3. **Merge** the layers: CCN base, then agent, then customer, then page. The narrowing rules apply (file 2).
4. **Use**: every question goes through the kernel, which applies the policy, sends the guidance to the AI, checks the reply, and returns it.

## What is enforced in code, and what is guidance

| Script line | Enforced in code | Given to the AI as guidance |
|---|---|---|
| `speaks:` | replies in other languages are refused or redone | which language to answer in |
| `knows:` | only the data listed is loaded and sent | the order of trust, and how to mark each source |
| `topics:` | web search is allowed only for questions on these topics, and every search query is checked against them (as today) | what the agent is about |
| `may search the web:` | the search tool is switched on or off; sites to prefer or avoid; the search limit | how to cite |
| `never:` | the ones the kernel can check (e.g. "talk about: cooking", blocked searches, banned words) | all of them, as firm instructions |
| `when asked about something else:` | the exact `say:` wording is returned when the kernel blocks a question | when to use it |
| `answers:` | the length limit, cut-short replies repaired, clip ids checked against the page | the style |
| `budget:` | the daily and monthly counts, as today | — |
| free lines | — | given as written |

## The compile report

Saving a script shows the author how it was read, so a free-form script never silently means something else:

```
✓ Agent: Tutu Cat · speaks English, Japanese
✓ Knows: tutu-world.md (2,140 words), general knowledge
✓ Topics: 6 · web search: off
✓ Never: 2 lines (1 checked in code: "talk about: violence, scary things, shopping")
✓ When asked about something else: exact reply set
• Guidance (given to the AI as written): 2 lines
⚠ "says nya now and then" — read as voice, not a rule
⚠ CCN base adds: never identify people from their appearance; mark general background
```

## A "Try it" box

Next to the editor: ask the agent a question with the script as it now stands, before saving. It shows the answer, which rules applied, which searches it made, and what it cost.

## Where scripts live

- **CCN base and agent scripts:** files in a repo (for example `agents/`), loaded by the kernel; git keeps their history.
- **Customer and page scripts:** in the customer's record in the cloud, under the master path `freeform/ff/eyewitness/`, edited in admin.
- **Compiled policies:** cached privately in the cloud next to them, and rebuilt when a script changes.

## How today's assistant fits

Today's rules (`ewAskRules`, the subject list, the web-search checks, the limits) are, in effect, the first compiled script. Step one of building this would be to write them out as the CCN base script plus the "Eye-witness assistant" script, and check that the compiled policy gives exactly today's behaviour.

© Computational Classnotes · CC BY-NC-SA 4.0
