"""Tests of the Python version against the Wolfram one.

    cd python && python3 -m unittest discover -s tests -v

The reference values in wolfram_reference.json were computed by the Wolfram notebooks
(motion/MotionPhrases.nb and nets/SubjectNet.nb, and version A's arithmetic) on 24 November 2026.

© Computational Classnotes · CC BY-NC-SA 4.0
"""

import json
import math
import os
import sys
import unittest
import zlib

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ccn_nets import motion, subjectnet                      # noqa: E402
from ccn_nets.nn import Net, gradient_check, train           # noqa: E402

HERE = os.path.dirname(__file__)
REF = json.load(open(os.path.join(HERE, "wolfram_reference.json"), encoding="utf-8"))
DATA = json.load(open(os.path.join(HERE, "..", "ccn_nets", "data", "subjectnet_tests.json"), encoding="utf-8"))


def canon(s: str) -> str:
    """The records a subject check sees, the motion parts and what was set aside, as one string
    (the same string is built in Wolfram)."""
    recs = subjectnet.parts_of(s)
    rc = " ; ".join(" ".join(r["Own"]) + "|" + r["Verb"] + "|" + " ".join(r["After"]) + "|" + " ".join(r["Prev"]) + "|" + r["Join"] for r in recs)
    f = motion.motion_find(s)
    mf = " || ".join(" // ".join(st) for st in f["Motions"]) + " ## " + " ; ".join(x["Text"] + "=>" + x["Reason"] for x in f["Set aside"])
    return rc + " @@ " + mf


def crc(s: str) -> int:
    return zlib.crc32(canon(s).encode("utf-8"))


class TestOwnNet(unittest.TestCase):
    def test_gradient_check(self):
        self.assertLess(gradient_check(("ReLU",)), 1e-8)
        self.assertLess(gradient_check(("Tanh", "Sigmoid", "None"), classes=3), 1e-8)

    def test_softmax_rows_sum_to_one(self):
        from ccn_nets.nn import softmax_rows
        p = softmax_rows(np.array([[1000.0, 0.0, -1000.0], [1.0, 2.0, 3.0]]))
        self.assertTrue(np.allclose(p.sum(axis=1), 1.0))
        self.assertTrue(np.all(np.isfinite(p)))

    def test_training_matches_wolfram(self):
        """Same starting weights and batches as Wolfram's version A: the same losses and weights."""
        x = np.array([[1.0 if ((i * 7 + j * 13) % 5 == 0 or (i + j) % 4 == 0) else 0.0 for j in range(1, 31)] for i in range(1, 41)])
        y = np.array([[0.0, 1.0] if i % 3 == 0 else [1.0, 0.0] for i in range(1, 41)])
        net = Net([30, 6, 2], ["ReLU"])
        net.params = [{"W": np.array([[math.sin(i + 2 * j) / 10 for j in range(1, 7)] for i in range(1, 31)]), "b": np.zeros(6)},
                      {"W": np.array([[math.cos(i * j) / 5 for j in range(1, 3)] for i in range(1, 7)]), "b": np.zeros(2)}]
        order = [np.arange(0, 16), np.arange(16, 32), np.arange(32, 40)]
        h = train(net, x, y, epochs=5, lr=0.01, l2=0.001, batches=[order] * 5)
        t = REF["training"]
        self.assertLess(max(abs(a - b) for a, b in zip(h, t["loss_history"])), 1e-12)
        self.assertAlmostEqual(net.params[0]["W"].sum(), t["sum_W1"], places=12)
        self.assertAlmostEqual(net.params[1]["W"].sum(), t["sum_W2"], places=12)
        self.assertTrue(np.allclose(net.params[1]["b"], t["b2"], atol=1e-12))
        self.assertAlmostEqual(net.params[0]["W"][2, 3], t["W1_3_4"], places=12)

    def test_save_and_load(self):
        import tempfile
        net = Net([8, 4, 3], ["Tanh"]).initialise(3)
        x = np.random.default_rng(1).uniform(size=(5, 8))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "net.npz")
            net.save(path)
            self.assertTrue(np.allclose(Net.load(path).probabilities(x), net.probabilities(x)))


class TestReader(unittest.TestCase):
    def test_hash_matches_wolfram(self):
        for s, h in REF["hash_crc32"].items():
            self.assertEqual(zlib.crc32(s.encode("utf-8")), h, s)

    def test_paragraphs_match_wolfram(self):
        r = REF["reader_crc32"]
        self.assertEqual([crc(p[0]) for p in DATA["paragraphs"]], r["paras"])
        self.assertEqual([crc(p[1]) for p in DATA["paragraphs"]], r["shorts"])
        self.assertEqual([crc(h[0]) for h in DATA["hard_sentences"]], r["hard"])

    def test_slips_and_templates_match_wolfram(self):
        self.assertEqual([crc(s) for s in REF["reader_more_sentences"]], REF["reader_more_crc32"])

    def test_poses_match_wolfram(self):
        for i, (text, short, o) in enumerate(DATA["paragraphs"]):
            opts = {"frame": o["frame"]} if o else {}
            for j, t in enumerate((1, 0.37)):
                p = motion.motion_transform(short, t, **opts)[:3].flatten()
                self.assertLess(np.abs(p - REF["poses_short"][i][j]).max(), 1e-8, (short, t))
            p = motion.motion_transform(text, 1, **opts)[:3].flatten()
            self.assertLess(np.abs(p - REF["poses_paragraph"][i]).max(), 1e-8, text[:40])

    def test_first_phrase(self):
        f = motion.motion_find("move along the path while spinning counterclokwise and move upwards")
        self.assertEqual(f["Motions"], [["move along the path", "spinning counterclokwise", "move upwards"]])


class TestSubjectNet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = subjectnet.run(verbose=False)["result"]

    def test_weights(self):
        self.assertEqual(self.out["Numbers in the net"], 65634)

    def test_results(self):
        self.assertGreaterEqual(self.out["Test 1: templates with unseen words, accuracy"], 0.98)
        self.assertEqual(self.out["Test 2: paragraph parts, accuracy"], "47 of 47")
        self.assertTrue(self.out["Test 4: paragraphs right step by step"].startswith("12 of 12"))


if __name__ == "__main__":
    unittest.main()
