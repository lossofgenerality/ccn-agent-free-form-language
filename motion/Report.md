<!-- © Computational Classnotes · CC BY-NC-SA 4.0 -->
# Motion phrases: a report on output and performance

*24 November 2026, second issue. Measured on Wolfram 15.0.1 (Linux, a cloud evaluation kernel), not on your Mac, so the times are a guide only.*

## Summary

- The code now reads **paragraph-sized text**, not just phrases. It finds the motion parts and sets the rest aside: ordinary sentences, figures of speech ("turn on the lights", "sales rose by 12 percent"), questions and negations. It also copes with common dictation and grammar slips.
- Tested on **557 phrase variants** and **12 paragraphs** (28 to 70 words each), old version against new:

| | Old version | New version |
|---|---|---|
| Phrases in other word orders, read right | 49 of 62 | **62 of 62** |
| All 557 phrase variants (orders × slips), read right | 340 (61%) | **547 (98%)** |
| Paragraphs ending in the right place and facing the right way | 2 of 12 | **12 of 12** |
| Paragraphs also right step by step (same steps, same timing) | 0 of 12 | **9 of 12** |
| Tests in `tests/MotionPhrasesTest.nb` | 16 of 16 | **23 of 23** (7 new) |

- Reading a phrase takes **about 7 ms** (the old version took about 3 ms). A paragraph takes **about 20 to 30 ms**.
- The three paragraphs not right step by step each pick up one harmless extra step: a full turn or a pause that a person wouldn't count as a motion (see "Where it still falls short").
- **Update, same day:** a small neural net now catches those three. It comes in two versions, one written entirely in our own code and one using Wolfram's neural-net functions, both switched on with `"SubjectCheck"`. With either one, all 12 paragraphs are right step by step. See `nets/SubjectNetReport.md`.

## How it was built

**Still no neural nets, and no conversational-construct while it runs.** Every step is rule-based, deterministic and listed in the report it gives, so the same text always gives the same motion, and every reading can be traced.

The test texts were the exception: Claude, a conversational-construct, wrote all twelve paragraphs and every phrase variant for this test. None were borrowed from other sources.

| Technique | Used for |
|---|---|
| Regular expressions (`StringReplace`, `StringSplit`, `StringPosition`, `StringCases`) | splitting text into sentences, steps and parts; tidying spellings; removing filler words and stutters; finding figures of speech |
| Word lists (`$MotionVocabulary`, an Association) | the meaning of each word, now with past-tense forms (moved, spun, rose, fell…), more verbs (raise, pivot, swivel, step, come…) and a list of figures of speech to set aside |
| Dictation fixes | words split apart ("counter clock wise", "up wards"), and homophones where the meaning is clear from the words around them ("write" for right, "too steps", "for units", "won more", "than spin") |
| Number words to digits | "ninety", "one hundred and eighty", "two and a half", "a hundred" |
| Spelling correction (`DamerauLevenshteinDistance`, `DictionaryWordQ`) | an unknown word of 5 or more letters, not in the dictionary, is matched to the nearest motion word with the same first letter, within 1 edit (2 for long words): "spining" → spinning, "counterclokwise" → counterclockwise, "orgin" → origin |
| Rules of English order | *then*, *next*, *finally*, *after that* make a new step; "Y **after** X" and "**before** X, Y" are put in time order; a comma list of actions ("moved forward, turned left, and moved on") is one after another; *while*, *as* and a leading "-ing" part ("spinning, move up") are at the same time |
| Keyword rules, in a fixed order (`Which`) | the kind of each part: pause, path, orbit, spin, move |
| Filters | a question, a negation ("don't move left"), a direction with no motion verb, or a lone verb with no direction or distance ("thank you for coming") is set aside, with the reason |
| Exact arithmetic and Wolfram's own geometry | `RotationTransform`, `TranslationTransform` and `AffineTransform`, composed with `Dot`, held as readable formulas with `Inactive` until evaluated; `Simplify` for where each step ends |
| `VerificationTest`, `TestReport` | 23 tests, and the 557-phrase and 12-paragraph scoring |

The word lists are the obvious place for one of the agent's own small nets (draft 8) to help. A net could learn which sentences carry motion and which words mean what, from the parts set aside and accepted in reports, and the rules would stay as its check.

## The algorithm, in pseudocode

