# Streaming our nets into Blender 5: plan

Noor Hoshino
AI System Programming Group

24 November 2026 · For discussion, with the Unity and Godot notes

---

## The aim

1. Our nets, and in future other applications, are converted into Python and streamed into Blender 5.
2. They run in the Blender Editor after being compiled at run time.
3. They also run in standalone Blender applications, again compiled at run time.

## A. What is already in place

4. **Blender's Python:** Blender 5.0 uses Python 3.11, and its `bpy` packages are built for CPython 3.11. From Blender 5.1, Python is 3.13.
5. **Our nets:** the Python nets (`ccn_nets`) use only NumPy, which Blender ships with. They were written and tested on Python 3.9, so they should run unchanged. They will be tested on 3.11 and 3.13.
6. **Run-time compiling in Python:**
   1. Source code arrives as text, is compiled with Python's built-in `compile()` into a fresh module in memory, and is swapped in.
   2. No extra compiler is needed, unlike Unity and Godot.
   3. Recompiling replaces the old module, so a stream can update a net while Blender is open.

## B. Streaming into Blender

7. A Blender add-on runs a small local server, using only Python's standard library, that listens on the owner's own machine only.
8. The net-diagram editor (or a Wolfram or Python session) sends a net to it. There are two kinds of message:
   1. **Net as data:** the structure plus the trained weights. Our fixed `ccn_nets` library inside Blender builds and runs it. No code is executed, so this is the safe default.
   2. **Net as code:** the generated Python, compiled at run time. It is more flexible, but Python code can do anything on the machine, so it is accepted only from the owner's own tools, with a secret token.
9. Blender's API is not thread-safe. The server receives in the background and hands each message to Blender's main thread on a timer.

## C. Running nets in the Editor

10. A panel in Blender's sidebar shows:
    1. the nets received;
    2. their weight counts;
    3. errors with line numbers;
    4. a Run or Train button.
11. A net can be attached to an object. Each frame, the net's output drives it:
    1. bone poses, shape keys, positions or materials;
    2. or Geometry Nodes inputs.
12. Nets can also bake their output into keyframes, so the animation plays without the net.

## D. Standalone Blender applications

"Standalone" can mean several things, and each works differently:

13. **Blender run from the command line** (`blender -b scene.blend --python …`): the add-on and nets run headless, for rendering, batch work or servers.
14. **Blender as a Python module** (`bpy` from PyPI): a separate Python program imports Blender and our nets together. It needs the matching Python version.
15. **A `.blend` file carrying its own scripts:** this works, but Blender asks the user to allow scripts to run when the file opens. That is a security setting and is not bypassed.
16. **Interactive real-time apps or games:** Blender itself has had no game player since 2.8. UPBGE is the open-source fork that keeps one, and its Python can run our nets. Its current state is to be checked.

## E. Licence (to decide early)

17. Blender's Extensions Platform requires add-ons to be licensed GPL 3.0 or later, and its guidance is that everything using the `bpy` API should be GPL 3.
18. CC BY-NC-SA is not compatible with the GPL for code. Therefore:
    1. the Blender add-on part would be GPL-3.0-or-later;
    2. the owner decides whether `ccn_nets` itself stays under its own licence, kept separate from the add-on;
    3. this is not legal advice and should be checked before anything is published.

## F. Testing

19. **On the owner's Mac:**
    1. the shell runs the owner's Blender 5 headless (`Blender -b --python test.py`) for automated tests;
    2. computer use checks the panel and the animation on screen.
20. **In Claude's workspace:** the server, the messages and the nets can be tested under plain Python 3.11 and 3.13. Getting Blender itself there may not be possible, because its download site is probably outside the workspace's network access.

## G. Order of work (proposed)

21. Stage 1: nets as data inside Blender: the `ccn_nets` library loaded by an add-on, with a test net driving an object (items 5, 10, 11).
22. Stage 2: the local server and streaming from the net-diagram editor (items 7 to 9).
23. Stage 3: nets as code, compiled at run time, with the token (item 8.2).
24. Stage 4: baking to keyframes and the standalone forms chosen (items 12 to 16).

## H. To decide

25. Which "standalone" is meant: items 13, 14, 15 or 16 (or several).
26. Whether streaming code (item 8.2) is wanted, or only nets as data to begin with.
27. The licence for the add-on and for `ccn_nets` (items 17 and 18).
28. Where it lives, as with the Unity and Godot notes.

## Sources

- Blender 5.0 Python API: https://docs.blender.org/api/5.0/index.html
- Blender 5.1 Python API release notes (Python 3.13): https://developer.blender.org/docs/release_notes/5.1/python_api/
- Blender as a Python module: https://pypi.org/project/bpy/
- Extension licences: https://docs.blender.org/manual/en/dev/extensions/licenses.html

---

© Computational Classnotes · CC BY-NC-SA 4.0
