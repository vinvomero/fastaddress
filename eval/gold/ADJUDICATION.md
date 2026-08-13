# Adjudication: 72 contested addresses

Two parsers disagree on 72 of 1,500 messy addresses. They are grouped below by **disagreement shape** — 32 groups instead of 72 decisions.

**Models are blinded as A and B on purpose.** Judge which parse is *correct*, not which model you expect to win. (The A/B mapping is recorded in the repo, so the result stays auditable.)

## How to fill this out

For each group, replace the `Verdict:` value with **A**, **B**, **neither**, or **skip** (use skip when the address is genuinely ambiguous). If one address in a group deserves a different answer than the rest, add a line under it — group verdicts are defaults, not handcuffs.

Labels are usaddress component names: `AddressNumber`, `StreetName`, `StreetNamePostType` (St/Ave/Rd), `StreetNamePreDirectional` (N/S/E/W before the name), `PlaceName` (city), `StateName`, `ZipCode`, `OccupancyType`/`OccupancyIdentifier` (Apt 4B), `USPSBoxType`/`USPSBoxID` (PO Box 12), `Recipient`, `LandmarkName`, `BuildingName`.

---

## Group 1 — 31 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `51` | AddressNumber | StreetName |
| `ST` | StreetName | StreetNamePostType |
| `JAMES` | StreetName | PlaceName |
| `PLACE` | StreetNamePostType | PlaceName |
| `NEW` | PlaceName | StateName |

**Examples:**

- `51 ST JAMES PLACE NEW YORK NY 10038`
- `111 ST MARKS PLACE NEW YORK NY 10009`
- `109 ST MARKS PLACE NEW YORK NY 10009`
- `116 ST MARKS PLACE NEW YORK NY 10009`
- `96 ST MARKS PLACE NEW YORK NY 10009`
- `101 ST MARKS PLACE NEW YORK NY 10009`
- `85 ST MARKS PLACE NEW YORK NY 10009`
- `45 ST JAMES PLACE NEW YORK NY 10038`
- `93 ST MARKS PLACE NEW YORK NY 10009`
- `92 ST MARKS PLACE NEW YORK NY 10009`
- `95 ST MARKS PLACE NEW YORK NY 10009`
- `55 ST JAMES PLACE NEW YORK NY 10038`
- …and 19 more with the same shape

**Verdict:** _____   (A / B / neither / skip)

---

## Group 2 — 4 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `NEW` | StreetName | PlaceName |

**Examples:**

- `76 AVENUE B NEW YORK NY 10009`
- `127 AVENUE C NEW YORK NY 10009`
- `34 AVENUE B NEW YORK NY 10009`
- `163 AVENUE C NEW YORK NY 10009`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 3 — 3 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Trail` | StreetName | StreetNamePostType |

**Examples:**

- `1733 Tamiami Trail South, Venice, FL 34293`
- `202 West Station Stree BARRINGTON IL 60010`
- `6 West South Water Market, Chicago, IL 60608`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 4 — 2 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `LK` | PlaceName | StreetNamePostType |

**Examples:**

- `425 SHORELINE RD LK BARRNGTN IL 60010`
- `430 FDR DRIVE WEST LANE NEW YORK NY 10002`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 5 — 2 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Okemo` | BuildingName | LandmarkName |
| `Market` | BuildingName | LandmarkName |
| `Place,` | BuildingName | LandmarkName |

**Examples:**

- `Okemo Market Place, Ludlow, VT 05149`
- `Valley West Mall, West Des Moines, IA 50266`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 6 — 2 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Mile` | StreetNamePreType | AddressNumberPrefix |
| `K` | StreetName | AddressNumber |
| `Beach` | StreetName | StreetNamePreType |
| `Road` | StreetNamePostType | StreetNamePreType |
| `#` | OccupancyIdentifier | StreetName |
| `1,` | OccupancyIdentifier | StreetName |

**Examples:**

- `Mile K Beach Road # 1, Kenai, AK 99611`
- `Mi K Beach Road # 2, Kenai, AK 99611`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 7 — 2 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Municipal` | BuildingName | LandmarkName |
| `Airport,` | BuildingName | LandmarkName |

**Examples:**

- `Municipal Airport, Hutchinson, KS 67501`
- `Municipal Airport, Lincoln, NE 68524`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 8 — 2 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Lee's` | AddressNumber | StreetName |

**Examples:**

- `Lee's Mill Road, Moultonborough, NH 03254`
- `Anchor Inn Road, Round Pond, ME 04564`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 9 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `N` | StreetNamePreDirectional | StreetNamePostDirectional |
| `HOFFMAN` | StreetName | PlaceName |
| `EST` | StreetNamePostType | PlaceName |

**Examples:**

- `4450 SHOREWOOD DR N HOFFMAN EST IL 60192`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 10 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `RD` | StreetNamePostType | StreetName |
| `MT` | PlaceName | StreetNamePostType |

**Examples:**

- `212 EAST RAND RD MT PROSPECT IL 60056`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 11 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `140` | OccupancyIdentifier | StreetName |

**Examples:**

- `1251 N PLUM GROVE 140 SCHAUMBURG IL 60173`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 12 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `US` | CornerOf | StreetNamePreType |

**Examples:**

- `US Highway 22, Miles City, MT 59301`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 13 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `West` | StreetNamePreDirectional | LandmarkName |
| `Business` | StreetName | LandmarkName |
| `Center,` | StreetName | LandmarkName |

