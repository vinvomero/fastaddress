# Gold-2b insurance source list (RT-U4)

Drafted 2026-08-16, while gold-2 attempt 2 is still unspent — insurance, not a commitment.
Rule: gold-2b sources must be **disjoint from gold-2's** at the dataset level (different county
or different portal), and remain free-text-only under PROTOCOL2's sourcing rules.

## Disjointness strategy

1. **Different counties, same proven statewide sources.** The statewide aggregates that passed
   spot-checks (NC, WI, MN, MT, ME, WV, FL DOR) cover every county; gold-2 sampled specific
   counties/windows. Gold-2b samples counties disjoint from those recorded in FETCH_MANIFEST.md,
   with fresh spot-checks per PROTOCOL2.
2. **Second-choice counties in single-county states.** States where gold-2 used one county
   portal (e.g., IL/Winnebago, NV/Carson City, NE/Douglas) have untried peers (IL: DuPage, Kane;
   NV: Washoe nightly extract; NE: Lancaster). SOURCE_MAP.md's moderate/weak candidate column
   lists the leads.
3. **Unconverted candidates.** SOURCE_MAP candidates never fetched for gold-2 remain virgin
   sources for gold-2b.
4. **Hard gaps stay hard.** CA/ID/KY/WY legal gaps apply to gold-2b equally; its ceiling is the
   same 46 + DC, and the coverage floor language rules carry over unchanged.

## Pre-registration requirement

Before gold-2b is scored against anything: fetch under these rules, then append gates to
PROTOCOL2 (same gates, fresh set) — the same commit-before-score discipline as every evaluation
asset in this project.
