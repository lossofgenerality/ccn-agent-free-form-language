<!-- © Computational Classnotes · CC BY-NC-SA 4.0 -->
# Motion phrases: a brief report on output and performance

*24 November 2026. Measured on Wolfram 15.0.1 (Linux, a cloud evaluation kernel), not on your Mac, so the times are a guide only.*

## Summary

- All **16 tests pass** (`tests/MotionPhrasesTest.nb`).
- Reading a phrase takes **about 2 to 3 ms**. A transform at one moment takes about **1 ms** once the phrase has been read.
- The outputs are exact (π, √2 and so on) wherever the phrase gives exact amounts. The default path and the moves give exact formulas in t.
- Three kinds of phrase are read too literally (see "Where it falls short"). Each one is easy to fix.

## Output: ten phrases

| Phrase | Read as | Ends at | Facing |
|---|---|---|---|
| move along the path while spinning counterclockwise and move upwards | path + spin + move, together | {3, 0, 1} | as it started (one full turn) |
| spin clockwise 90 degrees | spin | {0, 0, 0} | turned −90° about z |
| move up 2 units then turn left then move forward | move; spin; move | {0, 1, 2} | turned +90° about z |
| move right 2 then orbit counterclockwise around the origin a half turn | move; orbit | {−2, 0, 0} | turned 180° about z |
| spin two and a half turns about the x axis while rising 3 | spin + move | {0, 0, 3} | turned 180° about x |
| move forward 2 metres, spin twice | move + spin | {0, 2, 0} | as it started |
| slide left slowly | move | {−1, 0, 0} | as it started; "slowly" reported as not understood |
| dance wildly | nothing understood | {0, 0, 0} | as it started; both words reported |
| turn around | spin | {0, 0, 0} | as it started (a full turn: see below) |
| go up and down | two moves, together | {0, 0, 0} | as it started (they cancel: see below) |

The example phrase gives one formula in t:

```
TranslationTransform[{3 t, Sin[2 π t], t}] . RotationTransform[2 π t, {0, 0, 1}]
```

which evaluates to the TransformationFunction with matrix rows `{Cos[2πt], −Sin[2πt], 0, 3t}`, `{Sin[2πt], Cos[2πt], 0, Sin[2πt]}` and `{0, 0, 1, t}`.

Every assumption is listed in the report. The example has four: the default path, the z axis, one full turn, and one unit up.

## Performance

| Operation | Time |
|---|---|
| Read the example phrase (`MotionParse`) | 2.8 ms |
| Read a one-part phrase | 1.9 ms |
| Read a 20-stage phrase | 29 ms (grows in step with the number of stages) |
| `MotionTransform[phrase, 0.37]`: reads the phrase again on every call | 4.0 ms |
| One transform from formulas already read | 1.1 ms |
| 200 transforms from formulas already read (the path `MotionPlot` draws) | 0.22 s |
| `MotionTransform[phrase, t]`, symbolic | 5.1 ms |
| `MotionPlot[phrase]`, graphics built (rendering not included) | 0.23 s |

What this means:

- **Animation is smooth enough:** about 1 ms a frame, well under the time of a frame at 30 frames a second.
- **For many time points, read the phrase once.** `MotionTransform[phrase, t]` reads the phrase each time it is called. In a loop, get `MotionFormula[phrase]` once and evaluate that, as `MotionPlot` and `MotionAnimate` do.
- **Where the time goes:** in each transform, most of it is spent activating and composing the `RotationTransform` and `TranslationTransform` pieces anew. If it is ever needed, each stage can be compiled once into a plain function of t that gives the matrix. That should make each transform many times faster.

## Where it falls short

1. **"turn around" gives a full turn.** In English it means a half turn. Fix: read *turn around* (with no centre and no amount) as 180°.
2. **"go up and down" cancels out.** Parts joined by *and* happen at the same time, so up and down add to nothing. People usually mean one after the other. Fix: read *and* between two opposite directions as *then*, or ask for *then* and flag the case in the report (it is already flagged as "the directions cancel").
3. **Speed words are ignored.** *Slowly*, *quickly* and *for 3 seconds* are reported as not understood. Each stage takes an equal share of time. Fix, if wanted: let speed words change how long a stage takes.

Also by design, not faults:
- *forward*, *left* and so on are fixed directions in space unless `"Frame" -> "Object"` is set;
- a path given as points is walked at an even pace per segment, not by length.

## Before you run it

Open `motion/MotionPhrases.nb` and evaluate it, then open `tests/MotionPhrasesTest.nb` and evaluate it. Its last cell should show 16 passed, 0 failed. The notebooks were checked cell by cell against the tested code, but they haven't yet been opened in Mathematica itself.

---

© Computational Classnotes · CC BY-NC-SA 4.0
