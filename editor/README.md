# CCN Net Diagrams: the editor

> **Moved (24 November 2026).** The editor now lives in the private toolkit `ccn-net-lab` (`editor/`) and is published at https://lossofgenerality.github.io/ccn-nets/editor/net-diagram-editor.html. The old address here forwards there, `?example=` included. This guide is kept for reference; the current copy is in `ccn-net-lab/editor/README.md`.


`net-diagram-editor.html` is a single self-contained page that runs offline in a browser. Open it, draw a small neural net, and press **Diagram → Code**. The page writes a Wolfram notebook (`.nb`) or a Python script (`.py`); see "Wolfram or Python" below. The notebook builds the net drawn and trains it in two versions:

- **A, our own code:** the forward pass, backpropagation and Adam are written out, and no Wolfram neural-net function is used.
- **B, Wolfram's code:** `NetChain` (or `NetGraph` when the drawing branches) with `NetTrain`.

The page keeps the structure of the CCN String Diagrams editor (`lossofgenerality/ccn-string-diagrams`): the canvas, drawing wires from port to port, moving, zooming, panning, undo, the inspector, Save and Open as JSON, and Export SVG. The string-diagram mathematics is replaced by the elements of a net.

## Shared with tensor-algebra-nets

`lossofgenerality/tensor-algebra-nets` shows this editor on its site, at `docs/net-diagrams.html`, by loading it from https://lossofgenerality.github.io/ccn-agent-free-form-language/editor/net-diagram-editor.html?example=tnparser.

**Opening on an example.** `?example=` followed by `subjectnet`, `ownet`, `tnparser`, `tnpolicy` or `tnvalue` opens the editor on that example. It also gives that page its own saved work in the browser, so a change made on the TensorNets page doesn't appear on this one, nor the other way round. Without it, the editor opens on SubjectNet, as on this project's site. A change pushed here therefore appears there at once; nothing needs copying. **Keep this file's name and place.** If it ever moves, change `EDITOR` in tensor-algebra-nets' `tools/units/build_glossary.py` and rebuild there.

## The elements

| Element | Drawn as | What it is | Fields |
|---|---|---|---|
| Feature | purple box | a group of words from a motion part: own words, verb, words after, words before, joining word (as `MotionSubject` gives them) | which group |
| Hash | grey funnel | puts each feature word into a slot, `Mod[Hash[word, "CRC32"], slots] + 1` | inputs, slots |
| Slots | column of cells | the input vector; fed by a Hash, or with nothing feeding it a plain vector for your own data | length |
| Layer | column of teal circles (up to eight are drawn) | a fully connected layer | units; activation ReLU, Tanh, Sigmoid or None |
| Dropout | dashed box | dropout (version B only in this issue) | rate |
| Join | grey bar | joins branches side by side (version B only) | inputs |
| Softmax | dashed box of coral circles with the class names | the output: one unit per class, softmax, cross-entropy loss | classes |

Wires run from an output port (right side) to an input port (left side). An input port takes one wire; an output may feed several, which makes a branch.

The panel on the right reads the drawing as you work. It shows the input, the layers, whether the net is a chain, and the number of weights, with any errors or warnings. **Example: SubjectNet** draws the net of `nets/SubjectNet.nb`: 2,048 slots, 32 ReLU units, two classes and 65,634 weights.

## Sequence nets: transformers

The editor also draws the transformers of `lossofgenerality/tensor-algebra-nets`. They are added from **+ Sequence element…**:

