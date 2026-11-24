<!-- © Computational Classnotes · CC BY-NC-SA 4.0 -->
# SubjectNet: our own net against Wolfram's, on one job

*24 November 2026. Measured on Wolfram 15.0.1 (Linux, a cloud evaluation kernel), not on your Mac, so the times are a guide only.*

## The job

Reading paragraphs, `MotionPhrases` sometimes took a motion verb about something else for a motion of the object. The three cases were:
- "the camera holds on the kettle for a beat";
- "visitors often say the experience turns their sense of scale";
- "Mia laughed and turned to her brother".

SubjectNet is a small neural net that looks at each motion part and answers **object** (keep it) or **other** (set it aside). It plugs in as one option:

```wolfram
MotionParse[text, "SubjectCheck" -> SubjectCheckA]    (* or SubjectCheckB *)
```

## Two versions, built the same way

| | Version A: our own | Version B: Wolfram's |
|---|---|---|
| The net | 2048 inputs → 32 hidden units (max(0, x)) → 2 outputs (softmax) | the same: `NetChain[{LinearLayer[32], Ramp, LinearLayer[2], SoftmaxLayer[]}]` |
| Forward pass, backpropagation, Adam | **written out in this notebook**, using only `Dot`, `Exp`, `Log`, `Total`, `Transpose`, `UnitStep` | `NetTrain` with `"ADAM"` |
| Wolfram neural-net functions used | **none** | `NetChain`, `NetTrain`, `NetDecoder` and the layers |
| Settings | learning rate 0.005, L2 10⁻⁴, batches of 64, 12 passes, seed 1234 | the same |
| Data and features | the same 2,000 training parts, the same features | the same |

The gradients in version A were checked against finite differences. The largest difference was **6.7 × 10⁻¹²**.

### Where the data came from

**No conversational-construct labelled anything, and no outside data was used.** The notebook writes the training sentences itself, from templates, and each template carries its own label:

- **19 templates.** For example, about the object: "the {thing} should {imperative}" and "to inspect the {thing}, {imperative}". About something else: "{name} {laughed} and turned to {her} {relation}", "{camera} holds on the {thing}" and "{the news} turned {his} {mood}".
- **Separate words for training and testing.** The test nouns, names, relations and abstract words (teapot, kite, sphere, gripper, Mia, brother, the experience, sense of scale…) never appear in training, so the test shows whether the net learnt sentence shape rather than words.
- **Read by the real code.** Every sentence goes through `MotionFind`, so the net sees motion parts exactly as `MotionParse` hands them over.
- **Size:** 2,000 training parts (1,328 object, 672 other) and 600 test parts (401 and 199). Writing the 2,000 takes 4.6 s.
- **Some overlap with the paragraphs:** a few words in the paragraph test are also in the training lists ("drone", "robot", "camera"), because they are ordinary words for this job.

### What the net sees

Each part becomes a list of short features, hashed into 2,048 slots of 0 or 1:
- the words before the motion verb ("o:the", "o:camera");
- when there are none, the last words of the part before it in the sentence ("p:mia", "p:laughed");
- how the part was joined to the one before it (and, comma, while, then);
- the verb itself;
- the first words after the verb ("a:to", "a:her", and the pair "a2:to_her").

## The algorithm of version A, in pseudocode

```
FORWARD(W1, b1, W2, b2, X):            -- X: a batch of feature vectors, one per row
    Z1 ← X·W1 + b1;  A1 ← max(0, Z1)
    P  ← softmax(A1·W2 + b2)           -- per row: exp(z − max z) / sum

BACKWARD(X, Y, P):                     -- Y: the right answers, one-hot; n rows
    dZ2 ← (P − Y) / n
    dW2 ← A1ᵀ·dZ2 + λ·W2;   db2 ← column sums of dZ2
    dZ1 ← (dZ2·W2ᵀ) × [Z1 > 0]
    dW1 ← Xᵀ·dZ1 + λ·W1;    db1 ← column sums of dZ1

TRAIN:
    W1, W2 ← random normal (He scaling), seed 1234;  b1, b2 ← 0;  m, v ← 0
    repeat 12 times: shuffle; for each batch of 64:
        t ← t + 1;  g ← BACKWARD(...)
        m ← 0.9·m + 0.1·g;   v ← 0.999·v + 0.001·g²
        θ ← θ − 0.005 · (m / (1 − 0.9ᵗ)) / (√(v / (1 − 0.999ᵗ)) + 10⁻⁸)

CHECK(part) = "object" or "other", whichever output of FORWARD is larger
```

