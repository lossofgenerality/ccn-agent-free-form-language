"""Our own neural-net code, in Python.

Every piece of a small feed-forward net is written out here: the layers, the activations (ReLU, Tanh,
Sigmoid, none), softmax, cross-entropy with L2, the forward pass, backpropagation, Adam, the initial
weights and a gradient check. NumPy is used only for arrays and their arithmetic (dot products, exp,
log, sums), as Dot, Exp and Total are used in the Wolfram version A. No neural-net library is used.

The arithmetic follows version A of nets/SubjectNet.nb step for step, so that a net started from the
same weights and given the same batches in the same order learns the same weights in both languages.

By Dara O Shayda and Hikari Noor Hoshino (星野ヌール)
AI System Programming Group

© Computational Classnotes · CC BY-NC-SA 4.0
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

import numpy as np

# ---------- Activations: the function, and its derivative given the sums z and the outputs a ----------

def _relu(z):
    return z * (z >= 0)          # as z UnitStep[z] in Wolfram: UnitStep[0] = 1


def _relu_d(z, a):
    return (z >= 0).astype(z.dtype)


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


ACTIVATIONS = {
    "ReLU": (_relu, _relu_d),
    "Tanh": (np.tanh, lambda z, a: 1.0 - a * a),
    "Sigmoid": (_sigmoid, lambda z, a: a * (1.0 - a)),
    "None": (lambda z: z, lambda z, a: np.ones_like(z)),
}


def softmax_rows(z: np.ndarray) -> np.ndarray:
    """Softmax of each row, shifted by the row's largest value so that exp never overflows."""
    e = np.exp(z - z.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def cross_entropy(p: np.ndarray, y: np.ndarray) -> float:
    """Mean cross-entropy of predicted probabilities p against one-hot targets y."""
    return float(-np.mean(np.sum(y * np.log(p + 1e-12), axis=1)))


# ---------- The net: dense layers, each with an activation, and softmax at the end ----------

@dataclass
class Net:
    """A chain of dense layers. sizes = [inputs, hidden..., classes]; one activation per hidden layer."""
    sizes: list
    activations: list
    params: list = field(default_factory=list)       # one {"W": (in, out), "b": (out,)} per layer

    def __post_init__(self):
        if len(self.activations) != len(self.sizes) - 2:
            raise ValueError("one activation per hidden layer: len(activations) == len(sizes) - 2")
        for a in self.activations:
            if a not in ACTIVATIONS:
                raise ValueError(f"unknown activation {a!r}; use one of {sorted(ACTIVATIONS)}")

    # The initial weights: normal with standard deviation sqrt(2 / inputs), biases 0 (He initialisation)
    def initialise(self, seed: int | None = None) -> "Net":
        rng = np.random.default_rng(seed)
        self.params = [{"W": rng.normal(0.0, math.sqrt(2.0 / self.sizes[k]), (self.sizes[k], self.sizes[k + 1])),
                        "b": np.zeros(self.sizes[k + 1])} for k in range(len(self.sizes) - 1)]
        return self

    @property
    def weight_count(self) -> int:
        return sum(p["W"].size + p["b"].size for p in self.params)

    # Forward pass: Z are the sums before the activation, A the outputs of each layer (A[0] is the input)
    def forward(self, x: np.ndarray):
        a, zs, outs = x, [], [x]
        last = len(self.params) - 1
        for k, p in enumerate(self.params):
            z = a @ p["W"] + p["b"]
            a = softmax_rows(z) if k == last else ACTIVATIONS[self.activations[k]][0](z)
            zs.append(z)
            outs.append(a)
        return zs, outs

    def probabilities(self, x: np.ndarray) -> np.ndarray:
        return self.forward(np.atleast_2d(x))[1][-1]

    def classify(self, x: np.ndarray) -> np.ndarray:
        """The index of the most probable class of each row (the first, on a tie, as Ordering in Wolfram)."""
        return np.argmax(self.probabilities(x), axis=1)

    def loss(self, x, y, l2: float) -> float:
        return cross_entropy(self.probabilities(x), y) + l2 / 2 * sum(float(np.sum(p["W"] ** 2)) for p in self.params)

    # Backpropagation, written out, from the last layer to the first
    def gradients(self, x, y, l2: float):
        zs, outs = self.forward(x)
        n = len(x)
        dz = (outs[-1] - y) / n                        # softmax with cross-entropy: p - y
        grads = [None] * len(self.params)
        for k in range(len(self.params) - 1, -1, -1):
            p = self.params[k]
            grads[k] = {"W": outs[k].T @ dz + l2 * p["W"], "b": dz.sum(axis=0)}
            if k > 0:
                dz = (dz @ p["W"].T) * ACTIVATIONS[self.activations[k - 1]][1](zs[k - 1], outs[k])
        return grads

    # ---------- Saving and loading: JSON for the shape, NumPy's .npz for the weights ----------

    def save(self, path: str) -> None:
        arrays = {f"{key}{k}": p[key] for k, p in enumerate(self.params) for key in ("W", "b")}
        np.savez(path, **arrays, spec=json.dumps({"sizes": self.sizes, "activations": self.activations}))

    @classmethod
    def load(cls, path: str) -> "Net":
        data = np.load(path, allow_pickle=False)
        spec = json.loads(str(data["spec"]))
        net = cls(spec["sizes"], spec["activations"])
        net.params = [{"W": data[f"W{k}"], "b": data[f"b{k}"]} for k in range(len(spec["sizes"]) - 1)]
        return net


# ---------- Adam, written out ----------

class Adam:
    def __init__(self, lr=0.005, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps = lr, b1, b2, eps
        self.t, self.m, self.v = 0, None, None

    def step(self, params, grads):
        if self.m is None:
            self.m = [{k: np.zeros_like(a) for k, a in p.items()} for p in params]
            self.v = [{k: np.zeros_like(a) for k, a in p.items()} for p in params]
        self.t += 1
        b1, b2, t = self.b1, self.b2, self.t
        for p, g, m, v in zip(params, grads, self.m, self.v):
            for k in p:
                m[k] = b1 * m[k] + (1 - b1) * g[k]
                v[k] = b2 * v[k] + (1 - b2) * g[k] ** 2
                p[k] = p[k] - self.lr * (m[k] / (1 - b1 ** t)) / (np.sqrt(v[k] / (1 - b2 ** t)) + self.eps)


def train(net: Net, x, y, epochs=12, batch_size=64, lr=0.005, l2=1e-4, seed=1234, batches=None):
    """Mini-batch training with Adam. Returns the loss after each epoch.
    batches: optional list (one per epoch) of lists of index arrays, to fix the order of the batches."""
    rng = np.random.default_rng(seed)
    opt = Adam(lr)
    history = []
    for e in range(epochs):
        if batches is not None:
            order = batches[e]
        else:
            perm = rng.permutation(len(x))
            order = [perm[i:i + batch_size] for i in range(0, len(x), batch_size)]
        for idx in order:
            opt.step(net.params, net.gradients(x[idx], y[idx], l2))
        history.append(net.loss(x, y, l2))
    return history


# ---------- The written-out gradient against small finite differences ----------

def gradient_check(activations=("ReLU",), classes=2, seed=5, eps=1e-5, l2=0.01) -> float:
    """The largest difference between backpropagation and central differences, on a small net of the
    given shape, at two random entries of every weight array and bias."""
    rng = np.random.default_rng(seed)
    sizes = [10] + [4] * len(activations) + [classes]
    net = Net(sizes, list(activations)).initialise(9)
    x = rng.uniform(0, 1, (6, 10))
    y = np.eye(classes)[rng.integers(0, classes, 6)]
    g = net.gradients(x, y, l2)
    worst = 0.0
    for k, p in enumerate(net.params):
        for key in ("W", "b"):
            for _ in range(2):
                pos = tuple(rng.integers(0, s) for s in p[key].shape)
                old = p[key][pos]
                p[key][pos] = old + eps
                up = net.loss(x, y, l2)
                p[key][pos] = old - eps
                down = net.loss(x, y, l2)
                p[key][pos] = old
                worst = max(worst, abs((up - down) / (2 * eps) - g[k][key][pos]))
    return worst
