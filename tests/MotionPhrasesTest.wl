(* ::Package:: *)
(* Tests for motion/MotionPhrases.wl.
   Run:  RunProcess[{"wolframscript", "-file", "<repo>/tests/MotionPhrasesTest.wl"}]
   or evaluate this file in a notebook after Get["MotionPhrases.wl"].
   © Computational Classnotes · CC BY-NC-SA 4.0 *)

If[StringQ[$InputFileName] && $InputFileName =!= "",
  Get[FileNameJoin[{DirectoryName[$InputFileName], "..", "motion", "MotionPhrases.wl"}]]];

centre[T_] := T[{0, 0, 0}];
turnOf[T_] := TransformationMatrix[T][[1 ;; 3, 1 ;; 3]];
near[a_, b_] := Max[Abs[N[Flatten[{a - b}]]]] < 10^-9;
rz[a_] := RotationMatrix[a, {0, 0, 1}];

example = "move along the path while spinning counterclockwise and move upwards";

motionTests = {
  VerificationTest[MotionParse[example]["Stages"][[All, All, "Kind"]], {{"path", "spin", "translate"}},
   TestID -> "example: three parts, at the same time"],
  VerificationTest[With[{T = MotionTransform[example, 1]}, near[centre[T], {3, 0, 1}] && near[turnOf[T], IdentityMatrix[3]]],
   True, TestID -> "example: end of the default path, one unit up, one full turn"],
  VerificationTest[With[{T = MotionTransform[example, 1/4]}, near[centre[T], {3/4, 1, 1/4}] && near[turnOf[T], rz[Pi/2]]],
   True, TestID -> "example: a quarter of the way"],
  VerificationTest[near[turnOf[MotionTransform["spin clockwise 90 degrees", 1]], rz[-Pi/2]],
   True, TestID -> "clockwise, in degrees"],
  VerificationTest[MotionParse["spin two and a half turns about the x axis"]["Stages"][[1, 1, {"Angle", "Axis"}]],
   <|"Angle" -> 5 Pi, "Axis" -> {1, 0, 0}|>, TestID -> "two and a half turns, x axis"],
  VerificationTest[near[centre[MotionTransform["rise 3", 1]], {0, 0, 3}], True, TestID -> "rise, with a distance"],
  VerificationTest[near[centre[MotionTransform["move up and left", 1]], {-1, 0, 1}], True,
   TestID -> "two moves at the same time"],
  VerificationTest[
   With[{T = MotionTransform["move up 2 units then turn left then move forward", 1]},
    near[centre[T], {0, 1, 2}] && near[turnOf[T], rz[Pi/2]]],
   True, TestID -> "three stages, world frame"],
  VerificationTest[
   near[centre[MotionTransform["move up 2 units then turn left then move forward", 1, "Frame" -> "Object"]], {-1, 0, 2}],
   True, TestID -> "three stages, the object's own frame"],
  VerificationTest[
   With[{T = MotionTransform["move right 2 then orbit counterclockwise around the origin a half turn", 1]},
    near[centre[T], {-2, 0, 0}] && near[turnOf[T], rz[Pi]]],
   True, TestID -> "orbit about the origin"],
  VerificationTest[
   {near[centre[MotionTransform["follow the path", 1/2, "Path" -> {{0, 0}, {1, 0}, {1, 1}}]], {1, 0, 0}],
    near[centre[MotionTransform["follow the path", 1, "Path" -> {{0, 0}, {1, 0}, {1, 1}}]], {1, 1, 0}]},
   {True, True}, TestID -> "a path given as points"],
  VerificationTest[
   Simplify[turnOf[MotionTransform["spin clockwise", tt]] - RotationMatrix[-2 Pi tt, {0, 0, 1}]],
   ConstantArray[0, {3, 3}], TestID -> "symbolic time"],
  VerificationTest[First[MotionFormula["spin counterclockwise"]],
   Inactive[RotationTransform][2 Pi \[FormalT], {0, 0, 1}], TestID -> "the formula is a RotationTransform"],
  VerificationTest[StringContainsQ[MotionReport["move up slowly"], "not understood, ignored: slowly"], True,
   TestID -> "the report names words it did not understand"],
  VerificationTest[near[centre[MotionTransform["dance wildly", 1]], {0, 0, 0}], True,
   TestID -> "nothing understood: the object stays"],
  VerificationTest[Head[MotionPlot[example]], Graphics3D, TestID -> "MotionPlot draws"]
};

motionReport = TestReport[motionTests];
Print["MotionPhrases tests: ", motionReport["TestsSucceededCount"], " passed, ", motionReport["TestsFailedCount"], " failed"];
Scan[Print["FAILED: ", #["TestID"], "  got ", #["ActualOutput"]] &, Values[Join[motionReport["TestsFailedWrongResults"], motionReport["TestsFailedWithMessages"], motionReport["TestsFailedWithErrors"]]]];

(* © Computational Classnotes · CC BY-NC-SA 4.0 *)
