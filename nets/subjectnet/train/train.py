"""Train SubjectNet with our own code, record the run, and export the data for the 3D view.

    python3 nets/subjectnet/train/train.py [run-name]        (from the repository root)

The run goes to nets/subjectnet/runs/<date>-<run-name>/ (never overwritten), the 3D view's data to
nets/subjectnet/viz/viewer-data.json, and card.json is pointed at the new run.

It needs the lab's toolkit, ccn-net-lab, checked out beside this repository, or its path in the
environment variable CCN_NET_LAB.

By Dara O Shayda and Hikari Noor Hoshino (星野ヌール)
AI System Programming Group

© Computational Classnotes · CC BY-NC-SA 4.0
"""
import json, os, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
NET = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(NET))
LAB = os.environ.get("CCN_NET_LAB", os.path.join(os.path.dirname(REPO), "ccn-net-lab"))
sys.path[:0] = [os.path.join(REPO, "python"), LAB]

from ccn_nets import subjectnet as S          # noqa: E402  (this project's net, data and tests)
from ccnlab import export                     # noqa: E402  (the lab's run records and exports)

SETTINGS = {"epochs": 12, "batch_size": 64, "lr": 0.005, "l2": 1e-4, "seed": 1234, "hidden": 32,
            "optimiser": "Adam (0.9, 0.999, 1e-8)", "initialisation": "He, seed 1234",
            "training data": "2000 template parts (seed 11)", "test data": "600 template parts with unseen words (seed 22)"}


def examples(net):
    """The sentences shown in the 3D view: two worked examples, then object and other parts from the
    tests, then two that the net gets wrong."""
    _, pp, hp = S.test_data()
    pool, out, seen = pp + hp, [], set()

    def add(r, label):
        f = S.subject_features(r)
        out.append({"text": r["Text"], "label": label, "features": f,
                    "slots": [zlib.crc32(t.encode("utf-8")) % S.DIM for t in f]})
        seen.add(r["Text"])
    for s, label in [("slide it right 2 units", "object"), ("mia turned to her brother", "other")]:
        for r in S.parts_of(s):
            add(r, label)
    for r, l in [(r, l) for r, l in pool if l == "object" and r["Text"] not in seen][:4] + \
                [(r, l) for r, l in pool if l == "other" and r["Text"] not in seen][:5]:
        add(r, l)
    wrong = [(r, l) for r, l in pool if r["Text"] not in seen and S.CLASSES[int(net.classify(S.feature_vector(r)[None, :])[0])] != l]
    for r, l in wrong[:2]:
        add(r, l)
    return out


def main(name="seed1234"):
    out = S.run(verbose=False, **{k: SETTINGS[k] for k in ("epochs", "batch_size", "lr", "l2", "seed", "hidden")})
    net, result, history = out["net"], out["result"], out["history"]
    timings = {"making the data, s": result.pop("Making the data, s"), "training, s": result.pop("Training time, s"),
               "checking one part, ms": result.pop("Time to check one part, ms")}
    path = export.save_run(net, os.path.join(NET, "runs"), name, settings=SETTINGS, metrics=result,
                           history=history, timings=timings)
    run_id = os.path.basename(path)
    view = export.dense2_viewer_data(
        net, examples(net), name="SubjectNet", classes=S.CLASSES, input_noun="sentence", run_id=run_id,
        title=f"Fly over SubjectNet: {net.weight_count:,} numbers deciding one sentence",
        credit="SubjectNet, trained with our own NumPy code (ccn_nets).",
        look_for=["Sentences about the moved object switch off many hidden units at ReLU; sentences about something else switch off few, and W₂ reads the difference.",
                  "Words never seen in training have columns of almost zero: the net decides from the shapes it learnt, not from those words.",
                  "The last two sentences in the list are ones the net gets wrong; watch where their sums go astray."])
    export.write_json(os.path.join(NET, "viz", "viewer-data.json"), view)
    card_path = os.path.join(NET, "card.json")
    card = json.load(open(card_path, encoding="utf-8"))
    card["latest_run"] = run_id
    export.write_json(card_path, card)
    print(run_id, "·", net.weight_count, "numbers ·", result["Test 1: templates with unseen words, accuracy"])


if __name__ == "__main__":
    main(*sys.argv[1:])
