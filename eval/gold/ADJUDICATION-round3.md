# Adjudication round 3 — 6 addresses

The candidate now differs from the incumbent on 49 of 1,500 messy addresses. **43 already have your verdicts** and are excluded. These 6 are the ones never judged.

Models are blinded as **A** and **B** (the key is re-rolled each round and written to the repo). Judge which parse is *correct*. Answer **A**, **B**, **neither**, or **skip**.

---

## 1. `Terra Alta, WV 26764`

| Token | Model A | Model B |
|---|---|---|
| `Terra` | LandmarkName | PlaceName |
| `Alta,` | LandmarkName | PlaceName |

**Verdict:** _____

---

## 2. `3 Cherry LANE Miami`

| Token | Model A | Model B |
|---|---|---|
| `Miami` | OccupancyIdentifier | PlaceName |

**Verdict:** _____

---

## 3. `12100 WILSHIRE 1210 LOS ANGELES CA 90025`

| Token | Model A | Model B |
|---|---|---|
| `WILSHIRE` | StreetNamePreType | StreetName |
| `1210` | StreetName | OccupancyIdentifier |

**Verdict:** _____

---

## 4. `1 The Square, Lillington, NC 27546`

| Token | Model A | Model B |
|---|---|---|
| `Square,` | StreetName | StreetNamePostType |

**Verdict:** _____

---

## 5. `5051 PELICAN COLONY901 BONITA SPRGS FL 34134`

*Census:* 5051 PELICAN COLONY BLVD, BONITA SPRINGS, FL, 34134 — street **PELICAN COLONY**, type `BLVD`, city **BONITA SPRINGS** ⚠️ *(resolved to a city not in the input — treat with suspicion)*

| Token | Model A | Model B |
|---|---|---|
| `COLONY901` | OccupancyIdentifier | StreetName |

**Verdict:** _____

---

## 6. `807 South Central Expressway, Richardson, TX 75080`

*Census:* 807 S CENTRAL EXPY, RICHARDSON, TX, 75080 — street **CENTRAL**, type `EXPY`, city **RICHARDSON**

| Token | Model A | Model B |
|---|---|---|
| `Expressway,` | StreetName | StreetNamePostType |

**Verdict:** _____

---

## When you're done

Tell the agent. It will un-blind, fold these into the running tally, and report whether the candidate is clean across every adjudicated record — the last evidence gap before a ship decision.