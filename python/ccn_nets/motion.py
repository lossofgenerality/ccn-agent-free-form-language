"""Motion phrases, in Python: a port of motion/MotionPhrases.nb.

Reads spoken motion phrases ("move along the path while spinning counterclockwise and move upwards"),
or paragraphs with motion phrases inside them, into steps of motion parts, and gives the pose (a 4 x 4
matrix) at any time. Every function follows the Wolfram one of the same name: normalise, sentences,
stagesOf, clausesOf, groupsOf, sentenceGroups, settleGroup, readClause, readWords, MotionSubject,
readText, MotionFind, MotionParse and MotionTransform.

Two Wolfram functions have no Python equivalent and are written here:
  - StringReplace with a list of rules, which replaces in one pass (multi_replace);
  - DictionaryWordQ, used to leave real words uncorrected. Only the real words that lie near a motion
    word matter, and Wolfram's dictionary gave exactly those (data/near_words.txt).

By Dara O Shayda and Hikari Noor Hoshino (星野ヌール)
AI System Programming Group

© Computational Classnotes · CC BY-NC-SA 4.0
"""

from __future__ import annotations

import math
import os
import re
from fractions import Fraction

import numpy as np

# ---------- The words ----------

VOCABULARY = {
    "translate": ["move", "moves", "moving", "moved", "go", "goes", "going", "went", "gone", "travel", "travels",
                  "travelling", "traveling", "travelled", "traveled", "slide", "slides", "sliding", "slid", "glide", "glides",
                  "gliding", "glided", "drift", "drifts", "drifting", "drifted", "shift", "shifts", "shifting", "shifted",
                  "head", "heads", "heading", "headed", "walk", "walks", "walking", "walked", "fly", "flies", "flying", "flew",
                  "flown", "translate", "translates", "translating", "translated", "step", "stepping", "stepped",
                  "come", "comes", "coming", "came"],
    "rise": ["rise", "rises", "rising", "rose", "risen", "climb", "climbs", "climbing", "climbed", "ascend",
             "ascends", "ascending", "ascended", "lift", "lifts", "lifting", "lifted", "raise", "raises", "raising", "raised"],
    "sink": ["sink", "sinks", "sinking", "sank", "sunk", "fall", "falls", "falling", "fell", "fallen", "drop",
             "drops", "dropping", "dropped", "descend", "descends", "descending", "descended", "lower", "lowers",
             "lowering", "lowered"],
    "spin": ["spin", "spins", "spinning", "spun", "rotate", "rotates", "rotating", "rotated", "turn", "turns",
             "turning", "turned", "twist", "twists", "twisting", "twisted", "twirl", "twirls", "twirling", "twirled",
             "roll", "rolls", "rolling", "rolled", "pivot", "pivots", "pivoting", "pivoted", "swivel", "swivels",
             "swivelling", "swiveling", "swivelled", "swiveled", "whirl", "whirls", "whirling", "whirled"],
    "orbit": ["orbit", "orbits", "orbiting", "orbited", "revolve", "revolves", "revolving", "revolved", "circle",
              "circles", "circling", "circled"],
    "follow": ["follow", "follows", "following", "followed", "trace", "traces", "tracing", "traced"],
    "pause": ["pause", "pauses", "pausing", "paused", "wait", "waits", "waiting", "waited", "hold", "holds",
              "holding", "held", "stay", "stays", "staying", "stayed", "stop", "stops", "stopping", "stopped", "halt",
              "halts", "halted"],
    "directions": {
        "up": (0, 0, 1), "upward": (0, 0, 1), "upwards": (0, 0, 1),
        "down": (0, 0, -1), "downward": (0, 0, -1), "downwards": (0, 0, -1),
        "left": (-1, 0, 0), "leftward": (-1, 0, 0), "leftwards": (-1, 0, 0),
        "right": (1, 0, 0), "rightward": (1, 0, 0), "rightwards": (1, 0, 0),
        "forward": (0, 1, 0), "forwards": (0, 1, 0), "ahead": (0, 1, 0),
        "back": (0, -1, 0), "backward": (0, -1, 0), "backwards": (0, -1, 0)},
    "axes": {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1), "vertical": (0, 0, 1)},
    "senses": {"counterclockwise": 1, "clockwise": -1},
    "numbers": {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "half": Fraction(1, 2), "quarter": Fraction(1, 4),
                "once": 1, "twice": 2, "thrice": 3, "full": 1, "whole": 1, "andahalf": Fraction(1, 2), "andaquarter": Fraction(1, 4)},
    "angleUnits": ["degree", "degrees", "radian", "radians", "turn", "turns", "revolution", "revolutions",
                   "rotation", "rotations", "time", "times"],
    "distanceUnits": ["unit", "units", "metre", "metres", "meter", "meters", "step", "steps", "centimetre",
                      "centimetres", "centimeter", "centimeters"],
    "places": ["path", "origin", "center", "point"],
    "other": ["the", "its", "it", "itself", "own", "s", "to", "of", "by", "with", "in", "on", "at",
              "around", "about", "along", "axis", "direction", "way", "from", "into", "onto", "toward", "towards",
              "object", "body", "keep", "keeps", "keeping", "also", "too", "same", "is", "be", "all", "each", "then",
              "will", "should", "must", "can", "now", "just", "please", "so", "you", "we", "i", "let", "lets", "us"],
    # Figures of speech that use motion words without meaning a motion; set aside before reading
    "idioms": [
        r"\bturn(?:s|ed|ing)? (?:on|off|out|into|in)\b", r"\bturn(?:s|ed|ing)? (?:the|a) page\b",
        r"\bturn of (?:events|phrase)\b", r"\bupside down\b",
        r"\bmov(?:e|es|ed|ing) on(?: to)?\b", r"\bmov(?:e|es|ed|ing) (?:in|out|house)\b",
        r"\b(?:go|goes|went|going) (?:on|out|ahead and|over)\b", r"^going forward\b",
        r"\b(?:look|looks|looked|looking) up\b", r"\bpick(?:s|ed|ing)? (?:\w+ )?up\b",
        r"\bup to (?:you|date|now|speed|something|no good)\b", r"\bright (?:now|away|here|there)\b",
        r"\ball right\b", r"\bback then\b",
        r"\b(?:rise|rises|rose|risen|rising|fall|falls|fell|fallen|falling|drop|drops|dropped|dropping|climb|climbs|climbed|climbing|sink|sinks|sank|sinking|go|goes|went|gone|going) (?:up |down )?(?:to|by) [0-9.]+ ?(?:percent|per cent|%)",
        r"\bpath to (?:success|victory|recovery|peace|freedom|glory|happiness)\b",
        r"\b(?:get|got|getting) the ball rolling\b", r"\bdrop(?:s|ped|ping)? the ball\b",
        r"\bcircle(?:s|d)? back\b", r"\bfall(?:s|ing)? behind\b", r"\bfell behind\b",
        r"\bstep(?:s|ped|ping)? (?:up|down) as\b", r"\bspin doctor\b", r"\brolling hills\b"],
}

