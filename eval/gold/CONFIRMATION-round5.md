# Address review — 36 parses to judge

## What this is

Each entry below is one real address where the original parser and the retrained one disagree about what the pieces mean. You're deciding which reading is right.

**These decide whether the new model ships.** It already clears every other gate: it matches the original exactly on upstream's held-out set (159/159) and gets every one of the 75 previously-judged records right. What it also does is relabel the addresses below, and the accuracy bar we set before building anything can only count records a human has actually reviewed. If these go the model's way it clears the bar; if they don't, it doesn't ship. Please judge them on the evidence rather than on that fact — a bar we talk ourselves over is worth nothing.

**One of them is a trap, deliberately left in.** At least one address here is a case where the model's new reading is wrong and the original was right. The Census evidence under each entry will show you which. I have not marked it.

These **36** are the only ones that matter. Everywhere else the two parsers agree, and when they agree neither can look better than the other — so those need no judgment at all.

## How to answer

The two parsers are hidden as **A** and **B**, reshuffled for this round, so the suggestion can't sway you. Each table shows the whole address so you can see the reading in context; the rows they actually disagree on are marked **←** and bolded.

Write one of: **A** · **B** · **neither** (both readings wrong) · **skip** (genuinely ambiguous). **Suggested** is the earlier unconfirmed answer — agreeing with it is a fine outcome, it just needs to be your call.

Where a Census record was found it's quoted underneath. Treat it as evidence, not proof: anything flagged with ⚠️ resolved to a city that isn't in the address, which usually means the geocoder guessed.

---

## 1. `9 WALNUT LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **WALNUT**

| | Token | Model A | Model B |
|---|---|---|---|
| | `9` | AddressNumber | AddressNumber |
| | `WALNUT` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 2. `474 n lake shore 3910 CHICAGO IL 60611`

| | Token | Model A | Model B |
|---|---|---|---|
| | `474` | AddressNumber | AddressNumber |
| | `n` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `lake` | StreetName | StreetName |
| **←** | `shore` | **StreetName** | **StreetNamePostType** |
| | `3910` | OccupancyIdentifier | OccupancyIdentifier |
| | `CHICAGO` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60611` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 3. `1305 Lake Shore Dr N BARRINGTON IL 60010`

*Census splits this as:* city **BARRINGTON**, street **LAKE SHORE** with suffix direction **N** — here the `N` really is a **direction**, not part of the city

| | Token | Model A | Model B |
|---|---|---|---|
| | `1305` | AddressNumber | AddressNumber |
| | `Lake` | StreetName | StreetName |
| | `Shore` | StreetName | StreetName |
| | `Dr` | StreetNamePostType | StreetNamePostType |
| **←** | `N` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 4. `4 DEVERAUX COURT S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **DEVEAUX**

| | Token | Model A | Model B |
|---|---|---|---|
| | `4` | AddressNumber | AddressNumber |
| | `DEVERAUX` | StreetName | StreetName |
| | `COURT` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 5. `5 BROOKHAVEN CIRCLE S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **BROOKHAVEN**

| | Token | Model A | Model B |
|---|---|---|---|
| | `5` | AddressNumber | AddressNumber |
| | `BROOKHAVEN` | StreetName | StreetName |
| | `CIRCLE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 6. `27 WYCHWOOD LANE S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **WYCHWOOD**

| | Token | Model A | Model B |
|---|---|---|---|
| | `27` | AddressNumber | AddressNumber |
| | `WYCHWOOD` | StreetName | StreetName |
| | `LANE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 7. `32 WYCHWOOD LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **WYCHWOOD**

| | Token | Model A | Model B |
|---|---|---|---|
| | `32` | AddressNumber | AddressNumber |
| | `WYCHWOOD` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 8. `6 LEANDA LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **LEANDA**

| | Token | Model A | Model B |
|---|---|---|---|
| | `6` | AddressNumber | AddressNumber |
| | `LEANDA` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 9. `13 SPRING CREEK DRIVE S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **SPRING CREEK**

| | Token | Model A | Model B |
|---|---|---|---|
| | `13` | AddressNumber | AddressNumber |
| | `SPRING` | StreetName | StreetName |
| | `CREEK` | StreetName | StreetName |
| | `DRIVE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 10. `37 BEECHNUT DRIVE S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **BEECHNUT**

| | Token | Model A | Model B |
|---|---|---|---|
| | `37` | AddressNumber | AddressNumber |
| | `BEECHNUT` | StreetName | StreetName |
| | `DRIVE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 11. `5 BROOKE LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **BROOKE**

| | Token | Model A | Model B |
|---|---|---|---|
| | `5` | AddressNumber | AddressNumber |
| | `BROOKE` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 12. `1 WALNUT LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **WALNUT**

| | Token | Model A | Model B |
|---|---|---|---|
| | `1` | AddressNumber | AddressNumber |
| | `WALNUT` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 13. `8 FALCON COURT S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **FALCON**

| | Token | Model A | Model B |
|---|---|---|---|
| | `8` | AddressNumber | AddressNumber |
| | `FALCON` | StreetName | StreetName |
| | `COURT` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 14. `12 BROOKE LN S BARRINGTON IL 60010`

| | Token | Model A | Model B |
|---|---|---|---|
| | `12` | AddressNumber | AddressNumber |
| | `BROOKE` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 15. `42 HAVERSHAM LN N BARRINGTON IL 60010`

*Census splits this as:* city **N BARRINGTON** — the `N` is part of the **city name**, street is **HAVERSHAM**

| | Token | Model A | Model B |
|---|---|---|---|
| | `42` | AddressNumber | AddressNumber |
| | `HAVERSHAM` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `N` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 16. `10 BROOKE LANE S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **BROOKE**

