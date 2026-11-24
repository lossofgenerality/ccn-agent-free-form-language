<!-- © Computational Classnotes · CC BY-NC-SA 4.0 -->
# Motion phrases

The first simple operation of the agent free-form language. It reads spoken motion phrases such as

> move along the path while spinning counterclockwise and move upwards

and turns each part into a Wolfram Language `RotationTransform` or `TranslationTransform`.

**Authors:** Dara O Shayda and Hikari Noor Hoshino (星野ヌール), AI System Programmer

## Use

```wolfram
NotebookEvaluate["<folder>/MotionPhrases.nb"]   (* or open MotionPhrases.nb and evaluate it *)

phrase = "move along the path while spinning counterclockwise and move upwards";
MotionReport[phrase]             (* how each part was read, what was assumed, what wasn't understood *)
MotionFormula[phrase]            (* each stage as RotationTransform . TranslationTransform, inactive *)
MotionTransform[phrase, 1/4]     (* the TransformationFunction a quarter of the way through *)
MotionTransform[phrase, t]       (* symbolic in t *)
MotionPlot[phrase]               (* snapshots along the motion *)
MotionAnimate[phrase]
```

The report for the example:

```
Stage 1 of 1, all at the same time:
  ✓ "move along the path" → follow the path: TranslationTransform[{3*t, Sin[2*t*Pi], 0}]
      ⚠ no path given: the default curve {3 t, Sin[2 Pi t], 0} is used
  ✓ "spinning counterclockwise" → spin about its own centre, axis {0, 0, 1}, by 2*Pi: RotationTransform[2*t*Pi, {0, 0, 1}]
      ⚠ no axis: z (vertical) assumed
      ⚠ no amount: one full turn assumed
  ✓ "move upwards" → move 1 along {0, 0, 1}: TranslationTransform[{0, 0, t}]
      ⚠ no distance: 1 unit assumed
  Stage transform (t from 0 to 1): TranslationTransform[{3*t, Sin[2*t*Pi], t}] . RotationTransform[2*t*Pi, {0, 0, 1}]
Ends at {3, 0, 1}, facing as it started.
```

## How a phrase is read

- **Stages, one after another:** split at *then*, *and then*, *after that*, *followed by*, a full stop or a semicolon. Each stage takes an equal share of the time from 0 to 1.
- **Parts of a stage, all at the same time:** split at *while*, *and*, *as*, *meanwhile* or a comma.
- **Each part is one of:**

| Kind | Words | Transform |
|---|---|---|
| move | move, go, slide, glide, drift, travel…; rise, climb (up); sink, fall, drop (down); or just a direction | `TranslationTransform[d v t]` |
| follow the path | path, follow | `TranslationTransform[path[t] - path[0]]` |
| spin, about its own centre | spin, rotate, turn, twist, twirl, roll | `RotationTransform[θ t, axis]` |
| orbit, about a point | orbit, revolve, circle; or *around the origin / centre* | `RotationTransform[θ t, axis, centre]` |
| stay still | pause, wait, hold, stay, stop | none |

- **Directions:** up, down, left, right, forward, back (+z, −z, −x, +x, +y, −y), or *along the x / y / z axis*.
- **Amounts:** numbers in digits or words, *a quarter*, *half*, *two and a half*, *twice*; degrees, radians, turns, revolutions or *times*. With no amount: a move is 1 unit, a spin or orbit is one full turn, and *turn left / right* is a quarter turn.
- **Turning:** counterclockwise (also anticlockwise) is positive about the axis, by the right-hand rule. With none given, it is counterclockwise.
- **Within a stage:** the spins turn the object about its own centre first, then it is moved to its place, then any orbit carries it round its centre. The next stage starts where and as this one ended.

Words that aren't understood are listed in the report and ignored, as with free lines in agent scripts.

## Options

| Option | Default | Meaning |
|---|---|---|
| `"Path"` | `Automatic` (the curve `{3 t, Sin[2 Pi t], 0}`) | a function of t from 0 to 1, or a list of points (2D or 3D), walked at an even pace per segment |
| `"Centre"` | `{0, 0, 0}` | the centre for *orbit around the centre* |
| `"Step"` | `1` | the distance of a move with no amount |
| `"Frame"` | `"World"` | `"Object"` makes moves follow the object's own heading, so *turn left then move forward* goes the new way |
| `"Object"`, `"Snapshots"` | a small box with an arrow, 6 | for `MotionPlot` and `MotionAnimate` |

`$MotionVocabulary` holds all the words. Add to its lists to extend the language.

## Tests

`tests/MotionPhrasesTest.nb`: 16 tests (all passing in Wolfram 15). Open it and evaluate it: its first cell loads `MotionPhrases.nb` from the `motion` folder, and its last cell shows the results.

The package is a notebook, `MotionPhrases.nb`: its cells are initialisation (Code) cells, so evaluating the notebook loads the package. To use it in the cloud, put the notebook in your cloud and `NotebookEvaluate` it there.

---

© Computational Classnotes · CC BY-NC-SA 4.0
