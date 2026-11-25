# Three.js for our 3D pages, run-time code and nets: plan

Noor Hoshino
AI System Programming Group

25 November 2026 · To decide on Friday night, 27 November 2026, with the Unity and Godot notes

---

## About three.js

1. Three.js is a JavaScript library for 3D graphics in the browser, written in JavaScript and GLSL (the shader code that runs on the graphics card). It is under the MIT licence.
2. Ricardo Cabello (mr.doob), a self-taught programmer originally from Barcelona and living in Spain, first released it on GitHub in April 2010. He has worked as a freelancer, mainly for Google's Data Arts Team.
3. No company or foundation owns it. The copyright belongs to "the three.js authors", over 2,000 contributors, and the main maintainers are funded individually through GitHub Sponsors.
4. The latest release found is r186, published on 9 September 2026. Development now centres on `WebGPURenderer`, which falls back to WebGL 2 where WebGPU is missing. Since Safari 26 (September 2025), every major browser has WebGPU.
5. TSL, the three.js shading language, lets shaders, compute shaders included, be written in JavaScript; it compiles them to WGSL (WebGPU) or GLSL (WebGL). The WebGPU renderer and TSL still change between releases, so we would pin a release.
6. A limited search found no business, funding or office ties to Israel for the founder or the project. It was a quick check, not a full one, like the one for Godot.

## The difference from Unity and Godot

7. With Unity and Godot, most of the work is getting Roslyn to compile C# while the game runs, and some platforms forbid it (Unity's IL2CPP builds; Godot's C# on the web).
8. In three.js the browser compiles JavaScript itself. Code typed as text becomes a module and is loaded at once, on every platform, phones and the web included. There is no compiler to build.
9. The diagram editor is already JavaScript, so a net drawn there can run in a three.js page directly.

## Decided (25 November 2026)

10. **Three.js for small 3D animations and interactive pages**, for example the tatreez flag ("Threads in the Wind") and the shattered glass (Cuba).
11. **The CCN design-token look.** Plots and scenes use the colours, fonts and light and dark modes of `brand/ccn-tokens.css`, as the sites do: the CCN orange as the accent, ink and soft grey for text and lines, plain white light, thin grey axes and labels in the CCN fonts. `ColorFunction`, `PlotStyle` and `Lighting` still override it, as in Wolfram.
12. **Code from strangers is deferred** until more models are developed. For now, only the owner and Noor write code. Three things keep the door open, so a sandbox can be added later without a rewrite:
    1. **one way in:** every script loads through a single entry point, where a sandbox and an allowlist can go later;
    2. **one small interface:** scripts reach the scene only through `setup(scene, target)`, `update(dt)` and our helpers, never the whole page;
    3. **nets as data:** a net loads as structure plus weights, which is safe to accept from anyone.

## The Wolfram functions to match first

13. **`Plot3D[f, {x, a, b}, {y, c, d}]`**: a surface over a rectangle.
    1. Options to mirror: `PlotPoints`, `PlotRange`, `ColorFunction`, `Mesh`, `RegionFunction`, `PlotStyle`, `Opacity`, `BoxRatios`, `Boxed`, `Axes`, `AxesLabel`.
    2. In three.js: sample the grid into one buffer; join it into triangles with normals for the lighting; colour each vertex; draw the mesh lines as line segments; build the box and axes, with text labels over the 3D view; rotate with the mouse (OrbitControls).
    3. Later: Wolfram's refinement where the surface bends (`MaxRecursion`). We start with an even grid.
14. **`ParametricPlot3D`**:
    1. one parameter, `{x(t), y(t), z(t)}`: a curve, drawn as a thick line or a tube;
    2. two parameters, `{x(u,v), y(u,v), z(u,v)}`: a surface (torus, Möbius strip, cloth, tatreez threads), the same machinery as `Plot3D` on the (u, v) square.
