# SubjectNet's data

- **Made, not collected.** The training and test sentences are written from 19 templates, each carrying its own label (object or other). No conversational-construct labels anything, and no outside data is used.
- **Python:** `make_data` in `python/ccn_nets/subjectnet.py` (2000 training parts with seed 11, 600 test parts with seed 22). **Wolfram:** the same templates in `nets/SubjectNet.nb`.
- **Unseen words for testing:** the test nouns, names, relations and abstract words never appear in training.
- **Fixed tests:** the paragraphs and hard sentences are in `python/ccn_nets/data/subjectnet_tests.json`.

---
© Computational Classnotes · CC BY-NC-SA 4.0
