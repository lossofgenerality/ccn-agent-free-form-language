# A run-time C# compiler add-on for Godot: plan

Noor Hoshino
AI System Programming Laboratory

24 November 2026 · To discuss on Friday night, 27 November 2026, with the Unity note

---

## About Godot

1. Godot 4 is a free, open-source game engine under the MIT licence. C# needs the .NET edition of the editor, downloaded from the Godot website.
2. C# projects run on Windows, macOS and Linux, with experimental Android and iOS support. C# projects cannot be exported to the web.
3. Its editor runs natively on Windows, macOS and Linux.
4. On desktop, Godot runs C# on Microsoft's .NET runtime, which compiles just in time, so Roslyn can compile code while the game runs.
5. Founders: Juan Linietsky and Ariel Manzur (Buenos Aires). The source was released on GitHub under the MIT licence in 2014.
6. The Godot Foundation, a Dutch non-profit (Stichting Godot), manages donations. The copyright to the source is held collectively by every contributor, so no company or investor owns the engine.
7. W4 Games (Dublin) is a separate for-profit company founded by core Godot developers. It sells console exports, cloud services and paid support. Its investors include OSS Capital, Lux Capital, Bob Young, Sisu Game Ventures, Tencent, Naval Ravikant and Tobias Lütke's family office. It matters to us only if we use its paid services.
8. A limited search found no public business, funding or office ties to Israel for the founders, the Foundation or W4 Games (see the limits listed in the conversation of 24 November 2026).

## The plan

### A. The compiler

9. Use the official Roslyn package, `Microsoft.CodeAnalysis.CSharp`, added to the Godot project's `.csproj` like any other NuGet package. No hand-copied DLLs or special builds are needed, as they are in Unity.
10. The add-on lives in `addons/ccn_runtime_compiler/`, so it can be dropped into any Godot project.

### B. Our own compile service

11. It compiles source text in memory with `CSharpCompilation`.
12. It finds references by itself: the .NET runtime's assemblies, Godot's C# API (`GodotSharp.dll`) and the game's own assembly.
13. It loads each result into a separate, collectible `AssemblyLoadContext`, so old code can be unloaded on reload instead of piling up in memory. Unity's Mono cannot do this; .NET can.
14. It returns errors with line and column numbers, ready to show.

### C. A security check

15. Before compiling, a check with Roslyn's semantic model refuses types and namespaces that are not allowed (for example `System.IO`, `System.Net`, `System.Reflection`, process and thread control). It checks what the code actually calls, not just the names it writes.
16. The allowlist is a settings file that the owner controls.

### D. How compiled code meets Godot

17. Compiled classes are plain C# that implement our own interface, for example `IAnimationScript` with `Setup(Node3D target)` and `Process(double delta)`.
18. A fixed host node, `RuntimeScriptHost`, is built into the game. It holds a compiled script and calls it every frame.
19. Compiled classes do not subclass Godot's own types (`Node`), because Godot has to register those when the project is built. This can be a later stage if needed.

### E. Animation helpers

20. A small API lets compiled code drive:
    1. `AnimationPlayer` and `AnimationTree`;
    2. `Skeleton3D` bone poses;
    3. `Tween`s, cameras and materials;
    4. our nets' outputs, for example a net that produces poses.

### F. Tools

21. **Editor plugin:** a dock in the Godot Editor with a code editor, a Compile button, an error list, and a live preview on the selected node.
22. **In-game console:** an overlay where C# is typed, compiled and attached while the game runs.
23. **Hot reload:** a watched scripts folder. When a file changes, it is recompiled, the old version is unloaded and the new one is swapped in.

### G. Link to our nets

24. The C# net library (our own dense layers, softmax, backpropagation and so on) is built into the project.
25. On desktop, the C# code that the net-diagram editor generates for a net is compiled while the game runs.
26. On iOS, nets load as data: structure plus weights.

### H. Platforms

27. **Windows, macOS and Linux** (Editor and exported games): full run-time compiling.
28. **Android:** probably works, because .NET on Android compiles just in time. To be verified.
29. **iOS:** no run-time compiling, because it is compiled ahead of time. Nets load as data.
30. **Web:** Godot 4 cannot export C# projects to the web.

### I. Testing

31. **In Claude's workspace:** the compile service, the security check and the reload are plain .NET, so they can be tested under .NET 10 there, using the Roslyn that comes with the SDK.
32. **Godot itself:** the Linux .NET build of Godot can probably be fetched from GitHub and run headless there for tests. To be checked.
33. **On the owner's Mac:**
    1. the shell writes files and runs Godot headless;
    2. computer use checks the Editor dock and the animations on screen;
    3. unlike Unity, Godot does not lock the project while the Editor has it open, so command-line tests can run alongside the Editor.

### J. Order of work

34. Stage 1: the compile service and the security check (items 11 to 16), with tests.
35. Stage 2: the host node and the animation helpers (items 17 to 20), with a demo scene.
36. Stage 3: the editor plugin, the in-game console and hot reload (items 21 to 23).
37. Stage 4: the link to our nets (items 24 to 26).

## To decide on Friday

38. Where it lives: its own repository (for example `ccn-godot-runtime-compiler`) or a folder in an existing one.
39. Whether Unity, Godot or both come first.

## Sources

- Godot C# platform support: https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/index.html
- Godot governance: https://godotengine.org/governance/
- Godot team and founders: https://godotengine.org/contact/
- W4 Games Series B: https://w4games.com/blog/w4-games-news-1/w4-games-raises-18-million-to-accelerate-international-presence-193
- Roslyn: https://github.com/dotnet/roslyn

---

© Computational Classnotes · CC BY-NC-SA 4.0
