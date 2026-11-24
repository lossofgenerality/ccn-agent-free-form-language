# The Python version

A complete Python version of the motion-phrase reader and of SubjectNet. Every neural-net piece is our own code: dense layers, ReLU, Tanh, Sigmoid, softmax, cross-entropy with L2, the forward pass, backpropagation, Adam, the initial weights and the gradient check. No neural-net library is used. NumPy holds the arrays and does their arithmetic (dot products, exp, log, sums), as `Dot`, `Exp` and `Total` do in the Wolfram version A.

It needs Python 3.9 or later and NumPy, and nothing else.

```
cd python
python3 -m ccn_nets.subjectnet              # make the data, train SubjectNet, run the four tests
python3 -m unittest discover -s tests -v    # the tests against Wolfram's results
```

## The files

| File | What it is |
|---|---|
| `ccn_nets/nn.py` | Our own neural-net code: `Net` (dense layers with an activation each and softmax at the end), `softmax_rows`, `cross_entropy`, `Net.forward`, `Net.gradients` (backpropagation), `Adam`, `train`, `gradient_check`, `Net.save` and `Net.load` |
| `ccn_nets/motion.py` | A port of `motion/MotionPhrases.nb`: tidying of dictated speech, steps and parts, the reading of each part, the subject records (`motion_subject`), `motion_find`, `motion_parse`, and `motion_transform`, which gives the pose as a 4 × 4 matrix |
| `ccn_nets/subjectnet.py` | A port of `nets/SubjectNet.nb`: the templates (training and test words kept apart), `make_data`, the features hashed into 2,048 slots, training, the subject check for the reader, and the four tests |
| `ccn_nets/data/subjectnet_tests.json` | The 12 paragraphs, their short phrases and the 24 hard sentences, taken from `SubjectNet.nb` |
| `ccn_nets/data/near_words.txt` | The 1,799 real English words within the spelling-correction distance of a motion word (see below) |
| `tools/NearWords.nb` | Remakes that list from Wolfram's dictionary |
| `tests/test_ccn_nets.py`, `tests/wolfram_reference.json` | The tests, and the Wolfram results they compare with |

## Using it

```python
from ccn_nets import motion, subjectnet
from ccn_nets.nn import Net, train

motion.motion_find("move along the path while spinning counterclokwise and move upwards")
motion.motion_transform("rise 4 while spinning counterclockwise then move right 3", 1)   # the pose at the end

net = subjectnet.run()["net"]                                    # train SubjectNet and print the tests
check = subjectnet.subject_check(net)
motion.motion_find("Mia laughed and turned to her brother. The kite climbed 6 metres.", subject_check=check)

net = Net([20, 8, 3], ["Tanh"]).initialise(seed=1)                # any small net: sizes, activations
history = train(net, x, y, epochs=12, batch_size=64, lr=0.005, l2=1e-4)   # x: rows of features, y: one-hot
net.save("net.npz")
```

## The same as the Wolfram version

These checks were run against Wolfram itself on 24 November 2026. The Wolfram results are kept in `tests/wolfram_reference.json`, so the comparison can be repeated without Wolfram.

| Check | Result |
|---|---|
| **Training arithmetic:** the same starting weights and batches as Wolfram's version A, five epochs | Losses and weights differ by about 10⁻¹⁶, the last bit of a floating-point number |
| **Feature hashing:** Python's CRC32 against `Hash[…, "CRC32"]` | Identical slots |
| **The reader:** 116 texts, namely the 12 paragraphs, their 12 short phrases, the 24 hard sentences, 60 template sentences and 8 sentences with dictation slips | Identical records, motion parts and reasons for setting parts aside, in every text |
| **The poses:** the 12 short phrases at times 1 and 0.37, and the 12 paragraphs at time 1 | The largest difference is 5 × 10⁻¹⁰, the rounding of the Wolfram values |
| **Gradient checks** | 1.7 × 10⁻¹¹ (ReLU), 1.1 × 10⁻¹¹ (Tanh, Sigmoid and linear layers) |

## SubjectNet: Python and Wolfram compared

| | Python (our own code) | Wolfram A (our own code) | Wolfram B (NetTrain) |
|---|---|---|---|
| Weights | 65,634 | 65,634 | 65,634 |
| Training time | 0.8 s | 1.0 s | 1.0 s |
| Test 1: templates with unseen words | 99.5% | 100% | 100% |
| Test 2: paragraph parts | 47 of 47 | 47 of 47 | 47 of 47 |
| Test 3: hard sentences | 21 of 24 | 21 of 24 | 21 of 24 |
| Test 4: paragraphs right step by step | 12 of 12 (9 without the check) | 12 of 12 | 12 of 12 |
| Time to check one part | 0.03 ms | 0.40 ms | 0.86 ms |

Test 3 goes wrong on the same three sentences in all three: the lantern, the heart and the cameraman.

Test 1 differs slightly because Python's random numbers are not Wolfram's. The template sentences, and so the training and test data, are therefore different draws from the same templates. In this draw, Python's net called three of the 221 "other" parts "object".

## The word list

When a word is misspelt, the reader replaces it with the nearest motion word ("counterclokwise" becomes "counterclockwise"), but it never changes a real word. Wolfram decides what counts as a real word with `DictionaryWordQ`, and Python has no dictionary of its own.

Only the real words that lie within one or two letters of a motion word could ever be wrongly corrected, so `tools/NearWords.nb` lists exactly those from Wolfram's dictionary. "fails" is one: it is never turned into "falls". This reproduces Wolfram's behaviour exactly, with no extra package.

Evaluate `tools/NearWords.nb` again whenever the motion vocabulary changes.

## Not yet

- ONNX export, so that a net trained here can be read by Wolfram, and the other way round, as draft 8 describes.
- Python output from the net diagram editor.

By Dara O Shayda and Hikari Noor Hoshino (星野ヌール)
AI System Programming Group

© Computational Classnotes · CC BY-NC-SA 4.0
