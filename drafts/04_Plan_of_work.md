# Agent script — 4. A plan of work

*Interim draft for comment, 21 November 2026.*

1. **Write today's assistant as scripts.** The CCN base script and the "Eye-witness assistant" script, written out from the current kernel rules. Nothing changes in behaviour; it's a check that the language can say what we already do.
2. **The compiler, in Wolfram.** Reads a script, gives the policy, the guidance and the compile report. Tested on the two scripts from step 1 and on Tutu Cat's.
3. **The kernel uses the compiled policy** instead of the hard-wired rules, with the layers merged. The same tests as today must pass, plus tests for each enforced line.
4. **Admin: the script editor** for customers and pages (in place of the Keywords box), with the compile report and the "Try it" box.
5. **Tutu Cat on the same kernel**, with its own script. Then the other agents, one at a time.
6. **Documents:** the language reference (key words, layers, what's enforced) in Production Notes, for Wayne, Dara and customers.
7. **The ledger and `uses Claude:`.** Every Claude call records when, where and why (file 6). It goes into the kernel with step 3, so no call is ever made unrecorded.
8. **Code steps and the Python target.** The Python reader and compiler, with golden files checked by both readers; then the Python host, which calls Claude only through the kernel (file 7).
9. **The first own net: the topic gate**, trained in both Wolfram and Python from one description. First check that a net trained in PyTorch imports and runs in Wolfram. It is used live only after its scores are in a compile report and you approve it (file 8).

Steps 1 and 2 need only your comments on these drafts. Step 3 changes the live assistant, so it waits for your go-ahead and a test round. Steps 7 to 9 follow step 3, and step 9 also waits for question 9.

© Computational Classnotes · CC BY-NC-SA 4.0
