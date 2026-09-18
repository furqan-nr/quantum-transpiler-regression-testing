# Protocol edits to apply manually

Four changes to `SLR_Protocol_Quantum_Compiler_Testing.docx`.
Designed so that **no existing table needs renumbering** — the new table is added
as Appendix B / Table 10, after the PRISMA-P table.

---

## EDIT 1 — Data Extraction: add the classical antecedent to dual extraction

**Section:** Data Extraction (the paragraph beginning "For every included study, the form in Table 8 captures...")

**FIND this sentence:**

> The two exceptions, oracle limitations and regression-testing relevance, do call for judgement and are therefore extracted independently by both reviewers for every study, with disagreements resolved by discussion and, failing that, by the third author.

**REPLACE with:**

> The three exceptions, oracle limitations, regression-testing relevance, and the classical antecedent, do call for judgement and are therefore extracted independently by both reviewers for every study, with disagreements resolved by discussion and, failing that, by the third author. The classical antecedent is included among these deliberately: attributing a quantum technique to its classical origin is an inferential act rather than a transcription, straightforward where a paper names its ancestry but a matter of judgement where the debt is implicit, and because RQ5 rests on those attributions they are made twice and independently rather than once.

---

## EDIT 2 — Research Questions: point the scope boundary at the fixed frame

**Section:** the "Scope boundary: classical compiler testing." paragraph.

**FIND the final sentence:**

> This keeps the review's scope intact while making the transfer itself visible, and it lets RQ5 report not only which classical techniques crossed over but which did not, a negative result that a review confined to quantum papers alone could assert but never evidence.

**REPLACE with:**

> This keeps the review's scope intact while making the transfer itself visible, and it lets RQ5 report not only which classical techniques crossed over but which did not. That second half of the question only means something against a fixed list, since a technique can only be shown to be absent from a set that was decided in advance. Table 10 therefore pre-declares eight classical technique families, each with its canonical origin, and RQ5's absence claims are made against that frame and no other. Fixing the frame before the search is what turns "no quantum descendant" into a falsifiable prediction rather than an observation assembled after the data are in.

---

## EDIT 3 — Threats to Validity: bound the negative claim

**Section:** Threats to Validity. Add as a new sentence **immediately before** the final sentence
(the one beginning "Finally, because this is a qualitative mapping of techniques...").

**INSERT:**

> RQ5 carries a threat of its own, and it is specific to negative findings: reporting that a classical technique family has no quantum descendant is a claim about the absence of evidence, which is only as strong as the search that looked for it. A single missed paper would falsify it. Three things guard against that. The frame of Table 10 is fixed in advance, so the claim is bounded and cannot drift. Backward and forward snowballing covers work that the concept vocabulary does not reach. And for every family that finishes the review with no quantum descendant, a final targeted verification search is run using that family's own terminology and the names of its canonical tools, so absence is tested directly rather than inferred from the main search having returned nothing.

---

## EDIT 4 — New Appendix B and Table 10

Add at the very end of the document, after the existing Appendix A (PRISMA-P table).

**Heading:**

> Appendix B. Pre-Declared Classical Technique Frame

**Intro paragraph:**

> RQ5 asks which classical compiler-testing techniques have been carried into the quantum setting and which have not. The second half of that question requires a fixed candidate set, declared before the search, so that an empty row is a result rather than an artefact of what happened to be recalled. Table 10 gives that set: eight families, each with the canonical publication that introduced it. The frame was assembled from those canonical origins and cross-checked against the scope of Chen et al.'s survey of compiler testing [23]; it is not a reproduction of that survey's internal taxonomy. Bug benchmarks and datasets are deliberately not included, as those are evaluation infrastructure rather than testing techniques and are already covered by RQ4. Each included study is mapped to one or more of C1 to C8 at extraction; families with no mapped study at the end of the review are reported as the empty rows of the lineage synthesis, subject to the targeted verification search described under Threats to Validity.

**Caption:** Table 10: Pre-Declared Classical Technique Frame for RQ5

| ID | Classical technique family | Canonical origin |
|----|---------------------------|------------------|
| C1 | Randomised and grammar-based program generation | Yang et al. [24] |
| C2 | Differential testing | McKeeman [25] |
| C3 | Metamorphic testing | Chen, Cheung & Yiu [26] |
| C4 | Equivalence modulo inputs | Le, Afshari & Su [22] |
| C5 | Property-based testing | Claessen & Hughes [27] |
| C6 | Translation validation | Pnueli, Siegel & Singerman [28] |
| C7 | Proof-based compiler verification | Leroy [29] |
| C8 | Regression test selection and prioritisation | Yoo & Harman [9] |

---

## EDIT 5 — Six new references

Append after existing reference [23]:

```
[24]  X. Yang, Y. Chen, E. Eide, and J. Regehr, "Finding and understanding bugs in C
      compilers," in Proc. ACM SIGPLAN Conf. Programming Language Design and
      Implementation (PLDI), 2011, pp. 283-294.

[25]  W. M. McKeeman, "Differential testing for software," Digital Technical Journal,
      vol. 10, no. 1, pp. 100-107, 1998.

[26]  T. Y. Chen, S. C. Cheung, and S. M. Yiu, "Metamorphic testing: a new approach for
      generating next test cases," Dept. of Computer Science, Hong Kong University of
      Science and Technology, Tech. Rep. HKUST-CS98-01, 1998.

[27]  K. Claessen and J. Hughes, "QuickCheck: a lightweight tool for random testing of
      Haskell programs," in Proc. 5th ACM SIGPLAN Int. Conf. Functional Programming
      (ICFP), 2000, pp. 268-279.

[28]  A. Pnueli, M. Siegel, and E. Singerman, "Translation validation," in Proc. Int.
      Conf. Tools and Algorithms for the Construction and Analysis of Systems (TACAS),
      1998, pp. 151-166.

[29]  X. Leroy, "Formal verification of a realistic compiler," Communications of the ACM,
      vol. 52, no. 7, pp. 107-115, 2009.
```

All six were verified against their sources (venue, year, and page ranges) before being listed.

---

## EDIT 6 — Two PRISMA-P rows in Table 9

**Row 11c** — append to the existing cell text:

> The classical antecedent is extracted independently in duplicate along with the other two interpretive items.

**Row 12** — append to the existing cell text:

> The candidate set of classical techniques against which the antecedent is recorded is pre-declared in Table 10.

---

## Still outstanding (not covered here)

- The Table 5 queries have not been run. The header correctly says "Query as specified";
  it can become "as issued" once you execute them and record per-database yields.
- Scoping counts are arXiv-only (116 for the full string, 2015-2026; zero before 2015;
  one record for compiler + "regression testing", which is CertiQ).
- The adjudicator is a co-author. Disclosed in Threats rather than solved.
- Figure 1 was never checked against the text's promise that it records the
  title-and-abstract exclusion reasons. Worth an eye before submission.
