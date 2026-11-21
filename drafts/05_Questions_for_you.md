# Agent script — 5. Questions for you

*Interim draft for comment, 21 November 2026.*

1. **Its name.** A working name is "agent script". Possible names: *CCN Agent Script*, *Construct* (from "conversational-construct"), *Persona Script*, *Brief*. Or a name of your own.
2. **The language the scripts are written in.** English key words only, or also Arabic and Japanese key words, so a customer can write the whole script in their own language? (The free guidance lines can be in any language either way.)
3. **Who writes scripts.** CCN only, or customers too (their layer, in admin)? And may a customer's script add sites for web search, or only choose from CCN's list?
4. **How much is enforced.** Should `never:` lines that the kernel can't check be allowed at all, or should the compile report flag them as "guidance only" (as drafted)?
5. **The free form.** Is the structure in file 2 light enough? Should the language allow conditions such as `when the visitor writes in Arabic:` or `if the page has no faces:`, or keep those out for now?
6. **Tutu Cat's data.** Does Tutu Cat have a body of text it should know (a story, a list of puzzles), or should we write one together?
7. **Scripts as files.** Do you want the CCN and agent scripts in a new repo of their own (for example `ccn-agents`), or in each app's repo?
8. **Who writes code steps.** As drafted, only CCN's layers (base and agent) may contain Wolfram or Python code, and customers use spoken lines and key words only. Is that right?
9. **Training on Claude's decisions.** May own nets learn from questions Claude has already judged (only where questions are kept, and never for children's agents)? If so, we should check Anthropic's current terms on training with Claude's outputs before step 9.
10. **Where the Python target runs.** Vercel, as with the CCN Action Gateway, or somewhere else?
11. **The first own net.** The topic gate is proposed (it saves Claude calls on off-topic questions). Or would you rather start with the line reader, the language's own net for the compiler?
12. **One master path for all agents.** Eye-witness uses `freeform/ff/eyewitness/`. Should the other agents sit beside it (for example `freeform/ff/agents/<agent>/`)?
13. **Daemons** (file 9). How should CCN's systems be divided into components, and which should get daemons first? May any small, reversible change go live without your approval? Who is on the `tell:` list, and should alerts come by email, in admin, or both?

© Computational Classnotes · CC BY-NC-SA 4.0
