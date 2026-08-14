# Address review — 40 parses to judge

## What this is

Each entry below is one real address where the original parser and the retrained one disagree about what the pieces mean. You're deciding which reading is right.

**This will not get the new model shipped, and it isn't meant to.** The model misses the accuracy bar we set before building it, and it misses by more than these records can close. What these verdicts do is make the evidence real. We're going to publish that failure openly, with the numbers behind it — and the protocol we wrote in advance says only records a human actually reviewed may count. The first batch of answers came from ChatGPT and were never confirmed by you. Until they are, the published result rests on machine-generated judgments, which is exactly the kind of claim this project exists to not make.

These **40** are the only ones that matter. Everywhere else the two parsers agree, and when they agree neither can look better than the other — so those need no judgment at all.

## How to answer

The two parsers are hidden as **A** and **B**, reshuffled for this round, so the suggestion can't sway you. Each table shows the whole address so you can see the reading in context; the rows they actually disagree on are marked **←** and bolded.

Write one of: **A** · **B** · **neither** (both readings wrong) · **skip** (genuinely ambiguous). **Suggested** is the earlier unconfirmed answer — agreeing with it is a fine outcome, it just needs to be your call.

Where a Census record was found it's quoted underneath. Treat it as evidence, not proof: anything flagged with ⚠️ resolved to a city that isn't in the address, which usually means the geocoder guessed.

---

## 1. `51 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 51 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `51` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `JAMES` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10038` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 2. `212 EAST RAND RD MT PROSPECT IL 60056`

| | Token | Model A | Model B |
|---|---|---|---|
| | `212` | AddressNumber | AddressNumber |
| | `EAST` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `RAND` | StreetName | StreetName |
| **←** | `RD` | **StreetNamePostType** | **StreetName** |
| **←** | `MT` | **PlaceName** | **StreetNamePostType** |
| | `PROSPECT` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60056` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 3. `425 SHORELINE RD LK BARRNGTN IL 60010`

*Census record:* 425 SHORELINE RD, BARRINGTON, IL, 60010 — street **SHORELINE**, type `RD`, pre-dir `-`, post-dir `-`, city **BARRINGTON**
  (block range 257-809 — the range this address falls in, not its own number)  ⚠️ *resolved to a city not present in the input — treat as suspect*

| | Token | Model A | Model B |
|---|---|---|---|
| | `425` | AddressNumber | AddressNumber |
| | `SHORELINE` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `LK` | **PlaceName** | **StreetNamePostType** |
| | `BARRNGTN` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 4. `1251 N PLUM GROVE 140 SCHAUMBURG IL 60173`

*Census record:* 1251 N PLUM GROVE RD, SCHAUMBURG, IL, 60173 — street **PLUM GROVE**, type `RD`, pre-dir `N`, post-dir `-`, city **SCHAUMBURG**
  (block range 1201-1299 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| | `1251` | AddressNumber | AddressNumber |
| | `N` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `PLUM` | StreetName | StreetName |
| | `GROVE` | StreetName | StreetName |
| **←** | `140` | **OccupancyIdentifier** | **StreetName** |
| | `SCHAUMBURG` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60173` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 5. `111 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 111 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `111` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 6. `109 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 109 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `109` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 7. `116 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 116 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `116` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 8. `96 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 96 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `96` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 9. `101 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 101 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `101` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 10. `85 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 85 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `85` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 11. `45 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 45 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `45` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `JAMES` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10038` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 12. `93 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 93 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `93` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 13. `92 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 92 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `92` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 14. `95 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 95 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `95` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 15. `55 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 55 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `55` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `JAMES` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10038` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 16. `107 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 107 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `107` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 17. `47 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 47 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `47` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `JAMES` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10038` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 18. `103 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 103 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `103` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 19. `Mi K Beach Road # 2, Kenai, AK 99611`

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `Mi` | **StreetNamePreType** | **AddressNumberPrefix** |
| **←** | `K` | **StreetName** | **AddressNumber** |
| **←** | `Beach` | **StreetName** | **StreetNamePreType** |
| **←** | `Road` | **StreetNamePostType** | **StreetNamePreType** |
| **←** | `#` | **OccupancyIdentifier** | **StreetName** |
| **←** | `2,` | **OccupancyIdentifier** | **StreetName** |
| | `Kenai,` | PlaceName | PlaceName |
| | `AK` | StateName | StateName |
| | `99611` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 20. `98 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 98 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `98` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 21. `122 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 122 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `122` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 22. `87 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 87 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `87` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 23. `115 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 115 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `115` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 24. `128 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 128 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `128` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 25. `104 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 104 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `104` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 26. `Route 313 RR 313 Box, Arlington, VT 05250`

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `Route` | **NotAddress** | **USPSBoxGroupType** |
| **←** | `313` | **NotAddress** | **USPSBoxGroupID** |
| **←** | `RR` | **USPSBoxType** | **USPSBoxGroupType** |
| | `313` | USPSBoxID | USPSBoxID |
| | `Box,` | USPSBoxType | USPSBoxType |
| | `Arlington,` | PlaceName | PlaceName |
| | `VT` | StateName | StateName |
| | `05250` | ZipCode | ZipCode |

