# Adjudication: 72 contested addresses

Two parsers disagree on 49 of 1,500 messy addresses. They are grouped below by **disagreement shape** — 16 groups instead of 49 decisions.

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

## Group 2 — 3 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Square,` | StreetName | StreetNamePostType |

**Examples:**

- `1 The Square, Lillington, NC 27546`
- `807 South Central Expressway, Richardson, TX 75080`
- `6 West South Water Market, Chicago, IL 60608`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 3 — 2 addresses

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `140` | OccupancyIdentifier | StreetName |

**Examples:**

- `1251 N PLUM GROVE 140 SCHAUMBURG IL 60173`
- `5051 PELICAN COLONY901 BONITA SPRGS FL 34134`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 4 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `LK` | PlaceName | StreetNamePostType |

**Examples:**

- `425 SHORELINE RD LK BARRNGTN IL 60010`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 5 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `US` | StreetNamePreType | SubaddressType |
| `6` | StreetName | SubaddressIdentifier |
| `Ind` | StreetName | SubaddressType |
| `15,` | StreetName | SubaddressIdentifier |

**Examples:**

- `US 6 Ind 15, Milford, IN 46542`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 6 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Mile` | LandmarkName | AddressNumberPrefix |
| `K` | LandmarkName | AddressNumber |
| `Beach` | StreetName | StreetNamePreType |
| `Road` | StreetNamePostType | StreetNamePreType |
| `#` | OccupancyIdentifier | StreetName |
| `1,` | OccupancyIdentifier | StreetName |

**Examples:**

- `Mile K Beach Road # 1, Kenai, AK 99611`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 7 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `Mi` | StreetNamePreType | AddressNumberPrefix |
| `K` | StreetName | AddressNumber |
| `Beach` | StreetName | StreetNamePreType |
| `Road` | StreetNamePostType | StreetNamePreType |
| `#` | OccupancyIdentifier | StreetName |
| `2,` | OccupancyIdentifier | StreetName |

**Examples:**

- `Mi K Beach Road # 2, Kenai, AK 99611`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 8 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `E` | StreetNamePreDirectional | StreetNamePostDirectional |
| `NORTH` | StreetName | SubaddressIdentifier |
| `WATER` | OccupancyType | SubaddressType |
| `2500` | OccupancyIdentifier | SubaddressIdentifier |

**Examples:**

- `340 E NORTH WATER 2500 CHICAGO IL 60611`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 9 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `D.C.` | PlaceName | StateName |

**Examples:**

- `99 s spruce road apt. #4b, D.C. 20500`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 10 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `RR` | StreetNamePreType | USPSBoxType |
| `422` | StreetName | USPSBoxID |
| `Box,` | StreetName | USPSBoxType |

**Examples:**

- `RR 422 Box, Douglassville, PA 19518`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 11 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `ORL` | PlaceName | OccupancyIdentifier |
| `FL` | StateName | OccupancyType |

**Examples:**

- `300 orange ave, fl 7, ORL FL`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 12 — 1 address

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

## Group 13 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `1/2` | AddressNumberSuffix | StreetName |

**Examples:**

- `33 1/2 AVE`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 14 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `AND` | StreetName | StreetNamePostType |
| `DALES` | StreetName | PlaceName |

**Examples:**

- `63 HILLS AND DALES BARRINGTON IL 60010`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 15 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `BROADWAY` | Recipient | PlaceName |
| `NEW` | Recipient | StateName |

**Examples:**

- `BROADWAY NEW YORK NY 10013`

**Verdict:** _____   (A / B / neither / skip)

---

## Group 16 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `ST` | StreetName | StreetNamePostType |
| `UNT` | StreetName | PlaceName |
| `D` | StreetNamePostType | PlaceName |

**Examples:**

- `210 CRYSTAL ST UNT D CARY IL 60013`

**Verdict:** _____   (A / B / neither / skip)

---

## When you're done

Tell the agent it's filled in. It will read the verdicts, un-blind them, and score the gold gate — which decides whether the retrained model ships or stays shelved.

Disclosed limitation: judging only contested cases measures *relative* accuracy on the cases where the parsers differ, not absolute accuracy across all 1,500. It informs the decision; it does not replace the full-set gate in the protocol.