15. **`Manipulate[expr, {a, 0, 1}, …]`**: controls that redraw the picture.
    1. As in Wolfram, the control follows from the specification: `{a, min, max}` a slider; with a step, a stepped slider; `{a, {1, 2, 3}}` buttons or a menu; `{a, {True, False}}` a checkbox; `Locator` a point dragged on the picture.
    2. In three.js: lil-gui (shipped with three.js's examples) builds the panel. A change recomputes the points in the existing buffer instead of rebuilding the object, so dragging stays smooth on a phone.
16. **`Animate[…]`**: `Manipulate` with a play button.
    1. Options to mirror: `AnimationRate`, `AnimationDirection` (forward, backward, back and forth), `AnimationRunning`, `AnimationRepetitions`; play, pause and step.
    2. In three.js: the renderer's animation loop advances the parameter by real time, not by frames, so it plays at the same speed on every device.
17. **First piece of work:** `plot3D`, `parametricPlot3D`, `manipulate` and `animate` in one small JavaScript file, with its first test a surface checked against Wolfram's own values for the same formula.

## Run-time code, as in the Unity and Godot plans

18. **The host:** compiled scripts implement `setup(scene, target)` and `update(dt)`, the same idea as `IAnimationScript` in the Godot plan.
19. **Hot reload:** a changed script is loaded again and swapped in. Three.js does not free graphics memory by itself, so the old version's geometry and materials are disposed explicitly.
20. **Animation helpers:** `AnimationMixer`, skeleton bones (`SkinnedMesh`), morph targets, cameras, materials, and poses produced by our nets.

## Our nets in three.js

21. JavaScript becomes a fourth language of the diagram editor, beside Wolfram, Python and C#.
22. Small nets (SubjectNet and the like) run in plain JavaScript, on any phone.
23. Transformers (owNet and the TensorNets nets) run on the graphics card through TSL compute shaders. This is more work, but it would let the units' nets run live on the `monoid-algebra-nets` site.

## Testing

24. **In Claude's workspace:** three.js comes from npm, and headless Chrome runs and screenshots the pages, as it does for the net-diagram editor. WebGPU in headless Chrome may need flags; the WebGL 2 fallback always works.
25. **Against Wolfram:** the same formulas evaluated in a notebook give the reference values.
26. **On the owner's Mac:** only a final look on screen. There are no Editor locks, as there are with Unity.

## To decide on Friday

27. **How formulas are written:**
    1. as JavaScript, `(x, y) => Math.sin(x*y)`: quick to build and fast;
    2. in Wolfram form, `Sin[x y]`, read by our own small parser: the same line works in a notebook and on a page, and pages can be checked against Wolfram point by point. More work, but closer to how the owner writes. Noor leans this way; JavaScript first and the parser later is also possible.
28. **What it is for, first:** run-time scripts driving animation (as in the Unity and Godot plans), our nets running in the browser, or the Wolfram-style plotting functions for pages like the tatreez flag.
29. **Which nets first:** small nets in plain JavaScript, or the transformers through TSL.
30. **How it relates to Unity and Godot:** three.js for web and phones beside them, a quick prototype before C#, or first of the three.
31. **Where it lives:** its own repository (for example `ccn-three`) or a folder in `ccn-agent-free-form-language`.

## Worth a look before Friday

32. Google's open-source Three-Live (announced 3 November 2026, not an official Google product) runs AI-written three.js code in an on-device sandbox and turns it into glTF and USDZ for the web, Android and Apple devices. It bears on the deferred question of code from strangers.

## Sources

- three.js repository and licence: https://github.com/mrdoob/three.js
- Three.js (Wikipedia): https://en.wikipedia.org/wiki/Three.js
- Interview with Ricardo Cabello: https://www.realtimerendering.com/blog/?p=3329
- WebGPURenderer manual: https://threejs.org/manual/en/webgpurenderer
- Three.js r186 (CGWORLD, in Japanese): https://cgworld.jp/flashnews/01-202610-Threejs-r186.html
- TSL in r183: https://app.cinevva.com/news/2026-03-18-threejs-r183-render-pipeline
- Three-Live: https://opensource.googleblog.com/2026/11/

---

© Computational Classnotes · CC BY-NC-SA 4.0
