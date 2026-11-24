# Training SubjectNet

From the repository root, with `ccn-net-lab` checked out beside this repository (or its path in `CCN_NET_LAB`):

    python3 nets/subjectnet/train/train.py seed1234

The settings are at the top of `train.py`. The run is recorded in `runs/<date>-seed1234/`, the 3D view's data in `viz/viewer-data.json`, and `card.json` is pointed at the run. The Wolfram training (our own code and `NetTrain`) is in `nets/SubjectNet.nb`; both give the same weights from the same start (see `python/tests/`).

---
© Computational Classnotes · CC BY-NC-SA 4.0