MOTION_KINDS = ["translate", "rise", "sink", "spin", "orbit", "follow", "pause"]


def verb_forms(v=VOCABULARY) -> list:
    return sorted({w for k in MOTION_KINDS for w in v[k]})


def known_words(v=VOCABULARY) -> list:
    lists = MOTION_KINDS + ["angleUnits", "distanceUnits", "places", "other"]
    return sorted({w for k in lists for w in v[k]} | {w for k in ("directions", "axes", "senses", "numbers") for w in v[k]})


VF = verb_forms()
VF_SET = set(VF)
KNOWN = known_words()
KNOWN_SET = set(KNOWN)

NUMBER_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
                "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
                "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
                "ninety": 90, "hundred": 100, "thousand": 1000}

WORD_RE = re.compile(r"[a-z]+|\d+(?:\.\d+)?")
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")

# ---------- StringReplace with a list of rules: one pass, the first rule that matches at each place ----------

class Rules:
    def __init__(self, rules):
        """rules: (regex, replacement), the replacement a string with \\1 for groups, or a function of the match."""
        self.rules = [(re.compile(p), r) for p, r in rules]
        self.any = re.compile("|".join(f"(?:{p})" for p, _ in rules))

    def replace(self, s: str) -> str:
        out, i, n = [], 0, len(s)
        while i <= n:
            m = self.any.search(s, i)
            if not m:
                out.append(s[i:])
                break
            j = m.start()
            out.append(s[i:j])
            for pat, rep in self.rules:
                r = pat.match(s, j)
                if r and r.end() > j:
                    out.append(rep(r) if callable(rep) else r.expand(rep))
                    i = r.end()
                    break
            else:
                if j < n:
                    out.append(s[j])
                i = j + 1
        return "".join(out)

    def cases(self, s: str) -> list:
        """StringCases with a list of patterns: the matches, in order, without overlaps."""
        found, i, n = [], 0, len(s)
        while i <= n:
            m = self.any.search(s, i)
            if not m:
                break
            j = m.start()
            for pat, _ in self.rules:
                r = pat.match(s, j)
                if r and r.end() > j:
                    found.append(r.group(0))
                    i = r.end()
                    break
            else:
                i = j + 1
        return found


