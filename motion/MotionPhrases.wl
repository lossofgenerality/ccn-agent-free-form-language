(* ::Package:: *)
(* MotionPhrases: reads spoken motion phrases, such as
     "move along the path while spinning counterclockwise and move upwards",
   and turns each part into a Wolfram Language RotationTransform or TranslationTransform.
   The first of the simple operations for the CCN agent free-form language.

   Load:  Get["MotionPhrases.wl"]  (from the folder it is in), or put it in your cloud
          and use Get[CloudObject["<your path>/MotionPhrases.wl"]].
   Use:   MotionReport[phrase]        how each part was read, and what was assumed
          MotionFormula[phrase]       each stage as RotationTransform . TranslationTransform (inactive)
          MotionTransform[phrase, t]  the TransformationFunction at time t (0 to 1)
          MotionPlot[phrase]          snapshots along the motion;  MotionAnimate[phrase]

   By Dara O Shayda and Hikari Noor Hoshino (星野ヌール), AI System Programmer
   © Computational Classnotes · CC BY-NC-SA 4.0 *)

BeginPackage["MotionPhrases`"];

MotionParse::usage = "MotionParse[phrase] reads a motion phrase and gives an Association: its stages, the meaning of each part, the transform formula of each stage, where the object ends, and a report.";
MotionFormula::usage = "MotionFormula[phrase] gives the transform of each stage as an inactive composition of RotationTransform and TranslationTransform in the stage time \[FormalT], from 0 to 1. Activate it to get a TransformationFunction.";
MotionTransform::usage = "MotionTransform[phrase, t] gives the TransformationFunction at time t, from 0 to 1 over the whole phrase. For a symbolic t it gives the formula of a one-stage phrase, or a list of {{from, to}, transform} for each stage.";
MotionReport::usage = "MotionReport[phrase] shows how each part of the phrase was read, what was assumed and what was not understood.";
MotionPlot::usage = "MotionPlot[phrase] draws the object at several times along its motion, with the path of its centre.";
MotionAnimate::usage = "MotionAnimate[phrase] animates the object over its motion.";
$MotionVocabulary::usage = "$MotionVocabulary holds the words MotionParse knows, by kind. Add words to its lists to extend the language.";

Begin["`Private`"];

(* ---------- The words ---------- *)

$MotionVocabulary = <|
  "translate" -> {"move", "moves", "moving", "go", "goes", "going", "travel", "travels", "travelling",
    "traveling", "slide", "slides", "sliding", "glide", "glides", "gliding", "drift", "drifts", "drifting",
    "shift", "shifts", "shifting", "head", "heads", "heading", "walk", "walks", "walking", "fly", "flies",
    "flying", "translate", "translates", "translating"},
  "rise" -> {"rise", "rises", "rising", "climb", "climbs", "climbing", "ascend", "ascends", "ascending",
    "lift", "lifts", "lifting"},
  "sink" -> {"sink", "sinks", "sinking", "fall", "falls", "falling", "drop", "drops", "dropping",
    "descend", "descends", "descending", "lower", "lowers", "lowering"},
  "spin" -> {"spin", "spins", "spinning", "rotate", "rotates", "rotating", "turn", "turns", "turning",
    "twist", "twists", "twisting", "twirl", "twirls", "twirling", "roll", "rolls", "rolling"},
  "orbit" -> {"orbit", "orbits", "orbiting", "revolve", "revolves", "revolving", "circle", "circles", "circling"},
  "follow" -> {"follow", "follows", "following"},
  "pause" -> {"pause", "pauses", "pausing", "wait", "waits", "waiting", "hold", "holds", "holding",
    "stay", "stays", "staying", "stop", "stops", "stopping"},
  "directions" -> <|
    "up" -> {0, 0, 1}, "upward" -> {0, 0, 1}, "upwards" -> {0, 0, 1},
    "down" -> {0, 0, -1}, "downward" -> {0, 0, -1}, "downwards" -> {0, 0, -1},
    "left" -> {-1, 0, 0}, "leftward" -> {-1, 0, 0}, "leftwards" -> {-1, 0, 0},
    "right" -> {1, 0, 0}, "rightward" -> {1, 0, 0}, "rightwards" -> {1, 0, 0},
    "forward" -> {0, 1, 0}, "forwards" -> {0, 1, 0}, "ahead" -> {0, 1, 0},
    "back" -> {0, -1, 0}, "backward" -> {0, -1, 0}, "backwards" -> {0, -1, 0}|>,
  "axes" -> <|"x" -> {1, 0, 0}, "y" -> {0, 1, 0}, "z" -> {0, 0, 1}, "vertical" -> {0, 0, 1}|>,
  "senses" -> <|"counterclockwise" -> 1, "clockwise" -> -1|>,
  "numbers" -> <|"a" -> 1, "an" -> 1, "one" -> 1, "two" -> 2, "three" -> 3, "four" -> 4, "five" -> 5,
    "six" -> 6, "seven" -> 7, "eight" -> 8, "nine" -> 9, "ten" -> 10, "half" -> 1/2, "quarter" -> 1/4,
    "once" -> 1, "twice" -> 2, "thrice" -> 3, "full" -> 1, "whole" -> 1, "andahalf" -> 1/2, "andaquarter" -> 1/4|>,
  "angleUnits" -> {"degree", "degrees", "radian", "radians", "turn", "turns", "revolution", "revolutions",
    "rotation", "rotations", "time", "times"},
  "distanceUnits" -> {"unit", "units", "metre", "metres", "meter", "meters", "step", "steps"},
  "places" -> {"path", "origin", "center", "point"},
  "other" -> {"the", "its", "it", "itself", "own", "s", "to", "of", "by", "with", "in", "on", "at",
    "around", "about", "along", "axis", "direction", "way", "from", "into", "onto", "toward", "towards",
    "object", "body", "keep", "keeps", "keeping", "also", "too", "same", "is", "be", "all", "each", "then"}
