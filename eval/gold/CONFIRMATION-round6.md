# Address review — Round 6: 4 parses

## Where this sits

The new candidate (v36) has passed everything machine-checkable: byte-exact on upstream's held-out set (159/159), every one of your previous verdicts honored, both national scans, and — for the first time — the one-shot binding validation on 20 never-touched counties (70.5% right vs 17.3%, every county clean, with El Paso deliberately included as the hardest Spanish-language geography).

These 4 addresses are the only records on the primary gold set where v36 disagrees with the original and no human verdict exists yet. Your answers make the gold-set margin exact. After this, one review round remains — the national free-text set, which is what any public "national" claim will rest on.

No planted trap this time, and I won't claim one: judge each on its evidence. The blinding is real as always — models are A/B under a fresh key, and the suggestion line shows the earlier unconfirmed answer where one exists.

## How to answer

The two parsers are hidden as **A** and **B**, reshuffled for this round, so the suggestion can't sway you. Each table shows the whole address so you can see the reading in context; the rows they actually disagree on are marked **←** and bolded.

Write one of: **A** · **B** · **neither** (both readings wrong) · **skip** (genuinely ambiguous). **Suggested** is the earlier unconfirmed answer — agreeing with it is a fine outcome, it just needs to be your call.

Where a Census record was found it's quoted underneath. Treat it as evidence, not proof: anything flagged with ⚠️ resolved to a city that isn't in the address, which usually means the geocoder guessed.

---

## 1. `4517 SEAGROVE LANDING ESTERO FL 34134`

| | Token | Model A | Model B |
|---|---|---|---|
| | `4517` | AddressNumber | AddressNumber |
| | `SEAGROVE` | StreetName | StreetName |
| **←** | `LANDING` | **StreetName** | **StreetNamePostType** |
| | `ESTERO` | PlaceName | PlaceName |
| | `FL` | StateName | StateName |
| | `34134` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 2. `416 MORGAN LANE FOX RVR GRV IL 60021`

| | Token | Model A | Model B |
|---|---|---|---|
| | `416` | AddressNumber | AddressNumber |
| | `MORGAN` | StreetName | StreetName |
| **←** | `LANE` | **StreetName** | **StreetNamePostType** |
| **←** | `FOX` | **StreetName** | **PlaceName** |
| **←** | `RVR` | **StreetNamePostType** | **PlaceName** |
| | `GRV` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60021` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 3. `2926 Franklin Road Southwest, Roanoke, VA 24000`

| | Token | Model A | Model B |
|---|---|---|---|
| | `2926` | AddressNumber | AddressNumber |
| | `Franklin` | StreetName | StreetName |
| | `Road` | StreetNamePostType | StreetNamePostType |
| **←** | `Southwest,` | **PlaceName** | **StreetNamePostDirectional** |
| | `Roanoke,` | PlaceName | PlaceName |
| | `VA` | StateName | StateName |
| | `24000` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 4. `1285 Highway 7 East, Hutchinson, MN 55350`

| | Token | Model A | Model B |
|---|---|---|---|
| | `1285` | AddressNumber | AddressNumber |
| | `Highway` | StreetNamePreType | StreetNamePreType |
| | `7` | StreetName | StreetName |
| **←** | `East,` | **StreetName** | **StreetNamePostDirectional** |
| | `Hutchinson,` | PlaceName | PlaceName |
| | `MN` | StateName | StateName |
| | `55350` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## When you're done

Paste the answers back in any form — `1. A, 2. B, 3. neither` is fine, and you can group runs of the same answer. I'll un-blind them, fold them into the record, and recompute the margin using only human-reviewed evidence so the published figure is one you stood behind.

If any of these are genuinely too ambiguous to call, **skip** is a real answer and is recorded as such — a forced guess would be worse than an honest gap.