| | Token | Model A | Model B |
|---|---|---|---|
| | `10` | AddressNumber | AddressNumber |
| | `BROOKE` | StreetName | StreetName |
| | `LANE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 17. `2 LEANDA LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **LEANDA**

| | Token | Model A | Model B |
|---|---|---|---|
| | `2` | AddressNumber | AddressNumber |
| | `LEANDA` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 18. `6 WOODBURY CT S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **WOODBURY**

| | Token | Model A | Model B |
|---|---|---|---|
| | `6` | AddressNumber | AddressNumber |
| | `WOODBURY` | StreetName | StreetName |
| | `CT` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 19. `30 W PENNY RD S BARRINGTON IL 60010`

| | Token | Model A | Model B |
|---|---|---|---|
| | `30` | AddressNumber | AddressNumber |
| | `W` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `PENNY` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 20. `4 WIND RIDGE RD S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **WIND RIDGE**

| | Token | Model A | Model B |
|---|---|---|---|
| | `4` | AddressNumber | AddressNumber |
| | `WIND` | StreetName | StreetName |
| | `RIDGE` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 21. `46 SHENANDOAH CIRCLE S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **SHENANDOAH**

| | Token | Model A | Model B |
|---|---|---|---|
| | `46` | AddressNumber | AddressNumber |
| | `SHENANDOAH` | StreetName | StreetName |
| | `CIRCLE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 22. `7 LOCH LANE S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **LOCH**

| | Token | Model A | Model B |
|---|---|---|---|
| | `7` | AddressNumber | AddressNumber |
| | `LOCH` | StreetName | StreetName |
| | `LANE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 23. `6 E PENNY RD S BARRINGTON IL 60010`

| | Token | Model A | Model B |
|---|---|---|---|
| | `6` | AddressNumber | AddressNumber |
| | `E` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `PENNY` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 24. `4 LOCH LANE S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **LOCH**

| | Token | Model A | Model B |
|---|---|---|---|
| | `4` | AddressNumber | AddressNumber |
| | `LOCH` | StreetName | StreetName |
| | `LANE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 25. `12 E PENNY RD S BARRINGTON IL 60010`

| | Token | Model A | Model B |
|---|---|---|---|
| | `12` | AddressNumber | AddressNumber |
| | `E` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `PENNY` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 26. `3 TEWKESBURY LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **TEWKESBURY**

| | Token | Model A | Model B |
|---|---|---|---|
| | `3` | AddressNumber | AddressNumber |
| | `TEWKESBURY` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 27. `4 LOCH LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **LOCH**

| | Token | Model A | Model B |
|---|---|---|---|
| | `4` | AddressNumber | AddressNumber |
| | `LOCH` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 28. `Anchor Point, AK 99556`

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `Anchor` | **StreetName** | **PlaceName** |
| | `Point,` | PlaceName | PlaceName |
| | `AK` | StateName | StateName |
| | `99556` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 29. `18 FOREST LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **FOREST**

| | Token | Model A | Model B |
|---|---|---|---|
| | `18` | AddressNumber | AddressNumber |
| | `FOREST` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 30. `5 TAYNTON LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **TAYNTON**

| | Token | Model A | Model B |
|---|---|---|---|
| | `5` | AddressNumber | AddressNumber |
| | `TAYNTON` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 31. `2 DEVEAUX CT S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **DEVEAUX**

| | Token | Model A | Model B |
|---|---|---|---|
| | `2` | AddressNumber | AddressNumber |
| | `DEVEAUX` | StreetName | StreetName |
| | `CT` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 32. `26 RAINIER CIRCLE S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **RAINIER**

| | Token | Model A | Model B |
|---|---|---|---|
| | `26` | AddressNumber | AddressNumber |
| | `RAINIER` | StreetName | StreetName |
| | `CIRCLE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 33. `2 LOCH LN S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **LOCH**

| | Token | Model A | Model B |
|---|---|---|---|
| | `2` | AddressNumber | AddressNumber |
| | `LOCH` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 34. `3 WINDRIDGE RD S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **WIND RIDGE**

| | Token | Model A | Model B |
|---|---|---|---|
| | `3` | AddressNumber | AddressNumber |
| | `WINDRIDGE` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 35. `14 LEANDA CT S BARRINGTON IL 60010`

*Census splits this as:* city **S BARRINGTON** — the `S` is part of the **city name**, street is **LEANDA**

| | Token | Model A | Model B |
|---|---|---|---|
| | `14` | AddressNumber | AddressNumber |
| | `LEANDA` | StreetName | StreetName |
| | `CT` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 36. `54 W PENNY RD S BARRINGTON IL 60010`

| | Token | Model A | Model B |
|---|---|---|---|
| | `54` | AddressNumber | AddressNumber |
| | `W` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `PENNY` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **PlaceName** | **StreetNamePostDirectional** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## When you're done

Paste the answers back in any form — `1. A, 2. B, 3. neither` is fine, and you can group runs of the same answer. I'll un-blind them, fold them into the record, and recompute the margin using only human-reviewed evidence so the published figure is one you stood behind.

If any of these are genuinely too ambiguous to call, **skip** is a real answer and is recorded as such — a forced guess would be worse than an honest gap.