|>;

knownWords[] := Union[Flatten[{Lookup[$MotionVocabulary,
     {"translate", "rise", "sink", "spin", "orbit", "follow", "pause", "angleUnits", "distanceUnits", "places", "other"}],
    Keys /@ Lookup[$MotionVocabulary, {"directions", "axes", "senses", "numbers"}]}]];

(* ---------- Splitting a phrase into stages and parts ---------- *)

normalise[s_String] := StringReplace[ToLowerCase[s], {
   RegularExpression["counter[- ]?clockwise|anti[- ]?clockwise"] -> "counterclockwise",
   "\[Degree]" -> " degrees ", "°" -> " degrees ",
   RegularExpression["\\b([xyz])[- ]axis\\b"] -> "$1 axis",
   "centre" -> "center",
   RegularExpression["\\band an? half\\b"] -> " andahalf ",
   RegularExpression["\\band an? quarter\\b"] -> " andaquarter ",
   RegularExpression["\\b(?:and then|after that|followed by|afterwards|then)\\b"] -> " | ",
   RegularExpression["(?<!\\d)\\.|\\.(?!\\d)|;"] -> " | "}];

splitStages[s_String] := Select[StringTrim /@ StringSplit[normalise[s], "|"], # =!= "" &];

(* parts of one stage happen at the same time *)
splitClauses[s_String] := Select[StringTrim /@ StringSplit[s,
     RegularExpression["\\b(?:while|whilst|and|as|meanwhile|simultaneously)\\b|,"]], # =!= "" &];

words[s_String] := StringCases[s, RegularExpression["[a-z]+|\\d+(?:\\.\\d+)?"]];

numberValue[w_List] := Module[{v = $MotionVocabulary["numbers"], ws, plain},
  ws = Select[w, KeyExistsQ[v, #] || StringMatchQ[#, NumberString] &];
  If[Complement[ws, {"a", "an"}] === {}, Return[Missing["NotGiven"]]];
  plain = DeleteCases[ws, "andahalf" | "andaquarter"];
  Times @@ (If[KeyExistsQ[v, #], v[#], ToExpression[#]] & /@ plain) +
   If[MemberQ[ws, "andahalf"], 1/2, 0] + If[MemberQ[ws, "andaquarter"], 1/4, 0]];

notUnderstood[w_List] := With[{k = knownWords[]},
  DeleteDuplicates@Select[w, ! MemberQ[k, #] && ! StringMatchQ[#, NumberString] &]];

(* ---------- Reading one part ---------- *)

readClause[text_String, o_Association] := With[{w = words[text]}, If[w === {}, Nothing, readWords[text, w, o]]];

readWords[text_, w_, o_] := Module[{v = $MotionVocabulary, has, n, axisW, axisQ, axis, senseW, lr, dirW,
   kind, assumed = {}, base, sense, ang, vec, dist},
  has[key_] := IntersectingQ[w, v[key]];
  n = numberValue[w];
  axisW = Select[w, KeyExistsQ[v["axes"], #] &]; axisQ = axisW =!= {};
  axis = If[axisQ, v["axes"][First[axisW]], {0, 0, 1}];
  senseW = Select[w, KeyExistsQ[v["senses"], #] &];
  lr = Select[w, MemberQ[{"left", "right"}, #] &];
  dirW = Select[w, KeyExistsQ[v["directions"], #] &];
  kind = Which[
    has["pause"], "pause",
    MemberQ[w, "path"] || has["follow"], "path",
    has["orbit"] || (IntersectingQ[w, {"around", "about"}] && IntersectingQ[w, {"origin", "center", "point"}]), "orbit",
    has["spin"] || (senseW =!= {} && ! has["translate"]), "spin",
    has["rise"] || has["sink"] || has["translate"] || dirW =!= {} || axisQ, "translate",
    True, "unknown"];
  base = <|"Text" -> text, "Kind" -> kind|>;
  Switch[kind,
   "spin" | "orbit",
    If[! axisQ, AppendTo[assumed, "no axis: z (vertical) assumed"]];
    sense = Which[
      senseW =!= {}, v["senses"][First[senseW]],
      kind === "spin" && lr =!= {}, If[First[lr] === "left", 1, -1],
      True, AppendTo[assumed, "no direction of turning: counterclockwise assumed"]; 1];
    ang = Which[
      ! MissingQ[n], n Which[IntersectingQ[w, {"degree", "degrees"}], Pi/180,
        IntersectingQ[w, {"radian", "radians"}], 1, True, 2 Pi],
      kind === "spin" && lr =!= {}, AppendTo[assumed, "no amount: a quarter turn assumed (turn " <> First[lr] <> ")"]; Pi/2,
      True, AppendTo[assumed, "no amount: one full turn assumed"]; 2 Pi];
    base = Join[base, <|"Axis" -> axis, "Sense" -> sense, "Angle" -> ang|>];
    If[kind === "orbit", base["Centre"] = If[MemberQ[w, "origin"], {0, 0, 0}, o["Centre"]]],
   "translate",
    vec = Which[
      dirW =!= {}, Total[v["directions"] /@ dirW],
      has["rise"], {0, 0, 1}, has["sink"], {0, 0, -1}, axisQ, axis,
      True, AppendTo[assumed, "no direction: forward (+y) assumed"]; {0, 1, 0}];
    If[vec === {0, 0, 0}, AppendTo[assumed, "the directions cancel: no movement"], vec = Normalize[vec]];
    dist = If[MissingQ[n], AppendTo[assumed, "no distance: " <> ToString[o["Step"]] <> " unit assumed"]; o["Step"], n];
    base = Join[base, <|"Vector" -> vec, "Distance" -> dist|>],
   "path",
    If[! o["PathGiven"], AppendTo[assumed, "no path given: the default curve {3 t, Sin[2 Pi t], 0} is used"]],
   _, Null];
  Join[base, <|"Assumed" -> assumed, "NotUnderstood" -> notUnderstood[w]|>]];

(* ---------- From parts to transforms ---------- *)

clean[x_] := If[Precision[x] === Infinity, Simplify[x], Chop[x]];

framed[M_, vec_, o_] := If[o["Frame"] === "Object", M . vec, vec];

(* The piece of transform one part contributes, in the stage time u *)
clausePiece[a_, o_, M_ : IdentityMatrix[3], u_ : \[FormalT]] := Switch[a["Kind"],
  "translate", Inactive[TranslationTransform][framed[M, a["Distance"] a["Vector"], o] u],
  "path", Inactive[TranslationTransform][framed[M, o["Path"][u] - o["Path"][0], o]],
  "spin", Inactive[RotationTransform][a["Sense"] a["Angle"] u, a["Axis"]],
  "orbit", Inactive[RotationTransform][a["Sense"] a["Angle"] u, a["Axis"], a["Centre"]],
  _, Nothing];

(* One stage: orbits . translation to the current position . spins . the orientation so far *)
stageFormula[prims_List, P0_, M_, o_] := Module[{u = \[FormalT], off, spins, orbits, pos, pieces, f, mat},
  off = Total[Join[{{0, 0, 0}},
     Cases[prims, a_ /; MemberQ[{"translate", "path"}, a["Kind"]] :> First[clausePiece[a, o, M]]]]];
  spins = Cases[prims, a_ /; a["Kind"] === "spin" :> clausePiece[a, o]];
  orbits = Cases[prims, a_ /; a["Kind"] === "orbit" :> clausePiece[a, o]];
  pos = clean[P0 + off];
  pieces = Join[orbits,
    If[TrueQ[pos == {0, 0, 0}], {}, {Inactive[TranslationTransform][pos]}],
    spins,
    If[TrueQ[M == IdentityMatrix[3]], {}, {Inactive[AffineTransform][{M, {0, 0, 0}}]}]];
  f = Switch[Length[pieces], 0, Inactive[TranslationTransform][{0, 0, 0}], 1, First[pieces], _, Inactive[Dot] @@ pieces];
  mat = TransformationMatrix[Activate[f /. u -> 1]];
  {f, clean[mat[[1 ;; 3, 4]]], clean[mat[[1 ;; 3, 1 ;; 3]]]}];

pad3[p_List] := PadRight[p, 3];

resolvePath[Automatic] := Function[s, {3 s, Sin[2 Pi s], 0}];
resolvePath[pts_List?(MatrixQ[#, NumericQ] &)] := Module[{p = pad3 /@ pts, n},
  n = Length[p];
  If[n == 1, Function[s, Evaluate[First[p]]],
   Function[s, Evaluate[Table[Piecewise[Table[
         {p[[k, c]] + (p[[k + 1, c]] - p[[k, c]]) ((n - 1) s - (k - 1)), (k - 1)/(n - 1) <= s <= k/(n - 1)},
         {k, n - 1}]], {c, 3}]]]]];
resolvePath[f_] := Function[s, pad3[f[s]]];

Options[MotionParse] = {"Path" -> Automatic, "Centre" -> {0, 0, 0}, "Step" -> 1, "Frame" -> "World"};

MotionParse[phrase_String, opts : OptionsPattern[]] := Module[{o, stages, formulas = {}, P0 = {0, 0, 0},
   M = IdentityMatrix[3], f, res},
  o = <|"Path" -> resolvePath[OptionValue["Path"]], "PathGiven" -> OptionValue["Path"] =!= Automatic,
    "Centre" -> pad3[OptionValue["Centre"]], "Step" -> OptionValue["Step"], "Frame" -> OptionValue["Frame"]|>;
  stages = DeleteCases[Function[s, readClause[#, o] & /@ splitClauses[s]] /@ splitStages[phrase], {}];
  Do[{f, P0, M} = stageFormula[st, P0, M, o]; AppendTo[formulas, f], {st, stages}];
  If[formulas === {}, formulas = {Inactive[TranslationTransform][{0, 0, 0}]}];
  res = <|"Phrase" -> phrase, "Stages" -> stages, "Formulas" -> formulas,
    "End" -> <|"Position" -> P0, "Orientation" -> M|>, "Options" -> o|>;
  Append[res, "Report" -> report[res]]];

MotionFormula[phrase_String, opts : OptionsPattern[MotionParse]] := MotionParse[phrase, opts]["Formulas"];

transformAt[fs_List, t_] := With[{n = Length[fs]},
  Which[
   NumericQ[t], With[{k = Clip[Floor[t n] + 1, {1, n}]}, Activate[fs[[k]] /. \[FormalT] -> t n - (k - 1)]],
   n == 1, Activate[fs[[1]] /. \[FormalT] -> t],
   True, Table[{{(k - 1)/n, k/n}, Activate[fs[[k]] /. \[FormalT] -> t n - (k - 1)]}, {k, n}]]];

Options[MotionTransform] = Options[MotionParse];
MotionTransform[phrase_String, t_, opts : OptionsPattern[]] := transformAt[MotionFormula[phrase, opts], t];

(* ---------- The report ---------- *)

tstr[e_] := StringReplace[ToString[e /. \[FormalT] -> displayT, InputForm],
   {"MotionPhrases`Private`displayT" -> "t", "displayT" -> "t"}];

pieceString[Inactive[h_][args___]] := SymbolName[h] <> "[" <> StringRiffle[tstr /@ {args}, ", "] <> "]";
formulaString[Inactive[Dot][ps___]] := StringRiffle[pieceString /@ {ps}, " . "];
formulaString[p_] := pieceString[p];

senseName[s_] := If[s > 0, "counterclockwise", "clockwise"];

desc[a_, o_] := Switch[a["Kind"],
  "translate", "move " <> tstr[a["Distance"]] <> " along " <> tstr[a["Vector"]] <>
    If[o["Frame"] === "Object", " (in the object's own frame)", ""],
  "path", "follow the path, from where the object is",
  "spin", "spin about its own centre, axis " <> tstr[a["Axis"]] <> ", by " <> tstr[a["Angle"]] <> ", " <> senseName[a["Sense"]],
  "orbit", "orbit about " <> tstr[a["Centre"]] <> ", axis " <> tstr[a["Axis"]] <> ", by " <> tstr[a["Angle"]] <> ", " <> senseName[a["Sense"]],
  "pause", "stay still",
  _, ""];

clauseLine[a_, o_] := If[a["Kind"] === "unknown",
  "  ? \"" <> a["Text"] <> "\" \[RightArrow] not understood, ignored",
  "  \[Checkmark] \"" <> a["Text"] <> "\" \[RightArrow] " <> desc[a, o] <>
   If[a["Kind"] === "pause", "", ": " <> pieceString[clausePiece[a, o]]]];

report[res_] := Module[{st = res["Stages"], o = res["Options"], n, lines},
  n = Length[st];
  lines = {"Phrase: \"" <> res["Phrase"] <> "\""};
  If[n == 0, AppendTo[lines, "⚠ nothing was understood; the object stays where it is"]];
  Do[
   AppendTo[lines, "Stage " <> ToString[k] <> " of " <> ToString[n] <> If[Length[st[[k]]] > 1, ", all at the same time:", ":"]];
   Do[
    AppendTo[lines, clauseLine[a, o]];
    Scan[AppendTo[lines, "      ⚠ " <> #] &, a["Assumed"]];
    If[a["NotUnderstood"] =!= {} && a["Kind"] =!= "unknown",
     AppendTo[lines, "      • not understood, ignored: " <> StringRiffle[a["NotUnderstood"], ", "]]],
    {a, st[[k]]}];
   AppendTo[lines, "  Stage transform (t from 0 to 1): " <> formulaString[res["Formulas"][[k]]]],
   {k, n}];
  AppendTo[lines, "Ends at " <> tstr[res["End"]["Position"]] <>
    If[TrueQ[res["End"]["Orientation"] == IdentityMatrix[3]], ", facing as it started.", ", turned from how it started."]];
  StringRiffle[lines, "\n"]];

MotionReport[phrase_String, opts : OptionsPattern[MotionParse]] := MotionParse[phrase, opts]["Report"];

(* ---------- Pictures ---------- *)

$object = {EdgeForm[GrayLevel[0.35]], RGBColor[0.36, 0.6, 0.85], Cuboid[{-0.3, -0.18, -0.1}, {0.3, 0.18, 0.1}],
   RGBColor[0.85, 0.3, 0.25], Arrow[Tube[{{0, 0, 0}, {0.6, 0, 0}}, 0.03]]};

Options[MotionPlot] = Join[Options[MotionParse], {"Object" -> Automatic, "Snapshots" -> 6}];
MotionPlot[phrase_String, opts : OptionsPattern[]] := Module[{fs, obj, ts, trace},
  fs = MotionFormula[phrase, Sequence @@ FilterRules[{opts}, Options[MotionParse]]];
  obj = Replace[OptionValue["Object"], Automatic -> $object];
  ts = Subdivide[0, 1, Max[1, OptionValue["Snapshots"] - 1]];
  trace = transformAt[fs, #][{0, 0, 0}] & /@ Subdivide[0., 1., 200];
  Graphics3D[{{GrayLevel[0.55], Dashed, Line[trace]},
    MapIndexed[{Opacity[0.3 + 0.7 (First[#2] - 1)/Max[1, Length[ts] - 1]],
       GeometricTransformation[obj, transformAt[fs, N[#1]]]} &, ts]},
   Axes -> True, AxesLabel -> {"x", "y", "z"}, Boxed -> False, PlotRange -> All, ImageSize -> 420,
   PlotLabel -> Style[phrase, 11]]];

Options[MotionAnimate] = Join[Options[MotionParse], {"Object" -> Automatic}];
MotionAnimate[phrase_String, opts : OptionsPattern[]] := Module[{fs, obj, trace, pr},
  fs = MotionFormula[phrase, Sequence @@ FilterRules[{opts}, Options[MotionParse]]];
  obj = Replace[OptionValue["Object"], Automatic -> $object];
  trace = transformAt[fs, #][{0, 0, 0}] & /@ Subdivide[0., 1., 200];
  pr = {#1 - 0.8, #2 + 0.8} & @@@ (MinMax /@ Transpose[trace]);
  With[{fs0 = fs, obj0 = obj, trace0 = trace, pr0 = pr},
   Animate[Graphics3D[{{GrayLevel[0.55], Dashed, Line[trace0]}, GeometricTransformation[obj0, transformAt[fs0, time]]},
     PlotRange -> pr0, Axes -> True, AxesLabel -> {"x", "y", "z"}, Boxed -> False, ImageSize -> 420,
     SphericalRegion -> True, PlotLabel -> Style[phrase, 11]],
    {time, 0, 1}, AnimationRunning -> False, SaveDefinitions -> True]]];

End[];
EndPackage[];

(* © Computational Classnotes · CC BY-NC-SA 4.0 *)