# ---------- Tidying a sentence ----------

UNITS_AHEAD = r"(?=\s+(?:units?|steps?|turns?|times|degrees|metres?|meters?|centimetres?|centimeters?|and an? (?:half|quarter))\b)"

DICTATION = Rules([
    (r"\b(?:counter|anti)[- ]?clock[- ]?wise\b", "counterclockwise"),
    (r"\bclock[- ]wise\b", "clockwise"),
    (r"\bup wards\b", "upwards"), (r"\bdown wards\b", "downwards"),
    (r"\bback wards\b", "backwards"), (r"\bfor wards\b", "forwards"),
    (r"\bfor ward\b", "forward"),
    (r"\bex[- ]axis\b", "x axis"), (r"\bwhy[- ]axis\b", "y axis"),
    (r"\bze[de][- ]axis\b", "z axis"),
    (r"\bwrite\b", "right"),
    (r"\btoo\b" + UNITS_AHEAD, "two"),
    (r"\bfor\b" + UNITS_AHEAD, "four"),
    (r"\bwon\b(?!')", "one"),
    (r"(^|,\s*|\band\s+)than\b", lambda m: m.group(1) + "then"),
    (r"\bthan\b(?=\s+(?:" + "|".join(VF) + r")\b)", "then"),
])

_NW = "|".join(NUMBER_WORDS)
NUMBER_WORDS_RE = re.compile(r"\b(?:a\s+(?=hundred|thousand))?(?:" + _NW + r")(?:(?:(?:(?<=hundred)|(?<=thousand))\s+and\s+|[\s-]+)(?:" + _NW + r"))*\b")


def words_to_number(s: str) -> str:
    total = cur = 0
    for t in re.findall(r"[a-z]+", s):
        if t in ("a", "and"):
            continue
        elif t == "hundred":
            cur = max(cur, 1) * 100
        elif t == "thousand":
            total += max(cur, 1) * 1000
            cur = 0
        else:
            cur += NUMBER_WORDS[t]
    return str(total + cur)


IDIOMS = Rules([(p, " ") for p in VOCABULARY["idioms"]])

FINAL = Rules([
    (r"counter[- ]?clockwise|anti[- ]?clockwise", "counterclockwise"),
    ("°", " degrees "),
    (r"\b([xyz])[- ]axis\b", r"\1 axis"),
    ("centre", "center"),
    (r"\band an? half\b", " andahalf "),
    (r"\band an? quarter\b", " andaquarter "),
    (r"\b(?:and then|after that|followed by|afterwards|then|next|finally|lastly|later|subsequently)\b", " | "),
    (r"\b(?:first|firstly)\b", " "),
    (r"(?<!\d)\.|\.(?!\d)|;", " | "),
])


