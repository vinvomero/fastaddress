# Contested-record adjudication result

Adjudicator: **ChatGPT (LLM), submitted by Vin** (LLM — triage evidence, does NOT satisfy the protocol gate)

Contested records: 72 of 1,500 gold candidates (the rest were labeled identically by both models).

| Outcome | Records | Share of contested |
|---|---|---|
| v1 (shipped model) judged correct | 28 | 38.9% |
| v2 (retrained candidate) judged correct | 39 | 54.2% |
| neither correct | 4 | 5.6% |
| skipped (ambiguous) | 1 | 1.4% |

Head-to-head on the 67 decided records: **v2 58% / v1 42%**.

## Limits

- Contested-only: this is relative accuracy where the parsers differ, not absolute accuracy across the gold set. Both models were identical on 1428 of 1,500 records.
- The adjudicator was an LLM. `eval/PROTOCOL.md` requires human adjudication for the gold gate, and the prelabels were themselves machine-generated, so this is corroborating triage evidence — not gate-satisfying data.

## Per-record verdicts

| Address | Verdict (blind) | Model |
|---|---|---|
| `51 ST JAMES PLACE NEW YORK NY 10038` | A | v2 |
| `111 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `109 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `116 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `96 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `101 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `85 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `45 ST JAMES PLACE NEW YORK NY 10038` | A | v2 |
| `93 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `92 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `95 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `55 ST JAMES PLACE NEW YORK NY 10038` | A | v2 |
| `107 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `47 ST JAMES PLACE NEW YORK NY 10038` | A | v2 |
| `103 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `98 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `122 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `87 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `115 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `128 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `104 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `59 ST JAMES PLACE NEW YORK NY 10038` | A | v2 |
| `94 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `100 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `113 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `102 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `118 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `119 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `114 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `121 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `126 ST MARKS PLACE NEW YORK NY 10009` | A | v2 |
| `76 AVENUE B NEW YORK NY 10009` | B | v1 |
| `127 AVENUE C NEW YORK NY 10009` | B | v1 |
| `34 AVENUE B NEW YORK NY 10009` | B | v1 |
| `163 AVENUE C NEW YORK NY 10009` | B | v1 |
| `1733 Tamiami Trail South, Venice, FL 34293` | B | v1 |
| `202 West Station Stree BARRINGTON IL 60010` | B | v1 |
| `6 West South Water Market, Chicago, IL 60608` | A | v2 |
| `425 SHORELINE RD LK BARRNGTN IL 60010` | A | v2 |
| `430 FDR DRIVE WEST LANE NEW YORK NY 10002` | B | v1 |
| `Okemo Market Place, Ludlow, VT 05149` | B | v1 |
| `Valley West Mall, West Des Moines, IA 50266` | B | v1 |
| `Mile K Beach Road # 1, Kenai, AK 99611` | A | v2 |
| `Mi K Beach Road # 2, Kenai, AK 99611` | A | v2 |
| `Municipal Airport, Hutchinson, KS 67501` | B | v1 |
| `Municipal Airport, Lincoln, NE 68524` | B | v1 |
| `Lee's Mill Road, Moultonborough, NH 03254` | B | v1 |
| `Anchor Inn Road, Round Pond, ME 04564` | B | v1 |
| `4450 SHOREWOOD DR N HOFFMAN EST IL 60192` | B | v1 |
| `212 EAST RAND RD MT PROSPECT IL 60056` | A | v2 |
| `1251 N PLUM GROVE 140 SCHAUMBURG IL 60173` | A | v2 |
| `US Highway 22, Miles City, MT 59301` | B | v1 |
| `West Business Center, Wayne, PA 19087` | B | v1 |
| `1601 Englewood Road Route 776, Englewood, FL 34223` | B | v1 |
| `Glfprt Blx Rgnl Arpr, Gulfport, MS 39501` | B | v1 |
| `313-317 Broadway, Madison, IN 47250` | B | v1 |
| `Lee Bird Fld, North Platte, NE 69101` | B | v1 |
| `2255 N CHARTER POINT D ARLNGTON HTS IL 60004` | B | v1 |
| `350 OLD SUTTON BARRNGTN HLS IL 60010` | B | v1 |
| `US 6 Ind 15, Milford, IN 46542` | neither | neither |
| `15740 Aurora Avenue North, Seattle, WA 98133` | B | v1 |
| `RR 422 Box, Douglassville, PA 19518` | A | v2 |
| `2610 W BALMORAL AVE303 CHICAGO IL 60625` | neither | neither |
| `South Route Box South # 7, Bennington, VT 05201` | B | v1 |
| `Alvy Prk And Hghwy # 54, Owensboro, KY 42301` | B | v1 |
| `West Route Box West # 4, Goshen, CT 06756` | B | v1 |
| `Dthn Arprt Trmnl, Midland City, AL 36350` | B | v1 |
| `Route 313 RR 313 Box, Arlington, VT 05250` | skip | skip |
| `1011 Avn Of Th Amrcs, New York, NY 10018` | B | v1 |
| `63 HILLS AND DALES BARRINGTON IL 60010` | A | v2 |
| `BROADWAY NEW YORK NY 10013` | neither | neither |
| `810 BARRINGTON POINT R BARRINGTON IL 60010` | neither | neither |
## The headline is misleading — read the split

The 58/42 aggregate is carried entirely by one pattern class.

| Slice | v1 correct | v2 correct |
|---|---|---|
| Saint-name class (`N ST NAME PLACE …`, 31 records) | 0 | **31** |
| Everything else (36 decided records) | **28 (78%)** | 8 (22%) |
| All contested (67 decided) | 28 (42%) | 39 (58%) |

v2 wins the saint-name class outright — the same class that makes `usaddress.tag()` raise
`RepeatedLabelError` and accounts for 26 open upstream issues. Outside it, the shipped model is
judged correct nearly four times as often. Retraining bought one specific, valuable capability and
cost general accuracy elsewhere.

**Consequence for the ship decision:** replacing v1 with v2 wholesale would trade a broad
regression for a narrow win — the wrong trade for a library whose entire credibility rests on
matching the incumbent. The defensible options are (a) keep v1 as the only model and treat the
saint-name class as a documented limitation, or (b) ship v2 strictly as an opt-in alternate model
with this split published, so users choose with full information. Both keep the parity promise
intact; neither is a "v2 is more accurate" claim, which this evidence does not support.
