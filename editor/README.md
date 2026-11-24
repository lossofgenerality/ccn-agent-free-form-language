# CCN Net Diagrams: the editor

`net-diagram-editor.html` is a single self-contained page that runs offline in a browser. Open it, draw a small neural net, and press **Diagram → Code**. The page writes a Wolfram notebook (`.nb`) that builds the net drawn and trains it in two versions:

- **A, our own code:** the forward pass, backpropagation and Adam are written out, and no Wolfram neural-net function is used.
- **B, Wolfram's code:** `NetChain` (or `NetGraph` when the drawing branches) with `NetTrain`.

The page keeps the structure of the CCN String Diagrams editor (`lossofgenerality/ccn-string-diagrams`): the canvas, drawing wires from port to port, moving, zooming, panning, undo, the inspector, Save and Open as JSON, and Export SVG. The string-diagram mathematics is replaced by the elements of a net.

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
- Python export (PyTorch, and ONNX between the two languages, as draft 8 describes).
- **Code → Diagram:** drawing a net from its code.

By Dara O Shayda and Hikari Noor Hoshino (星野ヌール)
AI System Programming Group

© Computational Classnotes · CC BY-NC-SA 4.0
