# Confirmation round — 40 addresses

## Why you're being asked for these

The evaluation protocol we wrote *before* training anything says only records a human reviewed may count toward the ship decision. The first batch of verdicts came from ChatGPT and were never confirmed by you, so by our own rule they cannot be used.

These **40** are the only records where that matters. Everywhere else the two models produce an identical parse, and an identical parse can't make one model look better than the other — so those records need no judgment at all.

Models are blinded as **A** and **B** (key re-rolled for this round and written to the repo, so the suggestion below can't tip you off). **Suggested** is the earlier unconfirmed answer. Confirm it or write a different one.

Answer **A**, **B**, **neither** (both parses wrong), or **skip** (genuinely ambiguous).

---

## 1. `51 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 51 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `51` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `JAMES` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 2. `212 EAST RAND RD MT PROSPECT IL 60056`

| Token | Model A | Model B |
|---|---|---|
| `RD` | **StreetNamePostType** | **StreetName** |
| `MT` | **PlaceName** | **StreetNamePostType** |

**Suggested:** A  →  **Your verdict:** _____

---

## 3. `425 SHORELINE RD LK BARRNGTN IL 60010`

*Census record:* 425 SHORELINE RD, BARRINGTON, IL, 60010 — street **SHORELINE**, type `RD`, pre-dir `-`, post-dir `-`, city **BARRINGTON**
  (block range 257-809 — the range this address falls in, not its own number)  ⚠️ *resolved to a city not present in the input — treat as suspect*

| Token | Model A | Model B |
|---|---|---|
| `LK` | **PlaceName** | **StreetNamePostType** |

**Suggested:** A  →  **Your verdict:** _____

---

## 4. `1251 N PLUM GROVE 140 SCHAUMBURG IL 60173`

*Census record:* 1251 N PLUM GROVE RD, SCHAUMBURG, IL, 60173 — street **PLUM GROVE**, type `RD`, pre-dir `N`, post-dir `-`, city **SCHAUMBURG**
  (block range 1201-1299 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `140` | **OccupancyIdentifier** | **StreetName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 5. `111 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 111 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `111` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 6. `109 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 109 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `109` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 7. `116 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 116 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `116` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 8. `96 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 96 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `96` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 9. `101 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 101 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `101` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 10. `85 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 85 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `85` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 11. `45 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 45 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `45` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `JAMES` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 12. `93 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 93 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `93` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 13. `92 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 92 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `92` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 14. `95 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 95 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `95` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 15. `55 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 55 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `55` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `JAMES` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 16. `107 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 107 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `107` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 17. `47 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 47 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `47` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `JAMES` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 18. `103 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 103 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `103` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 19. `Mi K Beach Road # 2, Kenai, AK 99611`

| Token | Model A | Model B |
|---|---|---|
| `Mi` | **StreetNamePreType** | **AddressNumberPrefix** |
| `K` | **StreetName** | **AddressNumber** |
| `Beach` | **StreetName** | **StreetNamePreType** |
| `Road` | **StreetNamePostType** | **StreetNamePreType** |
| `#` | **OccupancyIdentifier** | **StreetName** |
| `2,` | **OccupancyIdentifier** | **StreetName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 20. `98 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 98 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `98` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 21. `122 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 122 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `122` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 22. `87 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 87 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `87` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 23. `115 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 115 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `115` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 24. `128 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 128 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `128` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 25. `104 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 104 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `104` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 26. `Route 313 RR 313 Box, Arlington, VT 05250`

| Token | Model A | Model B |
|---|---|---|
| `Route` | **NotAddress** | **USPSBoxGroupType** |
| `313` | **NotAddress** | **USPSBoxGroupID** |
| `RR` | **USPSBoxType** | **USPSBoxGroupType** |

**Suggested:** skip  →  **Your verdict:** _____

---

## 27. `59 ST JAMES PLACE NEW YORK NY 10038`

*Census record:* 59 ST JAMES PL, NEW YORK, NY, 10038 — street **ST JAMES**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 1-99 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `59` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `JAMES` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 28. `94 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 94 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `94` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 29. `100 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 100 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `100` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 30. `113 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 113 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `113` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 31. `102 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 102 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `102` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 32. `118 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 118 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `118` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 33. `63 HILLS AND DALES BARRINGTON IL 60010`

| Token | Model A | Model B |
|---|---|---|
| `AND` | **StreetName** | **StreetNamePostType** |
| `DALES` | **StreetName** | **PlaceName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 34. `295 South 250 East, Burley, ID 83318`

| Token | Model A | Model B |
|---|---|---|
| `South` | **StreetNamePreType** | **StreetNamePreDirectional** |

**Suggested:** *(never judged)*  →  **Your verdict:** _____

---

## 35. `BROADWAY NEW YORK NY 10013`

| Token | Model A | Model B |
|---|---|---|
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** neither  →  **Your verdict:** _____

---

## 36. `119 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 119 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `119` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 37. `114 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 114 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `114` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 38. `121 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 121 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 85-199 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `121` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## 39. `6 West South Water Market, Chicago, IL 60608`

| Token | Model A | Model B |
|---|---|---|
| `Market,` | **StreetName** | **StreetNamePostType** |

**Suggested:** A  →  **Your verdict:** _____

---

## 40. `126 ST MARKS PLACE NEW YORK NY 10009`

*Census record:* 126 SAINT MARKS PL, NEW YORK, NY, 10009 — street **SAINT MARKS**, type `PL`, pre-dir `-`, post-dir `-`, city **NEW YORK**
  (block range 90-198 — the range this address falls in, not its own number)

| Token | Model A | Model B |
|---|---|---|
| `126` | **AddressNumber** | **StreetName** |
| `ST` | **StreetName** | **StreetNamePostType** |
| `MARKS` | **StreetName** | **PlaceName** |
| `PLACE` | **StreetNamePostType** | **PlaceName** |
| `NEW` | **PlaceName** | **StateName** |

**Suggested:** A  →  **Your verdict:** _____

---

## When you're done

Paste the answers back. The agent un-blinds them, recomputes the full-set margin using only human-reviewed evidence, and reports whether the model clears the pre-registered +3.0 percentage-point bar.