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
9. `09_Daemons.md`: processes attached to components of CCN's systems, which watch them and invoke agents or software; including the update daemon (for discussion)

The kernel pattern (modes, keys kept in the cloud, a settings block first) is taken from CCN Composite Eye.

## First operations

- `motion/MotionPhrases.nb`: reads motion phrases ("move along the path while spinning counterclockwise and move upwards"), or paragraphs with motion phrases inside them, into `RotationTransform` and `TranslationTransform`. See `motion/README.md` and the report on its output and performance, `motion/Report.md`; tests in `tests/MotionPhrasesTest.nb`, and a larger corpus with paragraphs in `tests/MotionPhrasesCorpus.nb`.
- `nets/SubjectNet.nb`: the first of the agent's own nets (draft 8). It decides whether a motion part is about the object or about something else, in two versions: our own code with no Wolfram neural-net functions, and Wolfram's `NetChain`/`NetTrain`. The comparison is in `nets/SubjectNetReport.md`.
- `python/`: a complete Python version of the motion-phrase reader and of SubjectNet. Softmax, backpropagation, Adam and every other neural-net piece are written as our own code, with NumPy used only for arrays. It gives the same results as the Wolfram notebooks. See `python/README.md`.
- `editor/net-diagram-editor.html`: a browser editor for drawing small nets like SubjectNet. **Diagram → Code** writes a Wolfram notebook (`.nb`) that builds and trains the net drawn, in both versions. It is built on the canvas of the CCN String Diagrams editor. See `editor/README.md`.

Wolfram code in this repo is delivered as notebooks (`.nb`), never as `.wl` files.

Files are updated in place; git keeps the history.

© Computational Classnotes · CC BY-NC-SA 4.0

## Nets and the lab (24 November 2026)

The nets of this project are kept in the lab's standard layout, starting with `nets/subjectnet/` (structure, card, data, training script, recorded runs, analysis, visualisations, write-up). The general tools (the net-diagram editor, our own net code and the 3D viewers) moved to the private toolkit `ccn-net-lab`, and the published pages are in `ccn-nets`: https://lossofgenerality.github.io/ccn-nets/. The old editor and 3D addresses here forward there.
