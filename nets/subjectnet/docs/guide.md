---
title: "SubjectNet: User Guide"
subtitle: "A small net that keeps the motion parts of a sentence that are about the object, in Wolfram and in Python"
author: "Computational Classnotes"
date: "25 November 2026"
---

# SubjectNet: User Guide

*A small net that keeps the motion parts of a sentence that are about the object, in Wolfram and in Python*

Computational Classnotes · 25 November 2026

**Companion to:** the CCN agent free-form language (`ccn-agent-free-form-language`) and the CCN Net Lab catalogue (https://lossofgenerality.github.io/ccn-nets/free-form/subjectnet/)

**Files covered:** `nets/SubjectNet.nb`, `nets/SubjectNet_as_matrices.nb`, `motion/MotionPhrases.nb`, `python/ccn_nets/` (`nn.py`, `motion.py`, `subjectnet.py`), `nets/subjectnet/train/train.py`

© Computational Classnotes · CC BY-NC-SA 4.0

## Contents

1. What it is
2. Before you start
3. Finding your way around
4. The mathematics
5. The configuration, part by part
6. Using it in Wolfram
7. Using it in Python
8. Training it yourself
9. Results
10. Wolfram and Python side by side
11. A complete worked session
12. Messages you may see
13. Quick reference card
14. Files
15. Credits, copyright and licence

---

## 1. What it is

The motion reader (`MotionPhrases` in Wolfram, `ccn_nets.motion` in Python) turns spoken English such as "rise 4 while spinning counterclockwise then move right 3" into motions and a pose. Reading whole paragraphs, it sometimes took a motion verb about *something else* for a motion of the object:

- "the camera holds on the kettle for a beat";
- "visitors often say the experience turns their sense of scale";
- "Mia laughed and turned to her brother".

SubjectNet looks at each motion part the reader finds and answers **object** (keep it) or **other** (set it aside). It is a dense net with one hidden layer: 2,048 inputs, 32 hidden units and 2 outputs, 65,634 numbers in all. It plugs into the reader as a single option.

There are three versions, built from the same design, data and settings:

| Version | Where | Neural-net code |
|---|---|---|
| A | `nets/SubjectNet.nb` | our own, written out with `Dot`, `Exp`, `Log`, `Total`, `Transpose`, `UnitStep`; no Wolfram neural-net function |
| B | `nets/SubjectNet.nb` | Wolfram's `NetChain` and `NetTrain` |
| Python | `python/ccn_nets/` | our own (`nn.py`); NumPy holds the arrays, no neural-net library |

All three make the same decisions on the paragraph and hard-sentence tests.

## 2. Before you start

### What you need

| For | You need |
|---|---|
| Wolfram | Wolfram 14 or later (the numbers here are from Wolfram 15.0.1). Nothing else. |
| Python | Python 3.9 or later and NumPy. Nothing else. |
| The 3D viewer | Any current browser |

### Opening it

**Wolfram.** Open `motion/MotionPhrases.nb` and evaluate it, then open `nets/SubjectNet.nb` and evaluate it from top to bottom (its first cell loads `MotionPhrases.nb` if needed). Choose Evaluation ▸ Quit Kernel ▸ Local first, so no old values are left over. Evaluating writes nothing to the Wolfram Cloud.

**Python.**

```
cd python
python3 -m ccn_nets.subjectnet              # make the data, train, run the tests (about 1 s)
python3 -m unittest discover -s tests -v    # the tests against Wolfram's results
```

**On the web.** The catalogue page shows the net, its run and its matrices; the 3D page lets you glide over the weights.

## 3. Finding your way around

| You want to | Go to |
|---|---|
| Use the check in your own reading | §6 (Wolfram) or §7 (Python) |
| Understand what the net computes | §4 and §5 |
| See it as matrices | `nets/SubjectNet_as_matrices.nb`, and `viz/matrices.png` |
| Train it again, or on your own data | §8 |
| Know how far to trust it | §9 |
| Change the design | the CCN Net Diagram Editor, Examples ▸ SubjectNet |

## 4. The mathematics

A motion part becomes a vector **x** of 2,048 zeros and ones (§5). The net computes

$$
\mathbf h=\max(0,\ W_1^{\mathsf T}\mathbf x+\mathbf b_1),\qquad
\mathbf p=\operatorname{softmax}(W_2^{\mathsf T}\mathbf h+\mathbf b_2),\qquad
\operatorname{softmax}(\mathbf z)_k=\frac{e^{z_k-\max z}}{\sum_j e^{z_j-\max z}} ,
$$

with W₁ of size 2048 × 32 and W₂ of size 32 × 2. The answer is "object" if p₁ > p₂ and "other" otherwise.

Training minimises the cross-entropy with L2 regularisation over a batch of n rows,

$$
L=-\frac1n\sum_{i}\sum_k y_{ik}\log p_{ik}\;+\;\frac{\lambda}{2}\left(\lVert W_1\rVert^2+\lVert W_2\rVert^2\right),\qquad \lambda=10^{-4}.
$$

The gradients, as written out in version A and in Python:

```
dZ2 = (P − Y) / n
dW2 = A1ᵀ·dZ2 + λ·W2        db2 = column sums of dZ2
dZ1 = (dZ2·W2ᵀ) × [Z1 > 0]
dW1 = Xᵀ·dZ1 + λ·W1         db1 = column sums of dZ1
```

Adam updates each array θ with β₁ = 0.9, β₂ = 0.999, ε = 10⁻⁸ and learning rate 0.005:

$$
m\leftarrow\beta_1 m+(1-\beta_1)g,\quad v\leftarrow\beta_2 v+(1-\beta_2)g^2,\quad
\theta\leftarrow\theta-\eta\,\frac{m/(1-\beta_1^t)}{\sqrt{v/(1-\beta_2^t)}+\varepsilon}.
$$

Initial weights are normal with He scaling (standard deviation √(2/fan-in)); biases start at 0.

**Gradient check.** Each derivative is compared with a centred finite difference. The largest difference is 6.7 × 10⁻¹² in Wolfram version A and 1.7 × 10⁻¹¹ in Python.

## 5. The configuration, part by part

### The features

The reader hands each motion part over as a record (`MotionSubject` in Wolfram, `motion.motion_subject` in Python) with five fields. Each field gives short features:

| Field | Features | Example for "turned to her brother", after "mia laughed" |
|---|---|---|
| Own: the words before the verb | `o:<word>`, and `oL:<last word>`; `own:none` if there are none | `own:none` |
| Prev: the end of the part before, used only when Own is empty | `p:<word>` for its last four words | `p:mia`, `p:laughed` |
| Join: how the part was joined to the one before | `j:<and, comma, while, then, start>` | `j:and` |
| Verb | `v:<verb>` | `v:turned` |
| After: the first words after the verb | `a:<word>` for four words, and the pair `a2:<w1>_<w2>` | `a:to`, `a:her`, `a:brother`, `a2:to_her` |

Each feature is hashed with CRC32 into one of 2,048 slots, and the slot is set to 1. Python's `zlib.crc32` and Wolfram's `Hash[…, "CRC32"]` give identical slots.

### The layers and their numbers

| Part | Shape | Numbers |
|---|---|---|
| W₁ | 2048 × 32 | 65,536 |
| b₁ | 32 | 32 |
| ReLU | | 0 |
| W₂ | 32 × 2 | 64 |
| b₂ | 2 | 2 |
| softmax | | 0 |
| **Total** | | **65,634** |

### The settings

| Setting | Value |
|---|---|
| Hidden units | 32, ReLU |
| Learning rate | 0.005 (Adam) |
| L2 | 10⁻⁴ |
| Batch | 64 |
| Passes | 12 |
| Seed | 1234 |

### The data

No conversational-construct labelled anything, and no outside data was used. The notebook writes the sentences itself from 19 templates, and each template carries its label. The nouns, names, relations and abstract words used for testing (teapot, kite, sphere, gripper, Mia, brother…) never appear in training, so the tests show whether the net learnt sentence shape rather than words. There are 2,000 training parts and 600 test parts.

## 6. Using it in Wolfram

### Running

After `motion/MotionPhrases.nb` and `nets/SubjectNet.nb` are evaluated, the two checks are defined:

```wolfram
MotionParse[text, "SubjectCheck" -> SubjectCheckA]    (* version A, our own code *)
MotionParse[text, "SubjectCheck" -> SubjectCheckB]    (* version B, NetTrain *)
MotionFind[text, "SubjectCheck" -> SubjectCheckA]     (* the parts only *)
MotionSubject[part]                                   (* what a check sees of one part *)
```

Without the option the reader works as before, with no check.

### The functions

| Function | Gives |
|---|---|
| `MotionFind[text, opts]` | the motion parts in each step, the parts set aside with their reasons, and the figures of speech |
| `MotionParse[text, opts]` | the full reading: steps, parts, kinds, axes, amounts, assumptions and corrections |
| `MotionTransform[text, t, opts]` | the pose at time t as a 4 × 4 matrix |
| `MotionSubject[part]` | the record a check sees: Own, Verb, After, Prev, Join |
| `SubjectCheckA[record]`, `SubjectCheckB[record]` | "object" or "other" |

### Reading the output

`MotionFind` returns an association with three keys:

| Key | Holds |
|---|---|
| `"Motions"` | one list of part texts per step |
| `"Set aside"` | each part not kept, with its reason: "no motion words", or "about something else (subject check)" |
| `"Figures of speech"` | parts set aside by the list of figures of speech before any check sees them |

### Examples

The Python reader was checked against Wolfram on 116 texts and gives identical records, parts and reasons (§10), so these results hold for both.

| Input | With `SubjectCheckA` | Without a check |
|---|---|---|
| `"Mia laughed and turned to her brother. The kite climbed 6 metres."` | Motions: "the kite climbed 6 metres". Set aside: "mia laughed" (no motion words), "turned to her brother" (about something else) | Motions: "turned to her brother", "the kite climbed 6 metres" |
| `"slide it right 2 units"` (one part) | object, p = (0.9999, 0.0001) | |
| `"mia turned to her brother"` (one part) | other, p = (0.0069, 0.9931) | |

**Try this.** Read "The cameraman slowly moves left" with the check. It is kept, wrongly: "cameraman" was never in the templates, only "camera". §9 lists every known miss.

### Rules of the kernel

- Evaluating `SubjectNet.nb` trains both versions afresh (about 1 s each). Nothing is saved to the Cloud.
- The check is an option, not a change to the reader: leave it out and the reader is exactly as it was.
- Versions A and B may be swapped freely; they agreed on every decision in every test.

## 7. Using it in Python

### Running

```python
from ccn_nets import motion, subjectnet
from ccn_nets.nn import Net, train

out = subjectnet.run()                       # make the data, train, print the tests
net = out["net"]
check = subjectnet.subject_check(net)        # a function: record → "object" or "other"

motion.motion_find("Mia laughed and turned to her brother. The kite climbed 6 metres.",
                   subject_check=check)
```

### The functions

| Function | Gives |
|---|---|
| `motion.motion_find(text, subject_check=None, ...)` | the same three keys as `MotionFind` |
| `motion.motion_parse(text, ...)` | the full reading, as `MotionParse` |
| `motion.motion_transform(text, t, ...)` | the pose at time t, a 4 × 4 NumPy array |
| `motion.motion_subject(part)` | the record a check sees |
| `subjectnet.run(epochs=12, batch_size=64, lr=0.005, l2=1e-4, seed=1234, hidden=32, verbose=True)` | trains and tests; returns a dict with `"net"` and the results |
| `subjectnet.subject_check(net)` | the check, for `subject_check=` |
| `subjectnet.parts_of(sentence)` | the records of a sentence's parts |
| `subjectnet.feature_vector(record)` | the 2,048 zeros and ones |
| `Net(sizes, activations)` | any small dense net; `.initialise(seed)`, `.forward`, `.probabilities`, `.gradients`, `.save(path)`, `Net.load(path)` |
| `train(net, x, y, epochs, batch_size, lr, l2)` | our own Adam training; returns the loss history |

### Reading the output

`subjectnet.run()` prints, on 25 November 2026 in this workspace:

```
Training data (parts): 2000
Test data (parts): 600
Making the data, s: 0.24
Training time, s: 0.67
Loss, first and last epoch: [0.0095, 0.0031]
Gradient check, largest difference: 1.6605550268167235e-11
Test 1: templates with unseen words, accuracy: 0.995
Test 1: 'other' precision and recall: (1.0, 0.9864253393665159)
Test 2: paragraph parts, accuracy: 47 of 47
Test 3: hard sentences, accuracy: 21 of 24
Test 4: paragraphs ending right: 12 of 12 (without the check: 12)
Test 4: paragraphs right step by step: 12 of 12 (without the check: 9)
Time to check one part, ms: 0.029
Numbers in the net: 65634
Parts wrong (paragraphs and hard sentences): ['the lantern drifts upward 2 metres', 'my heart sank 2 times that day', 'the cameraman slowly moves left']
```

### Examples

```python
>>> for s in ["slide it right 2 units", "mia turned to her brother"]:
...     for p in subjectnet.parts_of(s):
...         print(s, "->", check(p), net.probabilities(subjectnet.feature_vector(p)[None, :])[0].round(4))
slide it right 2 units -> object [0.9999 0.0001]
mia turned to her brother -> other [0.0069 0.9931]

>>> motion.motion_transform("rise 4 while spinning counterclockwise then move right 3", 1).round(3)
[[ 1.  0.  0.  3.]
 [-0.  1.  0.  0.]
 [ 0.  0.  1.  4.]
 [ 0.  0.  0.  1.]]
```

The pose ends 3 to the right and 4 up, with a full turn about the vertical axis, so the rotation part is the identity.

**Try this.** `motion.motion_parse("move along the path while spinning counterclokwise and move upwards")`. The misspelling is corrected (`'Corrections': [('counterclokwise', 'counterclockwise')]`) and the assumptions are listed: "no axis: z (vertical) assumed", "no amount: one full turn assumed".

### A net of your own

```python
net = Net([20, 8, 3], ["Tanh"]).initialise(seed=1)       # sizes, one activation per hidden layer
history = train(net, x, y, epochs=12, batch_size=64, lr=0.005, l2=1e-4)   # x: rows, y: one-hot
net.save("net.npz"); net2 = Net.load("net.npz")
```

The activations are ReLU, Tanh and Sigmoid. The output is softmax with cross-entropy.

## 8. Training it yourself

| Way | How |
|---|---|
| Wolfram, both versions | evaluate `nets/SubjectNet.nb` |
| Python | `python3 -m ccn_nets.subjectnet` |
| A recorded run for the Net Lab | `python3 nets/subjectnet/train/train.py` writes `runs/<date>-<name>/` (never overwritten): settings, loss per epoch, results, weights |
| From the diagram | open the editor, Examples ▸ SubjectNet, change it, and generate a Wolfram notebook or a Python script (Language ▸ Python) |

To train on your own data in Python, write `my_data.py` with `train_records` and `test_records` (lists of (record, class)), as the editor's script explains.

**What changes the results.** More templates, or real labelled parts from motion reports, help more than a bigger net. Test 3 is the honest measure of generalisation.

## 9. Results

| | Python | Wolfram A | Wolfram B |
|---|---|---|---|
| Numbers in the net | 65,634 | 65,634 | 65,634 |
| Training time | 0.7–0.8 s | 1.0 s | 1.0 s |
| Test 1: 600 template parts with unseen words | 99.5 % | 100 % | 100 % |
| Test 2: the 47 motion parts in 12 paragraphs | 47 of 47 | 47 of 47 | 47 of 47 |
| Test 3: 24 parts from 23 harder sentences | 21 of 24 | 21 of 24 | 21 of 24 |
| Test 4: paragraphs right step by step | 12 of 12 (9 without) | 12 of 12 | 12 of 12 |
| Test 5: 557 phrase variants, check on | | 546 (547 without) | 546 |
| Time to check one part | 0.03 ms | 0.40 ms | 0.86 ms |

**The known misses (Test 3), the same in all three versions:**

- "The lantern drifts upward 2 metres": set aside. "Lantern" was never seen, and "drifts" appears mostly in camera templates.
- "My heart sank 2 times that day": kept. This figure of speech is not in the templates.
- "The cameraman slowly moves left": kept. Only "the camera" was seen.

**Test 5, one new miss:** "about the x axis spin counterclockwise 270 degrees", with no comma. The words before "spin" look like a subject. With the comma it is read correctly.

**How far to trust these numbers.** Test 1 uses the training templates with new words, so it is easy. Test 2 is real text but has only three "other" parts. Test 3, 88 %, is the honest measure, on a small set written as a test. Python's Test 1 differs slightly because its random draws of the template sentences are not Wolfram's.

## 10. Wolfram and Python side by side

| Check (24 November 2026, against Wolfram itself) | Result |
|---|---|
| Training arithmetic: the same starting weights and batches as version A, five epochs | losses and weights differ by about 10⁻¹⁶ |
| Feature hashing: `zlib.crc32` against `Hash[…, "CRC32"]` | identical slots |
| The reader on 116 texts | identical records, parts and reasons |
| The poses: 12 phrases at t = 1 and 0.37, 12 paragraphs at t = 1 | largest difference 5 × 10⁻¹⁰ |
| Gradient checks | 1.7 × 10⁻¹¹ (ReLU), 1.1 × 10⁻¹¹ (Tanh, Sigmoid and linear layers) |

The Wolfram results are kept in `python/tests/wolfram_reference.json`; `python3 -m unittest discover -s tests` repeats the comparison without Wolfram (11 tests, all pass).

**Misspellings without a dictionary.** Wolfram decides what is a real word with `DictionaryWordQ`. Python uses `ccn_nets/data/near_words.txt`, the 1,799 real words within one or two letters of a motion word, made by `tools/NearWords.nb`. "fails" is one of them, so it is never turned into "falls". Evaluate `tools/NearWords.nb` again whenever the motion vocabulary changes.

## 11. A complete worked session

In Python (the Wolfram calls are in the comments):

```python
from ccn_nets import motion, subjectnet
import numpy as np

net = subjectnet.run(verbose=False)["net"]            # SubjectNet.nb trains SubjectCheckA and B
check = subjectnet.subject_check(net)

text = "Mia laughed and turned to her brother. The kite climbed 6 metres."
motion.motion_find(text)                               # MotionFind[text]
# {'Motions': [['turned to her brother'], ['the kite climbed 6 metres']],
#  'Set aside': [{'Text': 'mia laughed', 'Reason': 'no motion words'}], 'Figures of speech': []}

motion.motion_find(text, subject_check=check)          # MotionFind[text, "SubjectCheck" -> SubjectCheckA]
# {'Motions': [['the kite climbed 6 metres']],
#  'Set aside': [{'Text': 'mia laughed', 'Reason': 'no motion words'},
#                {'Text': 'turned to her brother', 'Reason': 'about something else (subject check)'}],
#  'Figures of speech': []}

p = subjectnet.parts_of("mia turned to her brother")[0]
check(p), net.probabilities(subjectnet.feature_vector(p)[None, :])[0].round(4)
# ('other', array([0.0069, 0.9931]))

net.save("subjectnet.npz")                              # four plain arrays: W1, b1, W2, b2
```

What happened: without the check, "turned to her brother" was read as a turn of the object. With it, SubjectNet saw no words before the verb, so it looked at the end of the part before ("mia laughed"), the join "and", the verb "turned" and "to her brother" after it, and answered "other" with probability 0.993.

## 12. Messages you may see

| Message | Meaning | What to do |
|---|---|---|
| Wolfram: `SubjectCheckA` returned unevaluated | `SubjectNet.nb` has not been evaluated | evaluate `motion/MotionPhrases.nb`, then `nets/SubjectNet.nb` |
| Wolfram: `MotionSubject` undefined | an older `MotionPhrases.nb` | use the one in this repository, which has the `"SubjectCheck"` option |
| Python: `ModuleNotFoundError: ccn_nets` | not run from `python/` | `cd python`, or add it to `PYTHONPATH` |
| Python: `TypeError: string indices must be integers` from `motion_subject` | a string was passed | pass a part record, as `subjectnet.parts_of(sentence)` gives |
| A part "set aside: no motion words" | the part has no motion verb | not a SubjectNet decision |

## 13. Quick reference card

```
WOLFRAM                                           PYTHON  (cd python)
<< motion/MotionPhrases.nb, then SubjectNet.nb    from ccn_nets import motion, subjectnet
MotionFind[t, "SubjectCheck" -> SubjectCheckA]    motion.motion_find(t, subject_check=check)
MotionParse[t, "SubjectCheck" -> SubjectCheckB]   motion.motion_parse(t, subject_check=check)
MotionTransform[t, 1]                             motion.motion_transform(t, 1)
MotionSubject[part]                               motion.motion_subject(part)
                                                  net = subjectnet.run()["net"]
                                                  check = subjectnet.subject_check(net)
                                                  python3 -m ccn_nets.subjectnet
                                                  python3 -m unittest discover -s tests

NET  2048 hashed features → 32 ReLU → 2 softmax  ·  65,634 numbers
     Adam 0.005, L2 1e-4, batch 64, 12 passes, seed 1234
```

## 14. Files

| File | Holds |
|---|---|
| `nets/SubjectNet.nb` | the templates, the features, versions A and B, all five tests, the comparison |
| `nets/SubjectNet_as_matrices.nb` | the trained net written as matrices, typeset with `MatrixForm` |
| `nets/SubjectNetReport.md` | the report: our own net against Wolfram's |
| `motion/MotionPhrases.nb` | the reader, with the `"SubjectCheck"` option and `MotionSubject` |
| `python/ccn_nets/nn.py`, `motion.py`, `subjectnet.py` | the Python version |
| `python/tests/` | the tests against Wolfram's results |
| `nets/subjectnet/` | the Net Lab folder: `net.json`, `card.json`, `train/train.py`, `runs/`, `viz/` (`viewer-data.json`, `matrices.png`), `writeup.md`, this guide |

## 15. Credits, copyright and licence

By Dara O Shayda and Hikari Noor Hoshino (星野ヌール)
AI System Programming Laboratory

© Computational Classnotes · CC BY-NC-SA 4.0