```
READ-TEXT(text, options):
    for each sentence of text:                         -- split at . ! ? ; or a new line
        if it ends with "?": set it aside (a question); next sentence
        s ← TIDY(sentence)
        for each step of s, split at  then | next | finally | after that | . | ;
            for each piece of ORDER-IN-TIME(step):     -- "after" and "before"
                for each group of GROUP-PARTS(piece):
                    keep, aside ← SETTLE(group)
                    if keep has a motion: add keep as a new step
    position ← (0,0,0); orientation ← identity
    for each step: formula, position, orientation ← STEP-TRANSFORM(step, position, orientation)
    return the steps, their formulas, where it ends, what was set aside, and the report

TIDY(sentence):
    lower case; curly quotes to straight ones
    remove fillers (um, uh, er, hmm) and stutters ("spin spin" → spin)
    dictation fixes: "counter clock wise" → counterclockwise, "write" → right,
        "too"/"for" before a unit → two/four, "won" → one, "than" before a verb → then
    number words → digits: "one hundred and eighty" → 180
    set aside figures of speech: turn on/off, move on to, look up, rose by N percent…
    usual tidying: degrees, "x-axis", "and a half"

ORDER-IN-TIME(step):
    "after X, Y" or "after X Y"  → X, then Y      (Y starts at the next plain motion verb)
    "Y after X"                  → X, then Y
    "before X, Y"                → Y, then X
    "Y before X"                 → Y, then X

GROUP-PARTS(piece):
    split at  "," | ", and" | and | while | as | meanwhile, noting which one came before each part
    in run-on speech, split again before each motion verb after the first
        (not a unit like "a quarter turn", not a noun after "the", "a", "your"…)
    read each part (READ-PART)
    a part after a comma starts a new group (one after another) when both it and the part
        before have their own motion verb, neither begins with an "-ing" verb, and the part
        before wasn't introduced by "while"/"as"; otherwise it joins the same group (together)

SETTLE(group):
    set aside: negated parts; parts with no motion words; a direction with no motion verb
        in the whole group; a lone verb with no direction, distance or number
    join stray words to the spin they describe: "clockwise, spin 90 degrees",
        "about the x axis, spin 270 degrees"

READ-PART(part):
    words ← the words and numbers; correct misspellings (see the table above)
    kind ← pause | path | orbit | spin | move, the first that matches (as before)
    spin/orbit: axis (else z), sense (else counterclockwise; for turn left/right ±),
        angle = amount × unit (degrees, radians, turns); with no amount: a quarter turn for
        "turn left/right", a half turn for "turn around", else a full turn
    move: the sum of the directions named ("back" is dropped beside up/down: "raise it back up"),
        else up for rise words, down for sink words, the axis named, else forward;
        distance = amount, else 1
    path: also carries any direction named ("move upwards along the path")
    list assumptions, corrections and words not understood

STEP-TRANSFORM(parts, P, M):                       -- t from 0 to 1 within the step
    offset(t) ← Σ moves d·F(v)·t + Σ paths (F(path(t) − path(0)) + d·F(v)·t)
        where F(x) = M·x in the object's own frame, else x
    T(t) ← orbits(t) · TranslationTransform(P + offset(t)) · spins(t) · AffineTransform(M)
    P, M ← where T(1) puts and turns the object
```

## Output: twelve paragraphs

Each paragraph was scored against a short phrase holding the same motions in order. "Ends right" means the same final position and orientation. "Steps right" means the same steps, at the same times, checked at t = 0.37.

