# Adjudication round 2 — 8 addresses need your call

The parsers now disagree on 49 of 1,500 messy addresses (16 distinct shapes). **8 shapes carry your verdicts forward from last time and need no action** — they are listed at the bottom for reference only. That leaves **8 groups covering 8 addresses** to judge.

**Models are blinded as A and B on purpose.** Judge which parse is *correct*, not which model you expect to win. (The A/B mapping is recorded in the repo, so the result stays auditable.)

**Census evidence is attached where it exists.** The US Census geocoder (public domain, so it can be published with the eval set) says what the real address looks like — house number, street name, street type, city. Treat it as *evidence*, not as the answer: it reports a canonical address, not usaddress's token labels, and its component names do not carry every distinction in the schema. Where it says *no match*, it abstained — which is common on exactly the messy inputs that are hardest to judge.

## How to fill this out

For each group, replace the `Verdict:` value with **A**, **B**, **neither**, or **skip** (use skip when the address is genuinely ambiguous). If one address in a group deserves a different answer than the rest, add a line under it — group verdicts are defaults, not handcuffs.

Labels are usaddress component names: `AddressNumber`, `StreetName`, `StreetNamePostType` (St/Ave/Rd), `StreetNamePreDirectional` (N/S/E/W before the name), `PlaceName` (city), `StateName`, `ZipCode`, `OccupancyType`/`OccupancyIdentifier` (Apt 4B), `USPSBoxType`/`USPSBoxID` (PO Box 12), `Recipient`, `LandmarkName`, `BuildingName`.

---

## Group 1 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `US` | StreetNamePreType | SubaddressType |
| `6` | StreetName | SubaddressIdentifier |
| `Ind` | StreetName | SubaddressType |
| `15,` | StreetName | SubaddressIdentifier |

**Examples:**

- `US 6 Ind 15, Milford, IN 46542`
  - *Census: no match* (the geocoder abstains on messy input — judge on the labels alone)

**Verdict:** _____   (A / B / neither / skip)

---

## Group 2 — 1 address

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
  - *Census: no match* (the geocoder abstains on messy input — judge on the labels alone)

**Verdict:** _____   (A / B / neither / skip)

---

## Group 3 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `E` | StreetNamePreDirectional | StreetNamePostDirectional |
| `NORTH` | StreetName | SubaddressIdentifier |
| `WATER` | OccupancyType | SubaddressType |
| `2500` | OccupancyIdentifier | SubaddressIdentifier |

**Examples:**

- `340 E NORTH WATER 2500 CHICAGO IL 60611`
  - *Census records:* 340 E NORTH WATER ST, CHICAGO, IL, 60611 — pre-direction `E`, street name **NORTH WATER**, street type `ST`, city **CHICAGO** *(block range 300-498, not this address's number)*

**Verdict:** _____   (A / B / neither / skip)

---

## Group 4 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `D.C.` | PlaceName | StateName |

**Examples:**

- `99 s spruce road apt. #4b, D.C. 20500`
  - *Census: no match* (the geocoder abstains on messy input — judge on the labels alone)

**Verdict:** _____   (A / B / neither / skip)

---

## Group 5 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `RR` | StreetNamePreType | USPSBoxType |
| `422` | StreetName | USPSBoxID |
| `Box,` | StreetName | USPSBoxType |

**Examples:**

- `RR 422 Box, Douglassville, PA 19518`
  - *Census: no match* (the geocoder abstains on messy input — judge on the labels alone)

**Verdict:** _____   (A / B / neither / skip)

---

## Group 6 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `ORL` | PlaceName | OccupancyIdentifier |
| `FL` | StateName | OccupancyType |

**Examples:**

- `300 orange ave, fl 7, ORL FL`
  - *Census records:* 300 ORANGE AVE, SAINT AUGUSTINE, FL, 32092 — street name **ORANGE**, street type `AVE`, city **SAINT AUGUSTINE** *(block range 532-100, not this address's number)* ⚠️ **suspect match — the geocoder resolved to a city not in the input**

**Verdict:** _____   (A / B / neither / skip)

---

## Group 7 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `1/2` | AddressNumberSuffix | StreetName |

**Examples:**

- `33 1/2 AVE`
  - *Census: no match* (the geocoder abstains on messy input — judge on the labels alone)

**Verdict:** _____   (A / B / neither / skip)

---

## Group 8 — 1 address

**The disagreement:**

| Token | Model A says | Model B says |
|---|---|---|
| `ST` | StreetName | StreetNamePostType |
| `UNT` | StreetName | PlaceName |
| `D` | StreetNamePostType | PlaceName |

**Examples:**

- `210 CRYSTAL ST UNT D CARY IL 60013`
  - *Census records:* 210 CRYSTAL ST, CARY, IL, 60013 — street name **CRYSTAL**, street type `ST`, city **CARY** *(block range 298-200, not this address's number)*

**Verdict:** _____   (A / B / neither / skip)

---

## Already decided last round — no action needed

These shapes match verdicts you already gave; they are carried forward automatically and listed only so the record is complete.

- 31 address(es) differing on `51`, `ST`, `JAMES` — your prior verdict favors **Model A** here
- 3 address(es) differing on `Square,` — your prior verdict favors **Model B** here
- 2 address(es) differing on `140` — your prior verdict favors **Model A** here
- 1 address(es) differing on `LK` — your prior verdict favors **Model A** here
- 1 address(es) differing on `Mi`, `K`, `Beach` — your prior verdict favors **Model A** here
- 1 address(es) differing on `313`, `RR`, `313` — your prior verdict favors **Model skip** here
- 1 address(es) differing on `AND`, `DALES` — your prior verdict favors **Model A** here
- 1 address(es) differing on `BROADWAY`, `NEW` — your prior verdict favors **Model neither** here

---

## When you're done

Tell the agent it's filled in. It will read the verdicts, un-blind them, and score the gold gate — which decides whether the retrained model ships or stays shelved.

Disclosed limitation: judging only contested cases measures *relative* accuracy on the cases where the parsers differ, not absolute accuracy across all 1,500. It informs the decision; it does not replace the full-set gate in the protocol.