"""SubjectNet, in Python: a port of nets/SubjectNet.nb, trained with our own code (ccn_nets.nn).

Decides whether a motion part is about the object being moved ("the drone should rise 4 metres",
"spin twice") or about something else ("Mia turned to her brother", "the camera holds on the kettle").
The training data is made from templates; the nouns and names used for testing are kept out of
training, and no conversational-construct labels anything.

    python3 -m ccn_nets.subjectnet          train, run the four tests and print the comparison

By Dara O Shayda and Hikari Noor Hoshino (星野ヌール)
AI System Programming Laboratory

© Computational Classnotes · CC BY-NC-SA 4.0
"""

from __future__ import annotations

import json
import os
import random
import time
import zlib

import numpy as np

from . import motion
from .nn import Net, gradient_check, train

CLASSES = ["object", "other"]
DIM = 2048

# ---------- Template data: sentences about the object, and about something else ----------

def fillers(split: str) -> dict:
    """Words for training and words for testing are kept apart, so the test shows what the net learnt
    about sentence shape, not the words themselves."""
    tr = split == "train"
    return {
        "thing": ["drone", "robot", "box", "cube", "ball", "car", "platform", "arm", "statue", "cart", "puppet",
                  "rocket", "boat", "wheel", "block", "toy", "marker", "figure", "crane", "tray"] if tr else
                 ["teapot", "kite", "sphere", "gripper", "model", "satellite", "barrel", "lamp"],
        "adj": ["", "", "red ", "small ", "old ", "blue ", "metal ", "wooden "] if tr else ["", "", "brass ", "green ", "tiny "],
        "name": ["Sam", "Leo", "Omar", "Yuki", "Priya", "Tom", "Lena", "Ravi"] if tr else ["Mia", "Noor", "Jonas", "Aisha"],
        "human": ["the guide", "the teacher", "the crowd", "the audience", "my sister", "the pilot", "the driver",
                  "the children"] if tr else ["the visitors", "the team", "her friend", "the porter"],
        "relation": ["sister", "friend", "mother", "teacher", "father"] if tr else ["brother", "uncle", "cousin"],
        "abstract": ["the news", "the music", "the idea", "the story", "the result", "the film"] if tr else
                    ["the experience", "the lecture", "the painting"],
        "mind": ["mood", "mind", "attention", "view", "plans"] if tr else ["sense of scale", "thinking", "opinion"],
        "watcher": ["the camera", "the spotlight", "the narrator", "the lens"] if tr else ["the shot", "the viewer"],
        "place": ["Dublin", "Paris", "Lagos", "Tokyo", "Cairo"] if tr else ["Lisbon", "Galway"],
        "say": ["said", "think", "felt"] if tr else ["say", "believe"],
    }


# Motion and other words shared by both splits
IMPERATIVE = ["spin twice counterclockwise", "move left 2 units", "rise 3 metres", "turn to the left", "rotate 90 degrees clockwise",
              "slide back 2 units", "drop 1 unit", "orbit the origin once", "turn right", "move forward 4", "climb 2 metres",
              "spin around once", "pivot 45 degrees", "go up 2", "rotate it 30 degrees", "lift it up 2 units"]
THIRD = ["spins twice counterclockwise", "moves left 2 units", "rises 3 metres", "turns to the left", "rotates 90 degrees clockwise",
         "slides back 2 units", "drops 1 unit", "orbits the origin once", "turns right", "moves forward 4", "climbs 2 metres",
         "spins around once", "pivots 45 degrees"]
PAST = ["spun twice", "moved left 2 units", "rose 3 metres", "turned to the left", "rotated 90 degrees", "slid back 2 units",
        "dropped 1 unit", "orbited the origin once", "turned right", "moved forward 4", "climbed 2 metres"]
QUIET3 = ["wobbles", "hums", "glows", "blinks", "beeps", "settles", "flickers", "clicks"]
QUIET_PAST = ["laughed", "smiled", "sighed", "nodded", "waved", "shrugged", "coughed", "grinned"]
POSS = ["her", "his", "their", "our"]