| Element | What it is | Fields |
|---|---|---|
| Tokens | an input sequence of token indices (a port of the net) | name, vocabulary size |
| Numbers per token | an input with a few numbers at every position | name, numbers per token |
| Embedding | a learnt vector for each token, with positions added | width d; learnt, sinusoidal or no positions; longest sequence; shared weights (a name); multiply by √d |
| Per-token layer | the same dense layer at every position | units, activation |
| Add | adds sequences of one width, position by position | inputs |
| Encoder | layers of multi-head self-attention and a feed-forward net, each with a residual connection and layer normalisation | layers, heads, feed-forward width, activation |
| Decoder | layers of causal self-attention, cross-attention to the encoder (the lower input) and a feed-forward net | the same |
| Pick, Pool | one position, or the mean, maximum or sum over positions | position; pooling |
| Softmax per token | an output: a probability over the vocabulary at every position, optionally tied to shared weights, with label smoothing | name, vocabulary, tie, ε |
| Softmax over positions | an output: which position | name |
| Regression | an output of a few numbers, with a mean-squared loss | name, outputs, target port |

**The pictures.** Each sequence element is drawn as what it does, in the style of SubjectNet's elements, with its settings in grey labels underneath:
- tokens as a row of cells (the sample tokens can be set);
- an embedding as columns of vectors, with a wave for sinusoidal positions or small squares for learnt ones, and a badge for shared weights;
- the encoder and decoder as stacked layers with fans of attention and feed-forward blocks;
- the outputs as probability bars or value bars.

**Teacher forcing.** Tokens that reach a Decoder's target input are its target. The decoder reads them without the last token, and the Softmax per token is scored on them without the first. The Softmax (classes) and Dense elements work after Pick or Pool.

**Examples**, under Examples…:
- owNet, the trained net of Unit 4;
- tnParserNet, tnPolicyNet and tnValueNet, the three nets of the TensorNets design.

They are drawn from the nets' definitions, in `tools/units/unit4.py` and `ff_tensornets_new.nb`.

**The count.** The panel gives the learnt weights, and the number Wolfram's `Information[net, "ArraysTotalElementCount"]` reports. That number also counts fixed arrays: sinusoidal positions (2 × d for each embedding) and the label-smoothing table (V × V).

**The code.** Diagram → Code writes a Wolfram notebook with:
- the parts (multi-head attention, feed-forward, layer normalisation, embeddings, encoder and decoder), as in tensor-algebra-nets;
- the net as a `NetGraph` of the drawing, with its input, output, target and loss ports;
- a check of Wolfram's count against the drawing's;
- a training cell for data of one's own, with the ports it expects.

Python does not take sequence nets yet: our own Python code has no attention. The editor says so.

**Tested** (24 November 2026):

| Net | Learnt weights | Wolfram's count | The net built from its own definition |
|---|---|---|---|
| owNet | 59,722 | 59,950 (with 228 fixed numbers) | 59,950 |
| tnParserNet | 1,422,870 | 1,422,870 | 1,422,870 |
| tnPolicyNet | 611,468 | 611,468 | 611,468 |
| tnValueNet | 626,819 | 626,819 | 626,819 |

- **The generated nets:** all four built in the Wolfram kernel with exactly these counts.
- **Training:** the generated owNet trained for three rounds on a small copy task in 2 seconds, giving probabilities of the right shape.
- **The page:** in headless Chrome, every example opens and editing changes the count correctly (a third decoder layer gives 76,714), with no errors in the console.

## Wolfram or Python

**Language**, at the top of the training settings, decides what Diagram → Code writes:

- **Wolfram:** a notebook (`.nb`) with version A (our own code) and version B (`NetTrain`), as described below.
- **Python:** a script (`.py`) that trains the net with our own code in `python/ccn_nets`, with no neural-net library. **Download .py** saves it.
  - **Where to save it:** in the repository's `python/` folder, or anywhere else with "Where the repository's python/ folder is" set to the path from the script's folder to `python/`.
  - **Running it:** `python3 <name>.py`, which needs only NumPy.
  - **What the script contains:** the drawing as JSON, the layer sizes and activations, the features hashed exactly as in SubjectNet, the data, training, and checks: weights in the drawing against the trained net, the test accuracy, the gradient check and the training time. With SubjectNet's data it also reports whether the input matches SubjectNet's, and the paragraph, hard-sentence and step-by-step results. The trained weights are saved beside the script as `<name>.npz`.
  - **Your own data:** write `my_data.py` beside the script, as the script's first lines describe.
  - **Limits in this issue:** Python takes nets drawn as a chain only; for a net that branches, the editor says to choose Wolfram. Dropout is left out of the Python version, as it is of version A.