def normalise(s: str):
    """The tidied sentence, with " | " between steps, and the figures of speech set aside."""
    t = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"\b(?:um+|uh+|uhm|er+|erm|hmm+)\b", " ", t)        # filler words
    t = re.sub(r"\b(\w+)(?:\s+\1\b)+", r"\1", t)                    # stutters: "spin spin"
    t = DICTATION.replace(t)
    t = NUMBER_WORDS_RE.sub(lambda m: words_to_number(m.group(0)), t)
    idioms = IDIOMS.cases(t)
    t = IDIOMS.replace(t)
    t = FINAL.replace(t)
    return t, idioms


def sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?;])\s+|\n+", text) if s.strip()]


def words(s: str) -> list:
    return WORD_RE.findall(s)


# ---------- Steps in time: then, after, before ----------

def _split_drop_empty(s, pattern, maxsplit):
    """StringSplit[s, p, n]: as re.split, without empty pieces at the ends."""
    parts = re.split(pattern, s, maxsplit=maxsplit)
    while parts and parts[0] == "":
        parts.pop(0)
    while parts and parts[-1] == "":
        parts.pop()
    return parts


def split_at_word(s: str, k: int):
    p = [m.start() for m in WORD_RE.finditer(s)][k]
    return [s[:p], s[p:]]


def split_lead(rest: str, before: bool):
    """"after X, Y" or "after X Y": X happens first; "before X, Y": Y happens first."""
    if "," in rest:
        parts = _split_drop_empty(rest, ",", 1)
    else:
        w = words(rest)
        k = next((i for i in range(1, len(w)) if w[i] in VF_SET and not w[i].endswith("ing")), None)
        parts = [rest] if k is None else split_at_word(rest, k)
    return parts if len(parts) < 2 else (parts[::-1] if before else parts)


def order_stage(s: str):
    t = s.strip()
    if t.startswith("after "):
        return split_lead(t[6:], False)
    if t.startswith("before "):
        return split_lead(t[7:], True)
    if re.search(r"\bafter\b", t):
        return _split_drop_empty(t, r"\bafter\b", 1)[::-1]
    if re.search(r"\bbefore\b", t):
        return _split_drop_empty(t, r"\bbefore\b", 1)
    return [t]


def stages_of(t: str) -> list:
    return [x.strip() for part in t.split("|") for x in order_stage(part) if x.strip()]


# ---------- Parts of a step: together, or one after another ----------

SEP_RE = re.compile(r"\s*(?:,\s*(?:and\b\s*)?|\b(?:while|whilst|and|as|meanwhile|simultaneously)\b)\s*")


def conn_kind(sep: str) -> str:
    if sep.strip().startswith(","):
        return "comma"
    if re.search(r"\b(?:while|whilst|as|meanwhile|simultaneously)\b", sep):
        return "while"
    return "and"


def join_intro(old: str, k: str) -> str:
    if old == "none":
        return k
    if old == "while" or k == "while":
        return "while"
    if old == "start":
        return "start"
    if old == "and" or k == "and":
        return "and"
    return "comma"


UNIT_WORDS = set(VOCABULARY["angleUnits"]) | set(VOCABULARY["distanceUnits"])
DETERMINERS = {"to", "the", "a", "an", "your", "its", "his", "her", "their", "my", "our", "this", "that"}


def verb_split(text: str) -> list:
    """Run-on speech with no joining words: each motion verb after the first starts a new part, said at the
    same time, unless the word is a unit ("a quarter turn") or a noun after "the", "a", "your"..."""
    w = words(text)
    vs = [i for i in range(len(w)) if w[i] in VF_SET and w[i] not in UNIT_WORDS and (i == 0 or w[i - 1] not in DETERMINERS)]
    ks = vs[1:] if len(vs) >= 2 else []
    if not ks:
        return [text]
    starts = [m.start() for m in WORD_RE.finditer(text)]
    bounds = [0] + [starts[k] for k in ks] + [len(text)]
    return [text[bounds[i]:bounds[i + 1]].strip() for i in range(len(bounds) - 1)]


