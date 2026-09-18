# Protocol edits to apply manually

Four changes. Each gives you the exact text to paste. Where text is *replaced*, the
"Find" line is a unique phrase you can search for in Word (Ctrl+F).

A note on placement: I've deliberately put the new table in a **new Appendix B**
rather than inline as Table 6. Inline placement would be methodologically neater but
would force you to renumber Tables 6–9 and every cross-reference to them by hand.
Appendix B and Table 10 avoid all renumbering. If bash access is restored I can do
the inline version properly instead.

---

## EDIT 1 — Add "classical antecedent" to the dual-extraction set

**Section:** Data Extraction
**Find:** `The two exceptions, oracle limitations and regression-testing relevance`
**Replace that whole sentence with:**

> Three items, oracle limitations, regression-testing relevance, and the classical
> antecedent, call for judgement rather than transcription, and are therefore
> extracted independently by both reviewers for every study, with disagreements
> resolved by discussion and, failing that, by the third author. The classical
> antecedent is placed in this group deliberately: attributing a quantum technique
> to its classical ancestor is an inference rather than a fact stated on the page,
> and the credibility of the negative finding reported under RQ5 depends on those
> attributions being made consistently by more than one reader.

---

## EDIT 2 — Pre-declare the classical technique frame (the important one)

### 2a. Add this paragraph at the END of the "Scope boundary: classical compiler testing" paragraph

> Because RQ5 reports not only which classical techniques were carried over but which
> were not, the set of candidate techniques must be fixed before the search rather
> than assembled from whatever the included studies happen to mention. A frame drawn
> up after the data are seen cannot support a claim of absence, since any technique
> that failed to appear could simply have been left out of the frame. Table 10, in
> Appendix B, therefore pre-declares eight classical technique families, each
> identified by its canonical origin in the classical compiler-testing and regression-
> testing literature and cross-checked against the scope of the compiler-testing survey
> of Chen et al. [23]. Every included study is mapped to one or more of these families
> at extraction, and any family with no quantum descendant among the included studies
> is reported as an empty row. Fixing the frame in advance is what converts that empty
> row from an observation into a pre-registered prediction that the review can be held
> to. Bug benchmarks and fault databases are deliberately not part of the frame: they
> are evaluation infrastructure rather than testing techniques, and they are already
> captured under RQ4.

### 2b. Add a new Appendix B at the very end of the document (after Appendix A)

**Heading:** `Appendix B. Pre-Declared Classical Technique Frame for RQ5`

**Intro line:**

> Table 10 fixes the candidate set of classical technique families against which RQ5
> judges transfer and non-transfer. The frame is assembled from the canonical origin
> of each family and was fixed before the formal search was run.

**Caption:** `Table 10: Pre-declared classical technique families (RQ5 reference frame)`

**Table (3 columns):**

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

### 2c. Add these six references to the reference list, after [23]

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
      Haskell programs," in Proc. ACM SIGPLAN Int. Conf. Functional Programming (ICFP),
      2000, pp. 268-279.

[28]  A. Pnueli, M. Siegel, and E. Singerman, "Translation validation," in Proc. Int.
      Conf. Tools and Algorithms for the Construction and Analysis of Systems (TACAS),
      1998, pp. 151-166.

[29]  X. Leroy, "Formal verification of a realistic compiler," Communications of the ACM,
      vol. 52, no. 7, pp. 107-115, 2009.
```

All six were verified against their sources (venue, year, and page range).

---

## EDIT 3 — Add the RQ5 negative-claim threat

**Section:** Threats to Validity
**Find:** `Classifying techniques and oracle limitations again calls for judgement`
**Insert this sentence immediately BEFORE that sentence:**

> The negative half of RQ5 carries a threat of its own, and it is the sharpest one in
> this protocol. A report that some classical technique has no quantum descendant is
> bounded by what the search retrieves: a single unretrieved study adapting regression
> test selection to a quantum compiler would falsify it. Three measures are taken
> against this. The frame of Table 10 is fixed in advance, so the claim is made only
> about a closed and stated set of families rather than about the literature at large.
> Backward and forward snowballing is applied to every included study, which reaches
> work the concept terms miss. And before any family is reported as having no quantum
> descendant, a targeted verification search is run for that family specifically,
> pairing its canonical vocabulary with the quantum-compiler terms, with the query and
> its yield recorded in the OSF record. Even so, the finding is stated as absence of
> evidence within a defined and reproducible frame, not as evidence of absence.

---

## EDIT 4 — Update three rows of Table 9 (PRISMA-P mapping)

**Row 11c** — append to the existing cell text:

> The classical antecedent is extracted independently in duplicate along with the two
> other interpretive items.

**Row 12** — append to the existing cell text:

> The candidate set of classical technique families for the antecedent item is
> pre-declared in Table 10 (Appendix B).

**Row 16 (Meta-bias)** — append to the existing cell text:

> The risk that RQ5 reports a non-transfer that a missed study would contradict is
> addressed by the pre-declared frame of Table 10, by snowballing, and by a targeted
> per-family verification search recorded in OSF.

---

## After applying

Two things worth checking once the edits are in:

1. **Figure 1.** The text promises that the PRISMA diagram records the main
   title-and-abstract exclusion reasons. I was not able to open the embedded image to
   confirm it actually does. Please check, and if the exclusion-reason boxes are
   missing, either add them or soften the sentence in the Study Selection section.

2. **Bold lead-ins.** When Word merges an edited paragraph it sometimes carries the
   bold from a bold lead-in ("Data Availability.", "Outcomes and data-item
   prioritization.") across the whole paragraph. After pasting, confirm only the
   lead-in phrase is bold in any paragraph you touched.