The choice is remembered with the drawing.

**Tested:** the script written for the SubjectNet example gives Python's SubjectNet results exactly. These are 65,634 weights, 99.5% on test 1, 47 of 47 paragraph parts, 21 of 24 hard sentences and 12 of 12 paragraphs step by step, and the input matches SubjectNet's. Two other drawings also trained:

- three features into 512 slots, 32 ReLU, dropout and 8 Tanh units: 16,698 weights;
- a plain vector of 20 into 6 Sigmoid units and three classes, on data of one's own: 147 weights.

In the browser, switching the language changes the button, the settings shown and the code written, and is remembered after a reload. A branching net in Python is refused with a clear message.

## The notebook it writes

**Download .nb** saves a notebook of Code cells with these sections:

1. **The diagram:** the drawing and settings as JSON, so the drawing can be opened again in the editor, and `netSpec`, the net in plain terms.
2. **Data:**
   - SubjectNet's template data: the notebook evaluates `SubjectNet.nb` first, so save it beside that file or change the path in the settings.
   - Your own data: you define the named variables first.
   With Feature and Hash elements, the notebook also writes `diagramFeatures` and `diagramVector` for the features drawn.
3. **Version B:** the `NetChain` or `NetGraph`, its weight count, and `NetTrain` with the settings chosen.
4. **Version A:** the layer sizes and activations from the drawing, and our own forward pass, backpropagation, Adam and gradient check. This version covers chains only.
5. **Checks:**
   - weights in the drawing against weights in each trained net;
   - training time;
   - test accuracy;
   - the gradient check;
   - how often A and B agree.
   With SubjectNet's data, the trained nets are also offered as subject checks for `MotionParse`.

The training settings are epochs, batch size, learning rate (Adam), L2 and seed. The defaults are SubjectNet's: 12, 64, 0.005, 0.0001 and 1234.

## Tested

- **SubjectNet:** the editor counts 65,634 weights, and Wolfram's `NetChain` has 65,634.
- **Version A against SubjectNet's own version A:** with the same settings, the generated version A was trained in the Wolfram kernel beside SubjectNet's `trainA`, on the same data (300 vectors of 2,048, two epochs). The weights and the losses were identical, a difference of 0. The gradient check gave 3.9 × 10⁻¹².
- **The hashing:** the generated `diagramVector` equals SubjectNet's `featureVector` on 400 records, 101 of them with no words of their own.
- **A deeper chain** (20 → 6 Tanh → 5 Sigmoid → 4 linear → 3 classes) trained in both versions. Both count 200 weights, and the gradient check gave 1.3 × 10⁻¹¹.
- **A branching net** (two layers side by side, joined, dropout, softmax) was written as a `NetGraph` and trained. It has 2,499 weights, as the editor counted.
- **The page** was run in headless Chrome:
  - drawing, editing units, adding and wiring a layer, undo, Example, Download .nb and Export SVG all work, with no errors in the console;
  - every cell of the downloaded notebook parses, and the file is ASCII, with other characters written as `\:xxxx`.

## Not yet

- Version A for nets that branch, and dropout in version A.
- ONNX between the two languages, as draft 8 describes.
- Branching nets and dropout in the Python version, and sequence nets (attention) in our own Python code.
- **Code → Diagram:** drawing a net from its code or from the trained net itself, such as owNet in `unit4_build_your_own_nets.nb`.

By Dara O Shayda and Hikari Noor Hoshino (星野ヌール)
AI System Programming Group

© Computational Classnotes · CC BY-NC-SA 4.0