**Suggested: skip**  →  **Your verdict:** `      `

---

## 27. `59 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 59 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `59` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `JAMES` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10038` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 28. `94 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 94 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `94` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 29. `100 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 100 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `100` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 30. `113 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 113 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `113` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 31. `102 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 102 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `102` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 32. `118 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 118 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `118` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 33. `63 HILLS AND DALES BARRINGTON IL 60010`

| | Token | Model A | Model B |
|---|---|---|---|
| | `63` | AddressNumber | AddressNumber |
| | `HILLS` | StreetName | StreetName |
| **←** | `AND` | **StreetName** | **StreetNamePostType** |
| **←** | `DALES` | **StreetName** | **PlaceName** |
| | `BARRINGTON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60010` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 34. `295 South 250 East, Burley, ID 83318`

| | Token | Model A | Model B |
|---|---|---|---|
| | `295` | AddressNumber | AddressNumber |
| **←** | `South` | **StreetNamePreType** | **StreetNamePreDirectional** |
| | `250` | StreetName | StreetName |
| | `East,` | StreetNamePostDirectional | StreetNamePostDirectional |
| | `Burley,` | PlaceName | PlaceName |
| | `ID` | StateName | StateName |
| | `83318` | ZipCode | ZipCode |

**Suggested: none — never judged**  →  **Your verdict:** `      `

---

## 35. `BROADWAY NEW YORK NY 10013`

| | Token | Model A | Model B |
|---|---|---|---|
| | `BROADWAY` | PlaceName | PlaceName |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10013` | ZipCode | ZipCode |

**Suggested: neither**  →  **Your verdict:** `      `

---

## 36. `119 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 119 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `119` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 37. `114 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 114 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `114` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 38. `121 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 121 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `121` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 39. `6 West South Water Market, Chicago, IL 60608`

| | Token | Model A | Model B |
|---|---|---|---|
| | `6` | AddressNumber | AddressNumber |
| | `West` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `South` | StreetName | StreetName |
| | `Water` | StreetName | StreetName |
| **←** | `Market,` | **StreetName** | **StreetNamePostType** |
| | `Chicago,` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60608` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## 40. `126 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 126 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `126` | **AddressNumber** | **StreetName** |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `MARKS` | **StreetName** | **PlaceName** |
| **←** | `PLACE` | **StreetNamePostType** | **PlaceName** |
| **←** | `NEW` | **PlaceName** | **StateName** |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10009` | ZipCode | ZipCode |

**Suggested: A**  →  **Your verdict:** `      `

---

## When you're done

Paste the answers back in any form — `1. A, 2. B, 3. neither` is fine, and you can group runs of the same answer. I'll un-blind them, fold them into the record, and recompute the margin using only human-reviewed evidence so the published figure is one you stood behind.

If any of these are genuinely too ambiguous to call, **skip** is a real answer and is recorded as such — a forced guess would be worse than an honest gap.