def clauses_of(stage: str) -> list:
    items, last = [], 0
    for m in SEP_RE.finditer(stage):
        items.append(stage[last:m.start()])
        items.append(("sep", m.group(0)))
        last = m.end()
    items.append(stage[last:])
    intro, out = "start", []
    for it in items:
        if isinstance(it, tuple):
            intro = join_intro(intro, conn_kind(it[1]))
        elif it.strip():
            parts = verb_split(it.strip())
            out.append((intro, parts[0]))
            out += [("and", p) for p in parts[1:]]
            intro = "none"
    return out


def new_step_q(p: dict, c: dict) -> bool:
    """A comma starts a new step when both sides have their own motion verb, as in a list of actions."""
    return (c["Intro"] == "comma" and p["HasVerb"] and c["HasVerb"] and not p["IngStart"] and not c["IngStart"]
            and p["Intro"] != "while")


def groups_of(stage: str, o: dict) -> list:
    cl = []
    for intro, text in clauses_of(stage):
        r = read_clause(text, o)
        if r is not None:
            r["Intro"] = intro
            cl.append(r)
    groups, cur = [], []
    for c in cl:
        if cur and new_step_q(cur[-1], c):
            groups.append(cur)
            cur = [c]
        else:
            cur.append(c)
    if cur:
        groups.append(cur)
    return groups


def sentence_groups(t: str, o: dict) -> list:
    """All the groups of a sentence, in order; each part also notes the part before it ("Prev") and how it
    was joined ("then" at the start of a later step), for the subject check."""
    gl = []
    for i, st in enumerate(stages_of(t)):
        for g in groups_of(st, o):
            if i > 0:
                for c in g:
                    if c["Intro"] == "start":
                        c["Intro"] = "then"
            gl.append(g)
    prev = ""
    for g in gl:
        for c in g:
            c["Prev"] = prev
            prev = c["Text"]
    return gl


def settle_group(g: list, o: dict):
    """Keep the motion parts of a step, set the rest aside, and join stray words to the spin they describe."""
    keep, skipped = [], []
    verb_q = any(c["HasVerb"] and not c["Negated"] and c["Kind"] != "unknown" for c in g)
    check = o.get("SubjectCheck")
    for c in g:
        if c["Negated"]:
            skipped.append({"Text": c["Text"], "Reason": "negated"})
        elif c["Kind"] == "unknown":
            skipped.append({"Text": c["Text"], "Reason": "no motion words"})
        elif c["Kind"] == "translate" and not c["HasVerb"] and not verb_q:
            skipped.append({"Text": c["Text"], "Reason": "a direction with no motion verb"})
        elif c["Kind"] == "translate" and c["Bare"]:
            skipped.append({"Text": c["Text"], "Reason": "a motion verb with no direction or distance"})
        elif check is not None and c["HasVerb"] and (r := motion_subject(c)) is not None and check(r) == "other":
            skipped.append({"Text": c["Text"], "Reason": "about something else (subject check)"})
        else:
            keep.append(c)
    spin_at = next((i for i, c in enumerate(keep) if c["Kind"] in ("spin", "orbit") and c["HasVerb"]), None)
    if spin_at is not None:
        frags = [c for c in keep if not c["HasVerb"] and (c["Kind"] == "spin" or (c["Kind"] == "translate" and c["AxisOnly"]))]
        if frags:
            keep[spin_at] = read_clause(" ".join([keep[spin_at]["Text"]] + [f["Text"] for f in frags]), o)
            keep = [c for c in keep if not any(c is f for f in frags)]
    return keep, skipped


# ---------- Reading one part ----------

def negated_q(text: str) -> bool:
    return re.search(r"\b(?:not|never|cannot|dont|no longer)\b|n't\b", text) is not None


