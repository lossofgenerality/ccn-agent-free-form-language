# CCN agent free-form language

A plain, spoken-style language with a little programming structure, for defining CCN's support agents (the eye-witness page assistant, Tutu Cat and others): who each agent is, what it knows, what it may search and only about what, what it must never do, and its budget.

Each script is compiled on the CCN kernel into rules the kernel enforces and guidance the AI is given. CCN's base layer applies to every agent; customer and page scripts can narrow it but never loosen it.

## Status

Drafts for comment, in `drafts/`:

1. `01_Purpose_and_principles.md`
2. `02_The_language_by_example.md`: the eye-witness assistant and Tutu Cat
3. `03_How_a_script_is_compiled_and_enforced.md`
4. `04_Plan_of_work.md`
5. `05_Questions_for_you.md`
6. `06_Design_specification.md`: spoken lines, Wolfram and Python code steps, the two targets, `uses Claude:` and the ledger (when, where and why)
7. `07_Implementation_specification.md`: the reader, the compiler, `AgentKernel` and its modes, the Python host, tests
8. `08_The_agents_own_neural_nets.md`: small nets trained outside Claude, in Wolfram and in Python, exchanged as ONNX

The kernel pattern (modes, keys kept in the cloud, a settings block first) is taken from CCN Composite Eye.

Files are updated in place; git keeps the history.

© Computational Classnotes · CC BY-NC-SA 4.0
