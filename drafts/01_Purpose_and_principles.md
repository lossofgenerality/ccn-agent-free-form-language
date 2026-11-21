# Agent script — 1. Purpose and principles

*Interim draft for comment, 21 November 2026. Working name: "agent script" (see file 5 for names).*

## What it is for

Each support agent (the eye-witness page assistant, Tutu Cat, MAXIT, the Laplacian teaching assistant, and the ones still to come) is defined by **one script**, written in plain, spoken-style language with a little programming structure. The script replaces the context files and hand-written prompts we use today. It says:

- **who** the agent is: name, languages, voice and character;
- **what it knows**: its data (page readings, files, the cloud indexes we're planning, the web) and in what order to trust them;
- **what it may search**, and only about what: topics, sites, how many searches;
- **what it must never do**, and what to say instead;
- **its budget**: questions per day and per month, and who pays for them;
- **how it answers**: length, citations, clip buttons, and spoken answers.

## Principles

1. **Readable by anyone on the team.** A script should read like a short brief to a new colleague. Wayne, Dara or a customer should understand it without knowing a programming language.
2. **A little structure, never more than needed.** Headings with a colon, indented lines, lists with commas, quotes for exact wording. Nothing else is required. Anything the reader doesn't recognise as structure is kept as free guidance.
3. **What must hold is enforced in code, not just asked for.** The script is compiled into two parts:
   - **rules the kernel enforces** (who may search, about what, which sites, how many questions, which languages, which data);
   - **guidance the AI is given** (voice, tone, how to phrase things).

   "Never search about cooking" is enforced: the search is blocked in code. "Be playful" is guidance. Each script's compile report shows which is which (file 3).
4. **Layers, with CCN on top.** CCN's base script applies to every agent. A customer's or a page's script can narrow it but never loosen it. A customer can't switch off "never identify people from their appearance".
5. **One language for every agent.** Tutu Cat and the eye-witness assistant use the same script language, the same compiler and the same kernel, so a fix or a new safeguard reaches every agent at once.
6. **Honest by construction.** Every agent marks where an answer comes from (the media, general background, the web) and says when it doesn't know. These aren't optional lines in a script: they're part of CCN's base layer.

## What changes for us

- The **Keywords box** planned for admin becomes the agent's script editor. Keywords are simply the `topics:` block.
- The rules now written inside the kernel (`ewAskRules`) become CCN's base script, which you can read and edit.
- Each agent's behaviour is in a file you can review, compare and keep in git (with no version numbers in names; git keeps the history).

© Computational Classnotes · CC BY-NC-SA 4.0