def damerau_levenshtein(a: str, b: str) -> int:
    """Edits between two words: deletions, insertions, substitutions and swaps of neighbours."""
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[len(a)][len(b)]


def _load_near_words() -> set:
    path = os.path.join(os.path.dirname(__file__), "data", "near_words.txt")
    try:
        with open(path, encoding="utf-8") as f:
            return {w.strip() for w in f if w.strip() and not w.startswith("#")}
    except OSError:
        return set()


# Real English words within the correction distance of a motion word (from Wolfram's DictionaryWordQ):
# a word on this list is never "corrected"
NEAR_WORDS = _load_near_words()
_LONG_KNOWN = [k for k in KNOWN if len(k) >= 5]
_corrections: dict = {}


def correct_word(w: str) -> str:
    if w in _corrections:
        return _corrections[w]
    if len(w) < 5 or w in KNOWN_SET or NUMBER_RE.fullmatch(w) or w in NEAR_WORDS:
        out = w
    else:
        d = 1 if len(w) <= 6 else 2
        cands = [k for k in _LONG_KNOWN if k[0] == w[0] and damerau_levenshtein(w, k) <= d]
        out = min(cands, key=lambda k: damerau_levenshtein(w, k)) if cands else w     # first of the nearest
    _corrections[w] = out
    return out


def read_clause(text: str, o: dict):
    w0 = words(text)
    if not w0:
        return None
    corr, w = [], []
    for x in w0:
        y = correct_word(x)
        if y != x:
            corr.append((x, y))
        w.append(y)
    first_verb = next((x for x in w if x in VF_SET), None)
    r = read_words(text, w, o)
    r.update({"HasVerb": first_verb is not None,
              "IngStart": first_verb is not None and first_verb.endswith("ing"),
              "Negated": negated_q(text), "Corrections": corr})
    return r


def number_value(w: list):
    v = VOCABULARY["numbers"]
    ws = [x for x in w if x in v or NUMBER_RE.fullmatch(x)]
    if not set(ws) - {"a", "an"}:
        return None
    total = Fraction(1)
    for x in ws:
        if x in ("andahalf", "andaquarter"):
            continue
        total *= v[x] if x in v else Fraction(x)
    return total + (Fraction(1, 2) if "andahalf" in ws else 0) + (Fraction(1, 4) if "andaquarter" in ws else 0)


def not_understood(w: list) -> list:
    out = []
    for x in w:
        if x not in KNOWN_SET and not NUMBER_RE.fullmatch(x) and x not in out:
            out.append(x)
    return out


def _normalize(v):
    v = np.array(v, dtype=float)
    return v / np.linalg.norm(v)