**Examples:**

- `West Business Center, Wayne, PA 19087`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 14 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Road` | StreetName | StreetNamePostType |
| `Route` | StreetNamePostType | NotAddress |
| `776,` | OccupancyIdentifier | NotAddress |

**Examples:**

- `1601 Englewood Road Route 776, Englewood, FL 34223`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 15 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Glfprt` | Recipient | LandmarkName |
| `Blx` | Recipient | LandmarkName |
| `Rgnl` | Recipient | LandmarkName |
| `Arpr,` | Recipient | LandmarkName |

**Examples:**

- `Glfprt Blx Rgnl Arpr, Gulfport, MS 39501`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 16 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `313-317` | LandmarkName | AddressNumber |
| `Broadway,` | LandmarkName | StreetName |

**Examples:**

- `313-317 Broadway, Madison, IN 47250`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 17 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Lee` | AddressNumber | LandmarkName |
| `Bird` | StreetName | LandmarkName |
| `Fld,` | StreetNamePostType | LandmarkName |

**Examples:**

- `Lee Bird Fld, North Platte, NE 69101`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 18 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `POINT` | StreetNamePostType | StreetName |
| `D` | OccupancyIdentifier | StreetNamePostType |

**Examples:**

- `2255 N CHARTER POINT D ARLNGTON HTS IL 60004`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 19 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `BARRNGTN` | StreetName | PlaceName |
| `HLS` | StreetNamePostType | PlaceName |

**Examples:**

- `350 OLD SUTTON BARRNGTN HLS IL 60010`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 20 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `US` | USPSBoxGroupType | SubaddressType |
| `6` | USPSBoxGroupID | SubaddressIdentifier |
| `Ind` | StreetNamePreType | SubaddressType |
| `15,` | StreetName | SubaddressIdentifier |

**Examples:**

- `US 6 Ind 15, Milford, IN 46542`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 21 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `North,` | PlaceName | StreetNamePostDirectional |

**Examples:**

- `15740 Aurora Avenue North, Seattle, WA 98133`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 22 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `RR` | USPSBoxGroupType | USPSBoxType |
| `422` | USPSBoxGroupID | USPSBoxID |

**Examples:**

- `RR 422 Box, Douglassville, PA 19518`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 23 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `AVE303` | StreetName | OccupancyIdentifier |

**Examples:**

- `2610 W BALMORAL AVE303 CHICAGO IL 60625`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 24 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `South` | StreetNamePreDirectional | USPSBoxGroupID |
| `Route` | StreetNamePreType | USPSBoxGroupType |
| `Box` | StreetName | USPSBoxType |
| `South` | StreetNamePostDirectional | USPSBoxID |
| `#` | OccupancyIdentifier | USPSBoxID |
| `7,` | OccupancyIdentifier | USPSBoxID |

**Examples:**

- `South Route Box South # 7, Bennington, VT 05201`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 25 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Alvy` | LandmarkName | StreetName |
| `Prk` | LandmarkName | StreetNamePostType |
| `And` | LandmarkName | IntersectionSeparator |
| `#` | StreetNamePreType | StreetName |

**Examples:**

- `Alvy Prk And Hghwy # 54, Owensboro, KY 42301`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 26 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `West` | StreetNamePreDirectional | USPSBoxGroupID |
| `Route` | StreetName | USPSBoxGroupType |
| `Box` | StreetName | USPSBoxType |
| `West` | StreetNamePostDirectional | USPSBoxID |
| `#` | OccupancyIdentifier | USPSBoxID |
| `4,` | OccupancyIdentifier | USPSBoxID |

**Examples:**

- `West Route Box West # 4, Goshen, CT 06756`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 27 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Dthn` | Recipient | LandmarkName |
| `Arprt` | Recipient | LandmarkName |
| `Trmnl,` | Recipient | LandmarkName |

**Examples:**

- `Dthn Arprt Trmnl, Midland City, AL 36350`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 28 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `313` | AddressNumber | USPSBoxGroupID |
| `RR` | StreetNamePreType | USPSBoxGroupType |
| `313` | StreetName | USPSBoxID |
| `Box,` | StreetName | USPSBoxType |

**Examples:**

- `Route 313 RR 313 Box, Arlington, VT 05250`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 29 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Avn` | StreetName | StreetNamePreType |

**Examples:**

- `1011 Avn Of Th Amrcs, New York, NY 10018`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 30 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `AND` | StreetName | StreetNamePostType |
| `DALES` | StreetName | PlaceName |

**Examples:**

- `63 HILLS AND DALES BARRINGTON IL 60010`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 31 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `BROADWAY` | Recipient | PlaceName |
| `NEW` | Recipient | StateName |

**Examples:**

- `BROADWAY NEW YORK NY 10013`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 32 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `R` | OccupancyIdentifier | PlaceName |

**Examples:**

- `810 BARRINGTON POINT R BARRINGTON IL 60010`

**Verdict:** _____   (A / B / neither / skip)

---

## When you're done

Tell the agent it's filled in. It will read the verdicts, un-blind them, and score the gold gate — which decides whether the retrained model ships or stays shelved.

Disclosed limitation: judging only contested cases measures *relative* accuracy on the cases where the parsers differ, not absolute accuracy across all 1,500. It informs the decision; it does not replace the full-set gate in the protocol.