def templates(split: str, rng: random.Random) -> dict:
    f = fillers(split)
    rc = rng.choice
    thing = lambda: rc(f["adj"]) + rc(f["thing"])
    return {
        "object": [
            lambda: rc(["", "please ", "now ", "just "]) + rc(IMPERATIVE),
            lambda: "to " + rc(["see", "check", "inspect", "show"]) + " the " + thing() + ", " + rc(IMPERATIVE),
            lambda: rc(f["name"]) + ", " + rc(IMPERATIVE),
            lambda: "the " + thing() + " " + rc(["should", "will", "must", "can"]) + " " + rc(IMPERATIVE),
            lambda: "the " + thing() + " " + rc(THIRD),
            lambda: "it " + rc(["", "then ", "slowly ", "now "]) + rc(THIRD),
            lambda: "the " + thing() + " " + rc(QUIET3) + ", then " + rc(THIRD),
            lambda: "the " + thing() + " " + rc(QUIET3) + " and " + rc(THIRD),
            lambda: "the " + thing() + " " + rc(PAST),
            lambda: "it " + rc(PAST) + ", " + rc(PAST),
            lambda: "every " + rc(["evening", "hour", "morning"]) + " the " + thing() + " " + rc(THIRD)],
        "other": [
            lambda: rc(f["name"]) + " " + rc(QUIET_PAST) + " and " + rc(["turned to", "turned towards", "spun around to face", "stepped back from"]) + " " + rc(POSS) + " " + rc(f["relation"]),
            lambda: rc(f["name"] + f["human"]) + " " + rc(["turned to", "turned towards"]) + " " + rc(POSS) + " " + rc(f["relation"]),
            lambda: rc(f["watcher"]) + " " + rc(["holds on", "stays on", "moves slowly toward", "rises above", "drifts across", "turns to"]) + " the " + thing(),
            lambda: rc(f["abstract"]) + " " + rc(["turns", "turned", "lifted", "raised", "shifted"]) + " " + rc(POSS) + " " + rc(f["mind"]),
            lambda: rc(f["human"]) + " often " + rc(f["say"]) + " " + rc(f["abstract"]) + " " + rc(["turns", "lifts", "shifts"]) + " " + rc(POSS) + " " + rc(f["mind"]),
            lambda: rc(f["name"] + f["human"]) + " " + rc(["moved to", "went back to", "flew to", "walked to", "came back from"]) + " " + rc(f["place"]) + " " + rc(["in 2 days", "twice", "last year", "after 3 weeks"]),
            lambda: rc(f["human"]) + " " + rc(["stayed", "waited", "held on"]) + " " + rc(["for 2 hours", "in the hall", "by the door", "for 1 minute"]),
            lambda: rc(f["name"] + f["human"]) + " rose from " + rc(POSS) + " " + rc(["chair", "seat", "bed"])],
    }


def parts_of(sentence: str) -> list:
    """Every motion part the reader keeps from a sentence, as the subject check would see it."""
    recs = []
    motion.motion_find(sentence, subject_check=lambda r: (recs.append(r), "object")[1])
    return recs


def make_data(split: str, n: int, seed: int) -> list:
    rng = random.Random(seed)
    t = templates(split, rng)
    out = []
    while len(out) < n:
        label = "object" if rng.random() < 0.6 else "other"
        s = rng.choice(t[label])()
        out += [(r, label) for r in parts_of(s)]      # a sentence whose parts were all set aside adds nothing
    return out[:n]


# ---------- Features: the words before the verb, the part before, the joining word, the verb, the words after ----------

def subject_features(r: dict) -> list:
    own, prev, after = r["Own"], r["Prev"], r["After"]
    f = ["own:none"] if not own else ["o:" + w for w in own] + ["oL:" + own[-1]]
    if not own:
        f += ["prev:none"] if not prev else ["p:" + w for w in prev[-min(4, len(prev)):]]
    f += ["j:" + r["Join"], "v:" + r["Verb"]]
    f += ["a:" + w for w in after[:4]]
    if len(after) >= 2:
        f.append("a2:" + after[0] + "_" + after[1])
    return f


def feature_vector(r: dict, dim: int = DIM) -> np.ndarray:
    """The features hashed into dim slots of 0s and 1s; CRC32 gives the same slots as Hash[..., "CRC32"]."""
    v = np.zeros(dim)
    for f in subject_features(r):
        v[zlib.crc32(f.encode("utf-8")) % dim] = 1.0
    return v


def one_hot(labels) -> np.ndarray:
    return np.array([[1.0, 0.0] if l == "object" else [0.0, 1.0] for l in labels])


# ---------- The subject check ----------

def subject_check(net: Net):
    """A subject check for the motion reader: motion.motion_find(text, subject_check=subject_check(net))."""
    return lambda r: CLASSES[int(net.classify(feature_vector(r)[None, :])[0])]