def read_words(text: str, w: list, o: dict) -> dict:
    v = VOCABULARY
    has = lambda key: any(x in v[key] for x in w)
    n = number_value(w)
    axis_w = [x for x in w if x in v["axes"]]
    axis_q = bool(axis_w)
    axis = v["axes"][axis_w[0]] if axis_q else (0, 0, 1)
    sense_w = [x for x in w if x in v["senses"]]
    lr = [x for x in w if x in ("left", "right")]
    dir_w = [x for x in w if x in v["directions"]]
    if "back" in dir_w and set(dir_w) & {"up", "upward", "upwards", "down", "downward", "downwards"}:
        dir_w = [x for x in dir_w if x != "back"]                 # "raise it back up": back means again
    if has("pause"):
        kind = "pause"
    elif "path" in w or has("follow"):
        kind = "path"
    elif has("orbit") or (set(w) & {"around", "about"} and set(w) & {"origin", "center", "point"}):
        kind = "orbit"
    elif has("spin") or (sense_w and not has("translate")):
        kind = "spin"
    elif has("rise") or has("sink") or has("translate") or dir_w or axis_q:
        kind = "translate"
    else:
        kind = "unknown"
    base = {"Text": text, "Kind": kind}
    assumed, axis_only, bare = [], False, False
    if kind in ("spin", "orbit"):
        if not axis_q:
            assumed.append("no axis: z (vertical) assumed")
        if sense_w:
            sense = v["senses"][sense_w[0]]
        elif kind == "spin" and lr:
            sense = 1 if lr[0] == "left" else -1
        else:
            assumed.append("no direction of turning: counterclockwise assumed")
            sense = 1
        if n is not None:
            unit = math.pi / 180 if set(w) & {"degree", "degrees"} else 1.0 if set(w) & {"radian", "radians"} else 2 * math.pi
            ang = float(n) * unit
        elif kind == "spin" and lr:
            assumed.append(f"no amount: a quarter turn assumed (turn {lr[0]})")
            ang = math.pi / 2
        elif kind == "spin" and "around" in w and set(w) & {"turn", "turns", "turned", "turning"} and not axis_q:
            assumed.append('"turn around": a half turn')
            ang = math.pi
        else:
            assumed.append("no amount: one full turn assumed")
            ang = 2 * math.pi
        base.update({"Axis": axis, "Sense": sense, "Angle": ang})
        if kind == "orbit":
            base["Centre"] = (0, 0, 0) if "origin" in w else tuple(o["Centre"])
    elif kind == "translate":
        if dir_w:
            vec = tuple(np.sum([v["directions"][x] for x in dir_w], axis=0))
        elif has("rise"):
            vec = (0, 0, 1)
        elif has("sink"):
            vec = (0, 0, -1)
        elif axis_q:
            axis_only = not (has("translate") or has("rise") or has("sink"))
            vec = axis
        else:
            bare = n is None
            assumed.append("no direction: forward (+y) assumed")
            vec = (0, 1, 0)
        if not any(vec):
            assumed.append("the directions cancel: no movement")
            vec = np.zeros(3)
        else:
            vec = _normalize(vec)
        if n is None:
            assumed.append(f"no distance: {o['Step']} unit assumed")
            dist = o["Step"]
        else:
            dist = n
        base.update({"Vector": vec, "Distance": float(dist)})
    elif kind == "path":
        if not o["PathGiven"]:
            assumed.append("no path given: the default curve {3 t, Sin[2 Pi t], 0} is used")
        if dir_w or has("rise") or has("sink"):            # "move upwards along the path"
            vec = _normalize(np.sum([v["directions"][x] for x in dir_w], axis=0) if dir_w else (0, 0, 1) if has("rise") else (0, 0, -1))
            base.update({"Vector": vec, "Distance": float(o["Step"] if n is None else n)})
    base.update({"Assumed": assumed, "NotUnderstood": not_understood(w), "AxisOnly": axis_only, "Bare": bare})
    return base


# ---------- What a subject check sees of a motion part (see subjectnet.py) ----------

def motion_subject(c: dict):
    w = words(c["Text"])
    i = next((k for k, x in enumerate(w) if x in VF_SET), None)
    if i is None:
        return None
    return {"Text": c["Text"], "Own": w[:i], "Verb": w[i], "After": w[i + 1:],
            "Prev": words(c.get("Prev", "")) if i == 0 else [], "Join": c.get("Intro", "start")}


# ---------- Reading a text ----------

def options(path=None, centre=(0, 0, 0), step=1, frame="World", subject_check=None) -> dict:
    return {"Path": resolve_path(path), "PathGiven": path is not None, "Centre": tuple(_pad3(centre)), "Step": step,
            "Frame": frame, "SubjectCheck": subject_check}


def read_text(text: str, o: dict):
    """The steps found, what was set aside, and the figures of speech."""
    stages, skipped, idioms = [], [], []
    for sent in sentences(text):
        if sent.endswith("?"):
            skipped.append({"Text": sent, "Reason": "a question"})
            continue
        t, ids = normalise(sent)
        idioms += ids
        for g in sentence_groups(t, o):
            kept, sk = settle_group(g, o)
            skipped += sk
            if kept:
                stages.append(kept)
    seen, uniq = set(), []
    for i in (x.strip() for x in idioms):
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    return stages, skipped, uniq