| Paragraph | Words | Steps found / expected | Ends right | Steps right | Set aside |
|---|---|---|---|---|---|
| Drone light-show script | 70 | 3 / 3 | yes | yes | 7 sentences or parts, incl. "thank you for coming" |
| Dance class, dictated (no capitals, "write", "too", "clock wise") | 51 | 3 / 3 | yes | yes | 4 parts and "pick this up" |
| Animation storyboard | 56 | 4 / 3 | yes | no: "the camera holds on the kettle" read as a pause | 4 parts, incl. "the cat does not move" |
| Robot vacuum log (past tense; the robot's own frame) | 51 | 5 / 5 | yes | yes | 5 parts and "fell to 40 percent" |
| Children's game | 38 | 4 / 4 | yes | yes | "can you jump?", "don't move left!" and "turn on" |
| VR tutorial (numbers in words) | 59 | 3 / 3 | yes | yes | 5 parts and "turn off" |
| Gallery installation | 52 | 3 / 2 | yes | no: "the experience turns their sense of scale" read as a full turn | 2 parts and "upside down" |
| Email with instructions | 64 | 3 / 3 | yes | yes | 9 parts and "going forward", "rose by 12 percent", "falls behind" |
| Short story | 46 | 4 / 3 | yes | no: "Mia… turned to her brother" read as a full turn | 5 parts and "look up", "looking up" |
| Meeting minutes (no motions at all) | 54 | 0 / 0 | yes | yes | 10 parts and 6 figures of speech: "move on to", "rose to 80 percent", "circle back", "turn in", "drop the ball", "looking up" |
| Voice memo, run-on dictation ("than", "counterclokwise", "for units", "won") | 35 | 3 / 3 | yes | yes | — |
| Studio instructions ("after" and "before") | 28 | 4 / 4 | yes | yes | 3 parts |

What was found in two of them, as an example:

- **Drone script:** "the drone should rise 4 metres" + "spinning counterclockwise" (together), then "it will move right 3 units", then "orbit counterclockwise around the origin a half turn". It ends at {−3, 0, 4}, turned 180°.
- **Studio instructions:** "raising it 1 unit", then "spin the model 360 degrees clockwise", then "slide it right 2 units", then "wait". The *after* and *before* sentences came out in time order.

## Output: 557 phrase variants

There are 12 base phrases, and each is written in 3 to 6 other orders that mean the same in English (62 wordings in all). Each wording was then given 12 kinds of slip wherever the slip applies. A variant counts as read right when it matches its base phrase at t = 0.37 and at the end.

| Kind of slip | Variants | Old version | New version |
|---|---|---|---|
| None (just a different word order) | 62 | 49 | **62** |
| Capitals and a full stop | 62 | 49 | **62** |
| Filler words (um, uh, like) | 62 | 49 | **62** |
| Words split by dictation ("counter clock wise", "up wards", "for ward") | 36 | 20 | **36** |
| Homophones ("write", "too", "than", "for", "won") | 27 | 1 | **27** |
| Misspellings ("spining", "counterclokwise", "degres", "orgin") | 38 | 9 | **38** |
| Past tense ("spun", "moved", "rose", "orbited") | 59 | 28 | **58** |
| Wrong verb forms ("while turn", "while spin") | 20 | 16 | **19** |
| Repeated words ("spin spin", "the the") | 62 | 49 | **62** |
| Run-on, no joining words or commas | 37 | 8 | **29** |
| Numbers spelled out ("ninety", "a hundred and eighty") | 51 | 31 | **51** |
| Numbers as digits ("2.5") | 7 | 6 | **7** |
| Degree sign and hyphens ("90°", "x-axis", "counter-clockwise") | 34 | 25 | **34** |
| **All** | **557** | **340 (61%)** | **547 (98%)** |

The orders tested include "while spinning counterclockwise, move along the path and move upwards", "spinning counterclockwise, move upwards along the path", "clockwise, spin 90 degrees", "go up 2, spin twice, then come down 2", "first rise 2, next spin twice, finally sink 2", "move down one unit after a pause" and "spin 180 degrees after following the path".

Of the 10 variants still misread:

- **Two are fair readings, not errors.** "Spun counterclockwise, moved upwards along the path" and "spin counterclockwise, move upwards along the path" are comma lists of actions, which the code reads as one after another. The base phrase meant them at the same time, but English allows either.
- **Eight are run-on dictation with no joining words at all.** An example is "slide left 3 units turn a quarter turn clockwise". The cut at the second verb fails there because "turn" is also a unit word ("a quarter turn").

## Performance

| Operation | Time |
|---|---|
| Read one phrase (new version) | about 7 ms (old version: about 3 ms) |
| Read one paragraph of 30 to 70 words | about 20 to 30 ms |
| Score all 557 variants (each read twice, plus the bases) | 8.2 s |
| Score all 12 paragraphs (each read several times) | 1.1 s |
| One transform from formulas already read | about 1 ms, as before |

These are averages taken from the batch runs, not separate timings. The extra time per phrase goes mostly into spelling correction, which checks the dictionary and the word lists for each unknown word. Animation is as fast as before, because it works from formulas already read.

## Where it still falls short

1. **A motion verb about something else is read as a motion.** In the tests, "the camera holds on the kettle" became a pause, "the experience turns their sense of scale" a full turn, and "Mia turned to her brother" a full turn. They don't move the object, but each adds a step. **Now handled by the subject check** (`nets/SubjectNet.nb`): with it on, all three are set aside and all 12 paragraphs are right step by step. It still misses some new shapes, for example "the cameraman slowly moves left" and "my heart sank".
2. **Run-on dictation where "turn" is both verb and unit.** See above: 29 of 37 are read right.
3. **A comma list can mean "one after another" or "together".** The code reads a list of actions as one after another, which suits narrative and lists of instructions. "Move up, spinning slowly" (with "-ing") stays together.
4. **"Go up and down" still cancels out.** Parts joined by *and* are together, and the report says the directions cancel.
5. **A negation sets aside the whole part,** so "don't forget to spin twice" would be lost.
6. **Speed and units are not used.** *Slowly* and *quickly* are reported as not understood. *Centimetres* and *metres* count the same as *units*.
7. **Spelling correction needs the dictionary data.** `DictionaryWordQ` keeps real words (for example "spine") from being "corrected" into motion words. Without the data, more words would be corrected. Real-word slips the correction can't see ("ride" for "right") are only caught where a dictation fix lists them.

Also by design: *forward*, *left* and so on are fixed directions in space unless `"Frame" -> "Object"` is set (the robot log uses it). A path given as points is walked at an even pace per segment.

## Files

- `motion/MotionPhrases.nb`: the package. It is new in this issue: it reads paragraphs, and `MotionFind[text]` shows the motion parts found and what was set aside.
- `tests/MotionPhrasesTest.nb`: 23 tests.
- `tests/MotionPhrasesCorpus.nb`: the 557-variant corpus and the 12 paragraphs, with the scoring. Open it and evaluate it to reproduce the tables above.

Before you run them: open `motion/MotionPhrases.nb` and evaluate it, then evaluate the test notebook. Its last cell should show 23 passed, 0 failed. The notebooks were checked cell by cell against the code that was run, but they haven't yet been opened in Mathematica itself.

---

© Computational Classnotes · CC BY-NC-SA 4.0