## Results

| | Version A: our own | Version B: Wolfram's |
|---|---|---|
| Test 1: 600 template parts with unseen words | **100%** | **100%** |
| "Other" found (precision / recall), test 1 | 1.00 / 1.00 | 1.00 / 1.00 |
| Test 2: the 47 motion parts in the 12 paragraphs | **47 of 47** | **47 of 47** |
| Test 3: 24 parts from 23 harder sentences in new shapes | 21 of 24 | 21 of 24 |
| Test 4: paragraphs right step by step, with the check on | **12 of 12** (was 9 without it) | **12 of 12** |
| Test 5: the 557 phrase variants, with the check on | 546 (547 without it) | 546 |
| Training time | 1.0 s | 1.0 s |
| Time to check one part | **0.40 ms** | 0.86 ms |
| Numbers in the net | 65,634 | 65,634 |
| Code to build and train it | about 40 lines, all readable | about 5 lines |
| Wolfram neural-net functions used | none | NetChain, NetTrain and the layers |

**The two versions agreed on every single decision in every test.** With the same design, data and settings, writing the net ourselves cost nothing in accuracy. Ours was also twice as fast per part, because there is no net object to call.

### What each one got wrong

Both versions made exactly the same mistakes.

- **Test 3, three of 24:**
  - "The lantern drifts upward 2 metres" was set aside. "Lantern" was never seen, and "drifts" appears mostly in the camera templates ("the camera drifts across").
  - "My heart sank 2 times that day" was kept. This kind of figure of speech isn't in the templates.
  - "The cameraman slowly moves left" was kept. "Cameraman" was never seen; only "the camera" was.
  
  One sentence, "the detective circled back to the first clue", never reached the net, because the list of figures of speech had already set it aside.
- **Test 5, one new miss:** "about the x axis spin counterclockwise 270 degrees", a run-on variant with no comma. The words before "spin" ("about the x axis") look like a subject, so the part was set aside. With the comma ("about the x axis, spin…") it is read right.

### How far to trust these numbers

- **Test 1 is easy:** it uses the same templates with different words. It shows the net learnt sentence shape, not that it understands English.
- **Test 2 is real text,** but it has only three "other" parts.
- **Test 3 is the honest measure of generalisation:** 88% on shapes the templates never had. It is small (24 parts), and I wrote these sentences myself as a test, just as I wrote the paragraphs.
- **The way to improve it** is more templates, or real labelled parts from the motion reports, rather than a bigger net.

## Our own net against Wolfram's: beyond the numbers

| | Version A: our own | Version B: Wolfram's |
|---|---|---|
| Can be read and checked line by line | yes: every step is in the notebook, and the gradient check is included | the training is inside `NetTrain` |
| Runs elsewhere | the weights are four plain arrays: the same 10 lines of arithmetic run in Python or JavaScript | through ONNX export (draft 8 tested a Wolfram-to-Python ONNX round trip), or Wolfram only |
| Grows to bigger nets | each new kind of layer must be written out by hand, with its gradient | any layer Wolfram has (embeddings, attention, LSTM), with GPU training |
| Fits draft 8's "own nets" | yes, and the most portable | yes: the planned exchange through ONNX |

**A suggestion:** keep version A as the reference for small nets like this one, since it is transparent, tiny and portable. Use version B when a job needs layers we'd rather not write by hand. Either way, keep both versions trained on the same data, as here, so each checks the other.

## Files

- `nets/SubjectNet.nb`: the template data, the features, both versions, all five tests, and the comparison table. Evaluate it after `motion/MotionPhrases.nb` (its first cell loads that).
- `motion/MotionPhrases.nb`: the new `"SubjectCheck"` option and `MotionSubject`, which shows what a check sees of one part.

The notebook holds the code that was run for these numbers, arranged into cells; a few local names differ from the test runs. It hasn't yet been opened in Mathematica itself.

---

© Computational Classnotes · CC BY-NC-SA 4.0