# ---------- The tests ----------

_TESTS = os.path.join(os.path.dirname(__file__), "data", "subjectnet_tests.json")


def test_data():
    with open(_TESTS, encoding="utf-8") as f:
        d = json.load(f)
    about = set(d["about_something_else"])
    paragraph_parts = [(r, "other" if r["Text"] in about else "object") for p in d["paragraphs"] for r in parts_of(p[0])]
    hard_parts = [(r, label) for s, label in d["hard_sentences"] for r in parts_of(s)]
    return d["paragraphs"], paragraph_parts, hard_parts


def accuracy(check, data) -> float:
    return float(np.mean([check(r) == label for r, label in data]))


def other_precision_recall(check, data):
    pred = [check(r) for r, _ in data]
    truth = [l for _, l in data]
    both = sum(p == "other" and t == "other" for p, t in zip(pred, truth))
    return both / max(1, pred.count("other")), both / max(1, truth.count("other"))


def _near(a, b) -> bool:
    return float(np.max(np.abs(a - b))) < 1e-6


def paragraph_scores(paragraphs, check) -> list:
    """For each paragraph: does it end where its short phrase ends, and does it agree step by step?"""
    out = []
    for text, short, opts in paragraphs:
        o = {k: v for k, v in opts.items()}
        end = _near(motion.motion_transform(text, 1, subject_check=check, **o), motion.motion_transform(short, 1, **o))
        steps = (len(motion.motion_parse(text, subject_check=check, **o)["Stages"]) == len(motion.motion_parse(short, **o)["Stages"])
                 and _near(motion.motion_transform(text, 0.37, subject_check=check, **o), motion.motion_transform(short, 0.37, **o)))
        out.append((end, steps))
    return out


def run(epochs=12, batch_size=64, lr=0.005, l2=1e-4, seed=1234, hidden=32, verbose=True) -> dict:
    t0 = time.perf_counter()
    train_data = make_data("train", 2000, 11)
    test = make_data("test", 600, 22)
    t_data = time.perf_counter() - t0
    x = np.array([feature_vector(r) for r, _ in train_data])
    y = one_hot([l for _, l in train_data])
    net = Net([DIM, hidden, 2], ["ReLU"]).initialise(seed)
    t0 = time.perf_counter()
    history = train(net, x, y, epochs=epochs, batch_size=batch_size, lr=lr, l2=l2, seed=seed)
    t_train = time.perf_counter() - t0
    check = subject_check(net)
    paragraphs, paragraph_parts, hard_parts = test_data()
    no_check = lambda r: "object"
    scores = paragraph_scores(paragraphs, check)
    scores_without = paragraph_scores(paragraphs, None)
    r0 = paragraph_parts[0][0]
    t0 = time.perf_counter()
    for _ in range(200):
        check(r0)
    t_check = (time.perf_counter() - t0) / 200 * 1000
    result = {
        "Training data (parts)": len(train_data), "Test data (parts)": len(test),
        "Making the data, s": round(t_data, 2), "Training time, s": round(t_train, 2),
        "Loss, first and last epoch": [round(history[0], 4), round(history[-1], 4)],
        "Gradient check, largest difference": gradient_check(),
        "Test 1: templates with unseen words, accuracy": accuracy(check, test),
        "Test 1: 'other' precision and recall": other_precision_recall(check, test),
        "Test 2: paragraph parts, accuracy": f"{sum(check(r) == l for r, l in paragraph_parts)} of {len(paragraph_parts)}",
        "Test 3: hard sentences, accuracy": f"{sum(check(r) == l for r, l in hard_parts)} of {len(hard_parts)}",
        "Test 4: paragraphs ending right": f"{sum(s[0] for s in scores)} of 12 (without the check: {sum(s[0] for s in scores_without)})",
        "Test 4: paragraphs right step by step": f"{sum(s[1] for s in scores)} of 12 (without the check: {sum(s[1] for s in scores_without)})",
        "Time to check one part, ms": round(t_check, 3),
        "Numbers in the net": net.weight_count,
        "Parts wrong (paragraphs and hard sentences)": [r["Text"] for r, l in paragraph_parts + hard_parts if check(r) != l],
    }
    if verbose:
        for k, v in result.items():
            print(f"{k}: {v}")
    return {"net": net, "result": result, "history": history}


if __name__ == "__main__":
    run()
