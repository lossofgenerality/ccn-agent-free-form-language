# SubjectNet, in the lab's standard layout

| Path | Holds |
|---|---|
| `net.json` | The net's structure, as drawn in the net-diagram editor (example `subjectnet`) |
| `card.json` | The summary the lab's pages are built from: purpose, structure, size, latest run, files |
| `data/` | Where the training and test data come from |
| `train/train.py` | Trains the net with our own code, records the run and exports the 3D view's data |
| `runs/<date>-<name>/` | One folder per training run, never overwritten: weights, settings, results, loss per epoch |
| `analysis/` | The notebooks and reports that look inside the net |
| `viz/` | The 3D view's data and the matrix drawing, made from the latest run |
| `writeup.md` | The write-up: aim, data, design, results, limits |

The notebooks `nets/SubjectNet.nb` and `nets/SubjectNet_as_matrices.nb`, the report `nets/SubjectNetReport.md` and the Python code in `python/ccn_nets/` stay where they were; this folder points to them. Moving them in here would remove the old copies, which waits for the owner's authorisation.

Published at https://lossofgenerality.github.io/ccn-nets/free-form/subjectnet/

---
© Computational Classnotes · CC BY-NC-SA 4.0