def motion_find(text: str, **opts) -> dict:
    """The motion parts found in a text, step by step, and the parts set aside with the reason."""
    stages, skipped, idioms = read_text(text, options(**opts))
    return {"Motions": [[c["Text"] for c in st] for st in stages], "Set aside": skipped, "Figures of speech": idioms}


# ---------- From parts to poses ----------

def _pad3(p):
    p = list(p)
    return (p + [0, 0, 0])[:3]


def resolve_path(path):
    if path is None:
        return lambda s: np.array([3 * s, math.sin(2 * math.pi * s), 0.0])
    if callable(path):
        return lambda s: np.array(_pad3(path(s)), dtype=float)
    pts = np.array([_pad3(p) for p in path], dtype=float)
    if len(pts) == 1:
        return lambda s: pts[0]

    def f(s):
        k = min(int(s * (len(pts) - 1)), len(pts) - 2)
        u = s * (len(pts) - 1) - k
        return pts[k] + (pts[k + 1] - pts[k]) * u
    return f


def rotation(theta: float, axis, centre=(0, 0, 0)) -> np.ndarray:
    """RotationTransform[theta, axis, centre] as a 4 x 4 matrix (counterclockwise about the axis)."""
    a = _normalize(axis)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    r = np.eye(3) + math.sin(theta) * k + (1 - math.cos(theta)) * (k @ k)
    m = np.eye(4)
    m[:3, :3] = r
    c = np.array(centre, dtype=float)
    m[:3, 3] = c - r @ c
    return m


def translation(v) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = v
    return m


def _framed(M, vec, o):
    return M @ vec if o["Frame"] == "Object" else vec


def _offset(a, o, M, u):
    if a["Kind"] == "translate":
        return _framed(M, a["Distance"] * np.asarray(a["Vector"], dtype=float), o) * u
    if a["Kind"] == "path":
        off = _framed(M, o["Path"](u) - o["Path"](0), o)
        if "Vector" in a:
            off = off + _framed(M, a["Distance"] * np.asarray(a["Vector"], dtype=float), o) * u
        return off
    return np.zeros(3)


def stage_matrix(parts, P0, M, o, u) -> np.ndarray:
    """One step at step time u: orbits . translation to the current position . spins . orientation so far."""
    off = sum((_offset(a, o, M, u) for a in parts if a["Kind"] in ("translate", "path")), np.zeros(3))
    m = np.eye(4)
    for a in parts:
        if a["Kind"] == "orbit":
            m = m @ rotation(a["Sense"] * a["Angle"] * u, a["Axis"], a["Centre"])
    m = m @ translation(np.asarray(P0, dtype=float) + off)
    for a in parts:
        if a["Kind"] == "spin":
            m = m @ rotation(a["Sense"] * a["Angle"] * u, a["Axis"])
    affine = np.eye(4)
    affine[:3, :3] = M
    return m @ affine


def motion_parse(text: str, **opts) -> dict:
    o = options(**opts)
    stages, skipped, idioms = read_text(text, o)
    starts, P0, M = [], np.zeros(3), np.eye(3)
    for st in stages:
        starts.append((P0, M))
        end = stage_matrix(st, P0, M, o, 1.0)
        P0, M = end[:3, 3], end[:3, :3]
    return {"Phrase": text, "Stages": stages, "Starts": starts, "End": {"Position": P0, "Orientation": M},
            "Skipped": skipped, "Idioms": idioms, "Options": o}


def motion_transform(text: str, t: float, **opts) -> np.ndarray:
    """The pose (a 4 x 4 matrix) at time t, from 0 to 1 over the whole text."""
    p = motion_parse(text, **opts)
    n = len(p["Stages"])
    if n == 0:
        return np.eye(4)
    k = min(max(math.floor(t * n), 0), n - 1)
    P0, M = p["Starts"][k]
    return stage_matrix(p["Stages"][k], P0, M, p["Options"], t * n - k)
