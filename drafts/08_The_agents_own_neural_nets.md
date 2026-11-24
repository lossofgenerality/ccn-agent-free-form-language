# Agent script — 8. The agent's own neural nets

*Interim draft for comment, 21 November 2026.*

## What they are, and what they aren't

An **own net** is a small neural net that belongs to one agent and does one specific job. It is trained outside Claude (exogenous to it), on our own data, and can be trained and retrained in **Wolfram and in Python** from the same description.

Own nets don't replace the conversational-construct. Open answers in the agent's voice still come from Claude. What an own net offers, for the narrow jobs it suits:

- **speed and cost:** many questions are settled without a Claude call;
- **privacy:** the question doesn't leave the kernel or host;
- **exactness:** it gives the same answer every time, and it can be tested and scored;
- **it is ours:** it is trained on CCN's data, kept in our cloud, and has its history in our records.

## The first one, built (24 November 2026)

`nets/SubjectNet.nb` is the first own net. It decides whether a motion part is about the object or about something else ("Mia turned to her brother"). It was built twice, on the same data and design: once entirely in our own code (forward pass, backpropagation and Adam written out, with no Wolfram neural-net functions) and once with `NetChain` and `NetTrain`. The two agreed on every decision. See `nets/SubjectNetReport.md`.

## Jobs worth a net

| Net | Agent | Job | What it does with the answer |
|---|---|---|---|
| topic gate | eye-witness, Tutu Cat | is the question on the script's topics? | off topic and sure: give the `offTopicReply`, with no Claude call |
| language | all | which language is the question in? | checks `speaks:`, and chooses the reply language |
| line reader | the compiler | which key word does a free line belong to, or is it guidance? | suggests a reading in the compile report (file 7); the author accepts it |
| never check | Tutu Cat | does a question or reply touch a `never:` subject? | adds a check; never takes one away |
| route | MAXIT, Laplacian Lab | which code step or derivation fits this question? | chooses the step; Claude still phrases the answer |

The **line reader** is the language's own net: it learns how CCN's authors write scripts, from the lines they have accepted in compile reports.

## In a script

```
own net: topic gate
  job: is the question about the topics?
  input: the question
  answers: on topic, off topic
  shape: bytes 256, embedding 32, mean, 64, relu, 2
  learns from: file "topic-gate-examples.jsonl", labelled questions from the ledger
  must score: 0.97 on the held-out examples
  used when: sure above 0.9; otherwise ask Claude
  trains in: Wolfram, Python
```

- `shape:` uses the shared layer list below, so both trainers build the same net.
- `must score:` comes with a held-out set. A net that scores lower doesn't compile, and the agent goes on working without it (Claude decides, as today).
- `used when:` sets the line between the net deciding and Claude deciding. Each time it is crossed, the ledger records it (file 6, section 5).

## One description, two trainers

| In `shape:` | Wolfram | Python (PyTorch) |
|---|---|---|
| `bytes N` | input: N byte codes, padded | the same, as a tensor |
| `embedding D` | `EmbeddingLayer[D, 257]` | `nn.Embedding(258, D)` (row 0 unused) |
| `mean` | `AggregationLayer[Mean, 1]` | `.mean(dim=1)` |
| `N` (a number) | `LinearLayer[N]` | `nn.Linear(…, N)` |
| `relu`, `tanh` | `Ramp`, `Tanh` | `nn.ReLU()`, `nn.Tanh()` |
| `dropout p` | `DropoutLayer[p]` | `nn.Dropout(p)` |
| `norm` | `NormalizationLayer[]` | `nn.LayerNorm(…)` |
| the last number | followed by `SoftmaxLayer[]` | followed by `softmax` |

We start with this short list and add layers (for example a small attention block) only when a job needs them and both sides support them. Wolfram nets such as DistributeNet's transformer show where that could go.

### Inputs are bytes

The text goes in as **UTF-8 bytes**, padded or cut to a fixed length. Each byte is given the code *byte + 1* (1 to 256), and padding is 257. The codes start at 1 because Wolfram's `EmbeddingLayer` counts from 1. In PyTorch the same codes are used as they are, with an embedding of 258 rows and row 0 never used. The `mean` step averages over the padding too, on both sides alike. This choice:

- works the same for English, Arabic and Japanese, with no word list to keep in step;
- does the encoding outside the net, so both sides give the net exactly the same numbers;
- gives a fixed-length input, which is what ONNX exchange needs (below).

### Moving nets between Wolfram and Python: ONNX

A trained net is saved as **ONNX**, which both sides read and write: `Export[…, net, "ONNX"]` and `Import[…]` in Wolfram, and `torch.onnx.export` and `onnxruntime` in Python. A test run today in Wolfram 15:

- a fixed-length `NetChain` (linear, ramp, linear, softmax) exported to ONNX and imported back gave **exactly** the same outputs;
- an embedding, mean and linear net, with a fixed-length input, was exported from Wolfram and run in Python with `onnxruntime`. It gave the same outputs to 7 decimal places. The exported file takes the **same 1-based codes** as the Wolfram net (Wolfram adds the index conversion inside the file), as whole numbers (`int64`), one question at a time;
- a net with a **variable-length** input and a `NetEncoder` did **not** export.

So nets keep their encoding outside the net and use a fixed input length. That is the design above.

Still to test: the other direction, a net trained in PyTorch, exported to ONNX, and then imported and run in Wolfram. This is the first task of the net work (file 4, step 9).

### What "trains in both" promises

Training uses random starting weights, so a net trained in Wolfram and one trained in Python won't have identical weights. The promises are:

1. **The same net.** One `shape:` builds the same layers, with the same sizes, on both sides.
2. **The same data.** One examples file (JSON lines), one fixed split into training and held-out examples.
3. **Scores that agree.** Both trainers meet `must score:`, and are within 0.02 of each other.
4. **One net that runs anywhere.** Whichever trainer made it, the ONNX file gives the same outputs in Wolfram and in Python, to 5 decimal places, on the held-out set. This is checked every time a net is saved.

## Where the examples come from

1. **Examples we write**, in a file next to the script.
2. **Lines the author has accepted** in compile reports (for the line reader).
3. **Decisions Claude has already made**, taken from the ledger: for example, Claude answered a question as on topic and the visitor went on. This is allowed only where:
   - the question text was kept under the script's `keep questions:` rule, and the CCN base allows it;
   - **the agent isn't for children**: Tutu Cat never learns from its chats;
   - the use is in line with Anthropic's terms on using Claude's outputs to train models. Small task nets like these look to be fine, but we should check the current terms before step 9 of the plan (question 9 in file 5);
   - labelling by Claude, when we ask for it, is a listed purpose (`label`) and goes in the ledger like any other call.

## Release and records

- A net is used by an agent only after its scores are in a compile report and you have approved it. Retraining replaces the net in place.
- Nets live privately in the cloud next to the scripts, as `.wlnet` and `.onnx`. The repo keeps a **training record** for each net: its description, a fingerprint of its data, the trainer (Wolfram or Python), its scores and the date. Git keeps the history; file names carry no version numbers.
- Training runs only in the `train` mode or from a notebook, and only for the owner. Visitors can never cause training.

© Computational Classnotes · CC BY-NC-SA 4.0
