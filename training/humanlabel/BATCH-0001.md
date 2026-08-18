# Address labeling — batch 1-300 of 5000

## What this is

Real owner-mail addresses the shipping model is **least sure about**, ordered so the most informative come first. Every record you label becomes training data for a future v2 -- the one thing the campaign proved it needs is more real, human-labeled free text of exactly this kind. None of these appear in any evaluation set, so training on them keeps every gold set honest.

## How to answer

Under each address is the model's proposed parse. For each record:
- **`ok`** — the parse is right.
- **A correction** — name only the tokens that are wrong, e.g. `MT = PlaceName; GILEAD = PlaceName` or `LUXSTOR = Recipient`. Everything you don't mention stays as proposed.
- **`skip`** — genuinely ambiguous or you'd be guessing. Never counted; skipping is a real answer.

You'll notice many of these are already wrong — that's the point. The model reads `MT GILEAD` as a box number, splits `EL RENO`, calls a street a state. Your corrections are what fix that. Stop whenever your time runs out; the ordering means you never waste effort on the easy ones.

---

## 1. `38 PENOBSCOT AVE 38 PENOBSCOT AVENUE HOWLAND ME`
*ME · model confidence 0.26*

| Token | Proposed label |
|---|---|
| `38` | AddressNumber |
| `PENOBSCOT` | StreetName |
| `AVE` | StreetNamePostType |
| `38` | AddressNumber |
| `PENOBSCOT` | StreetName |
| `AVENUE` | StreetNamePostType |
| `HOWLAND` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 2. `PO BOX 53 MT GILEAD NC 27306`
*NC · model confidence 0.26*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `53` | USPSBoxID |
| `MT` | USPSBoxID |
| `GILEAD` | PlaceName |
| `NC` | StateName |
| `27306` | ZipCode |

**Your answer:** `      `

---

## 3. `5302 51ST AVE S LUXSTOR LLC, LESSEE FARGO ND 58104`
*ND · model confidence 0.27*

| Token | Proposed label |
|---|---|
| `5302` | AddressNumber |
| `51ST` | StreetName |
| `AVE` | StreetNamePostType |
| `S` | StreetNamePostDirectional |
| `LUXSTOR` | PlaceName |
| `LLC,` | PlaceName |
| `LESSEE` | PlaceName |
| `FARGO` | PlaceName |
| `ND` | StateName |
| `58104` | ZipCode |

**Your answer:** `      `

---

## 4. `%SEAN SPILLER 72 GATES AV 07042`
*NJ · model confidence 0.27*

| Token | Proposed label |
|---|---|
| `SEAN` | Recipient |
| `SPILLER` | Recipient |
| `72` | AddressNumber |
| `GATES` | StreetName |
| `AV` | StreetNamePostType |
| `07042` | ZipCode |

**Your answer:** `      `

---

## 5. `1009 S ROCK ISLAND EL RENO OK 73036-0000`
*OK · model confidence 0.28*

| Token | Proposed label |
|---|---|
| `1009` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `ROCK` | StreetName |
| `ISLAND` | StreetName |
| `EL` | StreetNamePostType |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036-0000` | ZipCode |

**Your answer:** `      `

---

## 6. `Friend EAST WEYMOUTH MA 02189`
*MA · model confidence 0.29*

| Token | Proposed label |
|---|---|
| `Friend` | Recipient |
| `EAST` | Recipient |
| `WEYMOUTH` | PlaceName |
| `MA` | StateName |
| `02189` | ZipCode |

**Your answer:** `      `

---

## 7. `8025 ARROWRIDGE BV 28273 CHARLOTTE NC 28273`
*NC · model confidence 0.30*

| Token | Proposed label |
|---|---|
| `8025` | AddressNumber |
| `ARROWRIDGE` | PlaceName |
| `BV` | StateName |
| `28273` | ZipCode |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28273` | ZipCode |

**Your answer:** `      `

---

## 8. `160 US ROUTE ONE PO BOX 536 FREEPORT ME`
*ME · model confidence 0.33*

| Token | Proposed label |
|---|---|
| `160` | AddressNumber |
| `US` | StreetNamePreType |
| `ROUTE` | StreetNamePreType |
| `ONE` | StreetName |
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `536` | USPSBoxID |
| `FREEPORT` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 9. `2405 S EVANS EL RENO OK 73036`
*OK · model confidence 0.35*

| Token | Proposed label |
|---|---|
| `2405` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `EVANS` | StreetName |
| `EL` | StreetNamePostType |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036` | ZipCode |

**Your answer:** `      `

---

## 10. `21 BAY ROAD EAST HAMPTON CT 6424`
*CT · model confidence 0.35*

| Token | Proposed label |
|---|---|
| `21` | AddressNumber |
| `BAY` | StreetName |
| `ROAD` | StreetNamePostType |
| `EAST` | NotAddress |
| `HAMPTON` | NotAddress |
| `CT` | NotAddress |
| `6424` | OccupancyIdentifier |

**Your answer:** `      `

---

## 11. `6367 UPPER RIDGE WAY ROSCOE IL 61073`
*IL · model confidence 0.36*

| Token | Proposed label |
|---|---|
| `6367` | AddressNumber |
| `UPPER` | StreetName |
| `RIDGE` | StreetNamePostType |
| `WAY` | PlaceName |
| `ROSCOE` | PlaceName |
| `IL` | StateName |
| `61073` | ZipCode |

**Your answer:** `      `

---

## 12. `9 RIVER RD 70 FARM VIEW DRIVE NEW GLOUCESTER ME`
*ME · model confidence 0.36*

| Token | Proposed label |
|---|---|
| `9` | AddressNumber |
| `RIVER` | StreetNamePreType |
| `RD` | StreetNamePreType |
| `70` | StreetName |
| `FARM` | StreetName |
| `VIEW` | StreetName |
| `DRIVE` | StreetNamePostType |
| `NEW` | PlaceName |
| `GLOUCESTER` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 13. `PO BOX 1331 MT GILEAD NC 27306`
*NC · model confidence 0.37*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `1331` | USPSBoxID |
| `MT` | StreetNamePostType |
| `GILEAD` | PlaceName |
| `NC` | StateName |
| `27306` | ZipCode |

**Your answer:** `      `

---

## 14. `7505 NW 113 PATH DORAL FL 0`
*FL · model confidence 0.37*

| Token | Proposed label |
|---|---|
| `7505` | AddressNumber |
| `NW` | StreetNamePreDirectional |
| `113` | StreetName |
| `PATH` | PlaceName |
| `DORAL` | PlaceName |
| `FL` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 15. `355 SPRING HILL LAKE LOOP CAPE CORAL FL 33993`
*FL · model confidence 0.37*

| Token | Proposed label |
|---|---|
| `355` | AddressNumber |
| `SPRING` | StreetName |
| `HILL` | StreetName |
| `LAKE` | StreetName |
| `LOOP` | StreetName |
| `CAPE` | StreetNamePostType |
| `CORAL` | PlaceName |
| `FL` | StateName |
| `33993` | ZipCode |

**Your answer:** `      `

---

## 16. `1-K18 VALPARAIS 0 TOA BAJA PR 949`
*FL · model confidence 0.37*

| Token | Proposed label |
|---|---|
| `1-K18` | AddressNumber |
| `VALPARAIS` | StreetNamePreType |
| `0` | StreetName |
| `TOA` | StreetName |
| `BAJA` | StreetName |
| `PR` | StreetNamePostType |
| `949` | OccupancyIdentifier |

**Your answer:** `      `

---

## 17. `9070 SW 69 TERR MIAMI FL 33173`
*FL · model confidence 0.38*

| Token | Proposed label |
|---|---|
| `9070` | AddressNumber |
| `SW` | StreetNamePostDirectional |
| `69` | OccupancyIdentifier |
| `TERR` | PlaceName |
| `MIAMI` | PlaceName |
| `FL` | StateName |
| `33173` | ZipCode |

**Your answer:** `      `

---

## 18. `11 SOUTH FREEPORT ROAD LORNA DONALD MARK DORSEY FREEPORT ME`
*ME · model confidence 0.38*

| Token | Proposed label |
|---|---|
| `11` | AddressNumber |
| `SOUTH` | StreetNamePreDirectional |
| `FREEPORT` | StreetName |
| `ROAD` | StreetNamePostType |
| `LORNA` | Recipient |
| `DONALD` | Recipient |
| `MARK` | Recipient |
| `DORSEY` | Recipient |
| `FREEPORT` | Recipient |
| `ME` | Recipient |

**Your answer:** `      `

---

## 19. `408 US ROUTE 1 SECOND FLR YORK ME 03909`
*ME · model confidence 0.38*

| Token | Proposed label |
|---|---|
| `408` | AddressNumber |
| `US` | StreetNamePreType |
| `ROUTE` | StreetNamePreType |
| `1` | StreetName |
| `SECOND` | OccupancyIdentifier |
| `FLR` | OccupancyType |
| `YORK` | PlaceName |
| `ME` | StateName |
| `03909` | ZipCode |

**Your answer:** `      `

---

## 20. `5410 E PLACITA DEL MAR TUCSON AZ 85718-4643`
*AZ · model confidence 0.38*

| Token | Proposed label |
|---|---|
| `5410` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `PLACITA` | StreetName |
| `DEL` | StreetName |
| `MAR` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85718-4643` | ZipCode |

**Your answer:** `      `

---

## 21. `0000 CIGRI DRIVE 20 CURTIS ROAD FREEPORT ME`
*ME · model confidence 0.39*

| Token | Proposed label |
|---|---|
| `0000` | AddressNumber |
| `CIGRI` | StreetNamePreType |
| `DRIVE` | StreetNamePreType |
| `20` | StreetName |
| `CURTIS` | StreetName |
| `ROAD` | StreetNamePostType |
| `FREEPORT` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 22. `444 SW 2ND AVE 3RD FLOOR MIAMI FL 0`
*FL · model confidence 0.40*

| Token | Proposed label |
|---|---|
| `444` | AddressNumber |
| `SW` | StreetNamePreDirectional |
| `2ND` | StreetName |
| `AVE` | StreetNamePostType |
| `3RD` | OccupancyIdentifier |
| `FLOOR` | OccupancyType |
| `MIAMI` | OccupancyType |
| `FL` | OccupancyType |
| `0` | OccupancyIdentifier |

**Your answer:** `      `

---

## 23. `7137 POPLAR CREEK TC NASHVILLE TN 37221`
*TN · model confidence 0.41*

| Token | Proposed label |
|---|---|
| `7137` | AddressNumber |
| `POPLAR` | StreetName |
| `CREEK` | StreetName |
| `TC` | StreetNamePostType |
| `NASHVILLE` | PlaceName |
| `TN` | StateName |
| `37221` | ZipCode |

**Your answer:** `      `

---

## 24. `912 W WADE EL RENO OK 73036`
*OK · model confidence 0.41*

| Token | Proposed label |
|---|---|
| `912` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `WADE` | StreetName |
| `EL` | PlaceName |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036` | ZipCode |

**Your answer:** `      `

---

## 25. `6 COPELAND CT 08080`
*NJ · model confidence 0.41*

| Token | Proposed label |
|---|---|
| `6` | AddressNumber |
| `COPELAND` | StreetName |
| `CT` | StreetNamePostType |
| `08080` | ZipCode |

**Your answer:** `      `

---

## 26. `20 LIBERTY RIDGE TRAIL 07512`
*NJ · model confidence 0.41*

| Token | Proposed label |
|---|---|
| `20` | AddressNumber |
| `LIBERTY` | StreetName |
| `RIDGE` | StreetNamePostType |
| `TRAIL` | PlaceName |
| `07512` | ZipCode |

**Your answer:** `      `

---

## 27. `% BANKIOWA 2701 EDGEWOOD PKWY SW CEDAR RAPIDS IA 52404`
*IA · model confidence 0.42*

| Token | Proposed label |
|---|---|
| `BANKIOWA` | Recipient |
| `2701` | AddressNumber |
| `EDGEWOOD` | StreetName |
| `PKWY` | StreetNamePostType |
| `SW` | StreetNamePostDirectional |
| `CEDAR` | PlaceName |
| `RAPIDS` | PlaceName |
| `IA` | StateName |
| `52404` | ZipCode |

**Your answer:** `      `

---

## 28. `1124 W LONDON EL RENO OK 73036-`
*OK · model confidence 0.42*

| Token | Proposed label |
|---|---|
| `1124` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `LONDON` | StreetName |
| `EL` | PlaceName |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036-` | ZipCode |

**Your answer:** `      `

---

## 29. `1514 W LONDON EL RENO OK 73036-0000`
*OK · model confidence 0.42*

| Token | Proposed label |
|---|---|
| `1514` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `LONDON` | StreetName |
| `EL` | PlaceName |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036-0000` | ZipCode |

**Your answer:** `      `

---

## 30. `205 N ADMIRE EL RENO OK 73036`
*OK · model confidence 0.42*

| Token | Proposed label |
|---|---|
| `205` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `ADMIRE` | StreetName |
| `EL` | PlaceName |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036` | ZipCode |

**Your answer:** `      `

---

## 31. `319 N BARKER EL RENO OK 73036-0000`
*OK · model confidence 0.42*

| Token | Proposed label |
|---|---|
| `319` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `BARKER` | StreetName |
| `EL` | PlaceName |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036-0000` | ZipCode |

**Your answer:** `      `

---

## 32. `109 PROV N L TPKE NORTH STONINGTON CT 6359`
*CT · model confidence 0.42*

| Token | Proposed label |
|---|---|
| `109` | AddressNumber |
| `PROV` | StreetName |
| `N` | StreetName |
| `L` | StreetName |
| `TPKE` | StreetName |
| `NORTH` | StreetNamePostDirectional |
| `STONINGTON` | PlaceName |
| `CT` | StateName |
| `6359` | ZipCode |

**Your answer:** `      `

---

## 33. `3886 TREASURE OAK WAY FORT MYERS FL 33905`
*FL · model confidence 0.42*

| Token | Proposed label |
|---|---|
| `3886` | AddressNumber |
| `TREASURE` | StreetName |
| `OAK` | PlaceName |
| `WAY` | PlaceName |
| `FORT` | PlaceName |
| `MYERS` | PlaceName |
| `FL` | StateName |
| `33905` | ZipCode |

**Your answer:** `      `

---

## 34. `701 NW 1 CT 16TH FLOOR MIAMI FL 0`
*FL · model confidence 0.43*

| Token | Proposed label |
|---|---|
| `701` | AddressNumber |
| `NW` | StreetNamePreDirectional |
| `1` | StreetName |
| `CT` | StreetNamePostType |
| `16TH` | OccupancyIdentifier |
| `FLOOR` | OccupancyType |
| `MIAMI` | OccupancyType |
| `FL` | OccupancyType |
| `0` | OccupancyIdentifier |

**Your answer:** `      `

---

## 35. `3 AVENIDA DEL MONTE SANDIA PARK NM 87047-9487`
*NM · model confidence 0.43*

| Token | Proposed label |
|---|---|
| `3` | AddressNumber |
| `AVENIDA` | StreetName |
| `DEL` | StreetName |
| `MONTE` | StreetName |
| `SANDIA` | PlaceName |
| `PARK` | PlaceName |
| `NM` | StateName |
| `87047-9487` | ZipCode |

**Your answer:** `      `

---

## 36. `2626 AVENUE S BIRMINGHAM AL 35218-2838`
*AL · model confidence 0.43*

| Token | Proposed label |
|---|---|
| `2626` | AddressNumber |
| `AVENUE` | StreetName |
| `S` | StreetNamePostDirectional |
| `BIRMINGHAM` | PlaceName |
| `AL` | StateName |
| `35218-2838` | ZipCode |

**Your answer:** `      `

---

## 37. `PSC 455 BOX 4345 FPO AP 0`
*NC · model confidence 0.43*

| Token | Proposed label |
|---|---|
| `PSC` | USPSBoxType |
| `455` | USPSBoxID |
| `BOX` | USPSBoxType |
| `4345` | USPSBoxID |
| `FPO` | PlaceName |
| `AP` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 38. `80 S 8TH ST 4916 IDS CENTER MINNEAPOLIS MN 55402`
*ND · model confidence 0.43*

| Token | Proposed label |
|---|---|
| `80` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `8TH` | StreetName |
| `ST` | StreetNamePostType |
| `4916` | OccupancyIdentifier |
| `IDS` | PlaceName |
| `CENTER` | PlaceName |
| `MINNEAPOLIS` | PlaceName |
| `MN` | StateName |
| `55402` | ZipCode |

**Your answer:** `      `

---

## 39. `2701 JENNY GULCH RAPID CITY SD 57702-7040`
*SD · model confidence 0.43*

| Token | Proposed label |
|---|---|
| `2701` | AddressNumber |
| `JENNY` | StreetName |
| `GULCH` | StreetName |
| `RAPID` | StreetNamePostType |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57702-7040` | ZipCode |

**Your answer:** `      `

---

## 40. `20805 NE 91ST 98053`
*WA · model confidence 0.43*

| Token | Proposed label |
|---|---|
| `20805` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `91ST` | StreetName |
| `98053` | ZipCode |

**Your answer:** `      `

---

## 41. `2400 HIDDEN TRAIL CT 28105 MATTHEWS NC 28105`
*NC · model confidence 0.43*

| Token | Proposed label |
|---|---|
| `2400` | AddressNumber |
| `HIDDEN` | StreetName |
| `TRAIL` | PlaceName |
| `CT` | StateName |
| `28105` | ZipCode |
| `MATTHEWS` | PlaceName |
| `NC` | StateName |
| `28105` | ZipCode |

**Your answer:** `      `

---

## 42. `PSC 808 BOX 522 FPO AE 09618`
*TX · model confidence 0.43*

| Token | Proposed label |
|---|---|
| `PSC` | USPSBoxType |
| `808` | USPSBoxID |
| `BOX` | USPSBoxType |
| `522` | USPSBoxID |
| `FPO` | PlaceName |
| `AE` | StateName |
| `09618` | ZipCode |

**Your answer:** `      `

---

## 43. `MARGARET CLIFTON PARK NY 12065`
*MA · model confidence 0.44*

| Token | Proposed label |
|---|---|
| `MARGARET` | PlaceName |
| `CLIFTON` | PlaceName |
| `PARK` | PlaceName |
| `NY` | StateName |
| `12065` | ZipCode |

**Your answer:** `      `

---

## 44. `C/O SHERRY LINDLEY 7 CALLE ESTRIBO RSM CA 92688-1965`
*MT · model confidence 0.44*

| Token | Proposed label |
|---|---|
| `C/O` | Recipient |
| `SHERRY` | Recipient |
| `LINDLEY` | Recipient |
| `7` | Recipient |
| `CALLE` | Recipient |
| `ESTRIBO` | Recipient |
| `RSM` | PlaceName |
| `CA` | StateName |
| `92688-1965` | ZipCode |

**Your answer:** `      `

---

## 45. `10 PONY RUN 08080`
*NJ · model confidence 0.44*

| Token | Proposed label |
|---|---|
| `10` | AddressNumber |
| `PONY` | StreetName |
| `RUN` | StreetNamePostType |
| `08080` | ZipCode |

**Your answer:** `      `

---

## 46. `701 HIGHGATE ROAD ST ALBANS VT 05478`
*VT · model confidence 0.44*

| Token | Proposed label |
|---|---|
| `701` | AddressNumber |
| `HIGHGATE` | StreetName |
| `ROAD` | StreetName |
| `ST` | StreetNamePostType |
| `ALBANS` | PlaceName |
| `VT` | StateName |
| `05478` | ZipCode |

**Your answer:** `      `

---

## 47. `611 HEARNE FARM RD MT GILEAD NC 27306`
*NC · model confidence 0.44*

| Token | Proposed label |
|---|---|
| `611` | AddressNumber |
| `HEARNE` | StreetName |
| `FARM` | StreetName |
| `RD` | StreetName |
| `MT` | StreetNamePostType |
| `GILEAD` | PlaceName |
| `NC` | StateName |
| `27306` | ZipCode |

**Your answer:** `      `

---

## 48. `921 A 28TH AVE S 98144`
*WA · model confidence 0.44*

| Token | Proposed label |
|---|---|
| `921` | AddressNumber |
| `A` | StreetName |
| `28TH` | StreetName |
| `AVE` | StreetNamePostType |
| `S` | StreetNamePostDirectional |
| `98144` | ZipCode |

**Your answer:** `      `

---

## 49. `3565 W CALLE CINCO GREEN VALLEY AZ 85622-5369`
*AZ · model confidence 0.44*

| Token | Proposed label |
|---|---|
| `3565` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `CINCO` | PlaceName |
| `GREEN` | PlaceName |
| `VALLEY` | PlaceName |
| `AZ` | StateName |
| `85622-5369` | ZipCode |

**Your answer:** `      `

---

## 50. `639 PARKERTOWN RD MT GILEAD NC 27306`
*NC · model confidence 0.44*

| Token | Proposed label |
|---|---|
| `639` | AddressNumber |
| `PARKERTOWN` | StreetName |
| `RD` | StreetNamePostType |
| `MT` | PlaceName |
| `GILEAD` | PlaceName |
| `NC` | StateName |
| `27306` | ZipCode |

**Your answer:** `      `

---

## 51. `20 WEST ST BOSTON MA 02111`
*MA · model confidence 0.44*

| Token | Proposed label |
|---|---|
| `20` | AddressNumber |
| `WEST` | StreetName |
| `ST` | StreetNamePostType |
| `BOSTON` | PlaceName |
| `MA` | StateName |
| `02111` | ZipCode |

**Your answer:** `      `

---

## 52. `33RD ST 8TH AVE NEW YORK NY 10099`
*MA · model confidence 0.45*

| Token | Proposed label |
|---|---|
| `33RD` | AddressNumber |
| `ST` | StreetNamePreDirectional |
| `8TH` | StreetName |
| `AVE` | StreetNamePostType |
| `NEW` | PlaceName |
| `YORK` | PlaceName |
| `NY` | StateName |
| `10099` | ZipCode |

**Your answer:** `      `

---

## 53. `532 PROTER ST 28208 CHARLOTTE NC 28208`
*NC · model confidence 0.45*

| Token | Proposed label |
|---|---|
| `532` | AddressNumber |
| `PROTER` | StreetName |
| `ST` | StreetNamePostType |
| `28208` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28208` | ZipCode |

**Your answer:** `      `

---

## 54. `13128 ROVER ST 28273 CHARLOTTE NC 28273`
*NC · model confidence 0.45*

| Token | Proposed label |
|---|---|
| `13128` | AddressNumber |
| `ROVER` | StreetName |
| `ST` | StreetNamePostType |
| `28273` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28273` | ZipCode |

**Your answer:** `      `

---

## 55. `727 BROOKLYN MOUNTAIN RD 07843`
*NJ · model confidence 0.45*

| Token | Proposed label |
|---|---|
| `727` | AddressNumber |
| `BROOKLYN` | StreetName |
| `MOUNTAIN` | StreetName |
| `RD` | StreetNamePostType |
| `07843` | ZipCode |

**Your answer:** `      `

---

## 56. `13459 HIGGS CT 20171 HERNDON VA 20171`
*NC · model confidence 0.45*

| Token | Proposed label |
|---|---|
| `13459` | AddressNumber |
| `HIGGS` | StreetName |
| `CT` | StreetNamePostType |
| `20171` | OccupancyIdentifier |
| `HERNDON` | PlaceName |
| `VA` | StateName |
| `20171` | ZipCode |

**Your answer:** `      `

---

## 57. `1626 OAK ST LA CROSSE WI 54603`
*ND · model confidence 0.46*

| Token | Proposed label |
|---|---|
| `1626` | AddressNumber |
| `OAK` | StreetName |
| `ST` | StreetName |
| `LA` | StreetNamePostType |
| `CROSSE` | PlaceName |
| `WI` | StateName |
| `54603` | ZipCode |

**Your answer:** `      `

---

## 58. `1700 E ELM EL RENO OK 73036-0000`
*OK · model confidence 0.46*

| Token | Proposed label |
|---|---|
| `1700` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `ELM` | StreetName |
| `EL` | PlaceName |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036-0000` | ZipCode |

**Your answer:** `      `

---

## 59. `10805 SW 44TH ST B MUSTANG OK 73064`
*OK · model confidence 0.46*

| Token | Proposed label |
|---|---|
| `10805` | AddressNumber |
| `SW` | StreetNamePreDirectional |
| `44TH` | StreetName |
| `ST` | StreetNamePostType |
| `B` | OccupancyIdentifier |
| `MUSTANG` | PlaceName |
| `OK` | StateName |
| `73064` | ZipCode |

**Your answer:** `      `

---

## 60. `8557 S 102ND ST LA VISTA NE 68128`
*NE · model confidence 0.46*

| Token | Proposed label |
|---|---|
| `8557` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `102ND` | StreetName |
| `ST` | PlaceName |
| `LA` | PlaceName |
| `VISTA` | PlaceName |
| `NE` | StateName |
| `68128` | ZipCode |

**Your answer:** `      `

---

## 61. `8628 S 102ND ST LA VISTA NE 68128`
*NE · model confidence 0.46*

| Token | Proposed label |
|---|---|
| `8628` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `102ND` | StreetName |
| `ST` | PlaceName |
| `LA` | PlaceName |
| `VISTA` | PlaceName |
| `NE` | StateName |
| `68128` | ZipCode |

**Your answer:** `      `

---

## 62. `8101 S 103RD ST LA VISTA NE 68128`
*NE · model confidence 0.46*

| Token | Proposed label |
|---|---|
| `8101` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `103RD` | StreetName |
| `ST` | PlaceName |
| `LA` | PlaceName |
| `VISTA` | PlaceName |
| `NE` | StateName |
| `68128` | ZipCode |

**Your answer:** `      `

---

## 63. `52 SHORTILL FARMS RD 52 SHORTILL FARMS BUXTON ME`
*ME · model confidence 0.46*

| Token | Proposed label |
|---|---|
| `52` | AddressNumber |
| `SHORTILL` | StreetName |
| `FARMS` | StreetName |
| `RD` | StreetNamePostType |
| `52` | OccupancyIdentifier |
| `SHORTILL` | PlaceName |
| `FARMS` | PlaceName |
| `BUXTON` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 64. `4755 N PASEO DEL SUENO TUCSON AZ 85745-8908`
*AZ · model confidence 0.46*

| Token | Proposed label |
|---|---|
| `4755` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `PASEO` | StreetName |
| `DEL` | StreetName |
| `SUENO` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-8908` | ZipCode |

**Your answer:** `      `

---

## 65. `14 PONY RUN 08080`
*NJ · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `14` | AddressNumber |
| `PONY` | StreetName |
| `RUN` | StreetNamePostType |
| `08080` | ZipCode |

**Your answer:** `      `

---

## 66. `11250 NW 50 TER MIAMI FL 0`
*FL · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `11250` | AddressNumber |
| `NW` | StreetNamePreDirectional |
| `50` | StreetName |
| `TER` | StreetNamePostType |
| `MIAMI` | PlaceName |
| `FL` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 67. `115 COLLEGE ST 28134 PINEVILLE NC 28134`
*NC · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `115` | AddressNumber |
| `COLLEGE` | StreetName |
| `ST` | StreetNamePostType |
| `28134` | OccupancyIdentifier |
| `PINEVILLE` | PlaceName |
| `NC` | StateName |
| `28134` | ZipCode |

**Your answer:** `      `

---

## 68. `0 FLYING POINT ROAD 10 JOHN A ANDREW STREET JAMAICA PLAIN MA`
*ME · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `0` | AddressNumber |
| `FLYING` | StreetNamePreType |
| `POINT` | StreetNamePreType |
| `ROAD` | StreetNamePreType |
| `10` | StreetName |
| `JOHN` | StreetName |
| `A` | StreetName |
| `ANDREW` | StreetName |
| `STREET` | StreetNamePostType |
| `JAMAICA` | PlaceName |
| `PLAIN` | PlaceName |
| `MA` | StateName |

**Your answer:** `      `

---

## 69. `15104 SW 30 TER MIAMI FL 0`
*FL · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `15104` | AddressNumber |
| `SW` | StreetNamePreDirectional |
| `30` | StreetName |
| `TER` | StreetNamePostType |
| `MIAMI` | PlaceName |
| `FL` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 70. `3814 SW 331ST 98003`
*WA · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `3814` | AddressNumber |
| `SW` | StreetNamePreDirectional |
| `331ST` | StreetName |
| `98003` | ZipCode |

**Your answer:** `      `

---

## 71. `3 BEACON HEATH FARMINGTON CT 06032`
*CT · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `3` | AddressNumber |
| `BEACON` | StreetName |
| `HEATH` | StreetName |
| `FARMINGTON` | PlaceName |
| `CT` | StateName |
| `06032` | ZipCode |

**Your answer:** `      `

---

## 72. `9181 E PLACITA VIOLETA TUSCON AZ 857499221`
*CO · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `9181` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `PLACITA` | StreetName |
| `VIOLETA` | StreetName |
| `TUSCON` | PlaceName |
| `AZ` | StateName |
| `857499221` | ZipCode |

**Your answer:** `      `

---

## 73. `2141 NW 47 TERR MIAMI FL 33142`
*FL · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `2141` | AddressNumber |
| `NW` | StreetNamePreDirectional |
| `47` | StreetName |
| `TERR` | StreetNamePostType |
| `MIAMI` | PlaceName |
| `FL` | StateName |
| `33142` | ZipCode |

**Your answer:** `      `

---

## 74. `14427 NW 88 CT MIAMI LAKES FL 0`
*FL · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `14427` | AddressNumber |
| `NW` | StreetNamePreDirectional |
| `88` | StreetName |
| `CT` | StreetNamePostType |
| `MIAMI` | PlaceName |
| `LAKES` | PlaceName |
| `FL` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 75. `19366 SANTA BARBARA DETROIT MI 48221`
*MI · model confidence 0.47*

| Token | Proposed label |
|---|---|
| `19366` | AddressNumber |
| `SANTA` | StreetName |
| `BARBARA` | StreetName |
| `DETROIT` | PlaceName |
| `MI` | StateName |
| `48221` | ZipCode |

**Your answer:** `      `

---

## 76. `PO BOX 41 E BARRE VT 05649-0041`
*VT · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `41` | USPSBoxID |
| `E` | StreetNamePostDirectional |
| `BARRE` | PlaceName |
| `VT` | StateName |
| `05649-0041` | ZipCode |

**Your answer:** `      `

---

## 77. `PO BOX 15 E BARRE VT 05649-0015`
*VT · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `15` | USPSBoxID |
| `E` | StreetNamePostDirectional |
| `BARRE` | PlaceName |
| `VT` | StateName |
| `05649-0015` | ZipCode |

**Your answer:** `      `

---

## 78. `203 GLEN HEATHER PEACHTREE CTY GA 30269`
*NC · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `203` | AddressNumber |
| `GLEN` | StreetName |
| `HEATHER` | StreetName |
| `PEACHTREE` | StreetName |
| `CTY` | PlaceName |
| `GA` | StateName |
| `30269` | ZipCode |

**Your answer:** `      `

---

## 79. `8710 NE 139TH ST 98034`
*WA · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `8710` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `139TH` | StreetName |
| `ST` | StreetNamePostType |
| `98034` | ZipCode |

**Your answer:** `      `

---

## 80. `15304 NE 201ST ST 98072`
*WA · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `15304` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `201ST` | StreetName |
| `ST` | StreetNamePostType |
| `98072` | ZipCode |

**Your answer:** `      `

---

## 81. `18256 NE 111TH ST 98052`
*WA · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `18256` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `111TH` | StreetName |
| `ST` | StreetNamePostType |
| `98052` | ZipCode |

**Your answer:** `      `

---

## 82. `18316 NE 111TH ST 98052`
*WA · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `18316` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `111TH` | StreetName |
| `ST` | StreetNamePostType |
| `98052` | ZipCode |

**Your answer:** `      `

---

## 83. `7817 NE 112TH ST 98034`
*WA · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `7817` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `112TH` | StreetName |
| `ST` | StreetNamePostType |
| `98034` | ZipCode |

**Your answer:** `      `

---

## 84. `3601 NE 195TH ST 98155`
*WA · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `3601` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `195TH` | StreetName |
| `ST` | StreetNamePostType |
| `98155` | ZipCode |

**Your answer:** `      `

---

## 85. `512 E NEW YORK ST RAPID CITY SD 57701-1638`
*SD · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `512` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `NEW` | StreetName |
| `YORK` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-1638` | ZipCode |

**Your answer:** `      `

---

## 86. `1710 STATE HWY 14 NORTH GOLDEN NM 870479648`
*NM · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `1710` | AddressNumber |
| `STATE` | StreetNamePreType |
| `HWY` | StreetNamePreType |
| `14` | StreetName |
| `NORTH` | PlaceName |
| `GOLDEN` | PlaceName |
| `NM` | StateName |
| `870479648` | ZipCode |

**Your answer:** `      `

---

## 87. `115 TREADWELL ACRES HERMON ME`
*ME · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `115` | AddressNumber |
| `TREADWELL` | StreetName |
| `ACRES` | PlaceName |
| `HERMON` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 88. `626 SW 302ND ST 98023`
*WA · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `626` | AddressNumber |
| `SW` | StreetNamePreDirectional |
| `302ND` | StreetName |
| `ST` | StreetNamePostType |
| `98023` | ZipCode |

**Your answer:** `      `

---

## 89. `3714 SW 330TH ST 98023`
*WA · model confidence 0.48*

| Token | Proposed label |
|---|---|
| `3714` | AddressNumber |
| `SW` | StreetNamePreDirectional |
| `330TH` | StreetName |
| `ST` | StreetNamePostType |
| `98023` | ZipCode |

**Your answer:** `      `

---

## 90. `FORREST PARK ROAD MADISON TN 37115`
*TN · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `FORREST` | AddressNumber |
| `PARK` | StreetName |
| `ROAD` | StreetNamePostType |
| `MADISON` | PlaceName |
| `TN` | StateName |
| `37115` | ZipCode |

**Your answer:** `      `

---

## 91. `11401 NE 103RD ST 98033`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `11401` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `103RD` | StreetName |
| `ST` | StreetNamePostType |
| `98033` | ZipCode |

**Your answer:** `      `

---

## 92. `11905 FDR ROAD 228 LIBBY MT 59923`
*MT · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `11905` | AddressNumber |
| `FDR` | StreetNamePreType |
| `ROAD` | StreetNamePreType |
| `228` | StreetName |
| `LIBBY` | PlaceName |
| `MT` | StateName |
| `59923` | ZipCode |

**Your answer:** `      `

---

## 93. `24515 SE 146TH ST 98027`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `24515` | AddressNumber |
| `SE` | StreetNamePreDirectional |
| `146TH` | StreetName |
| `ST` | StreetNamePostType |
| `98027` | ZipCode |

**Your answer:** `      `

---

## 94. `9 B ARROYO GRIEGO SANTA FE NM 87506`
*NM · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `9` | AddressNumber |
| `B` | AddressNumberSuffix |
| `ARROYO` | StreetName |
| `GRIEGO` | StreetName |
| `SANTA` | PlaceName |
| `FE` | PlaceName |
| `NM` | StateName |
| `87506` | ZipCode |

**Your answer:** `      `

---

## 95. `5436 S 150TH ST 98188`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `5436` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `150TH` | StreetName |
| `ST` | StreetNamePostType |
| `98188` | ZipCode |

**Your answer:** `      `

---

## 96. `6203 S 117TH ST 98178`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `6203` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `117TH` | StreetName |
| `ST` | StreetNamePostType |
| `98178` | ZipCode |

**Your answer:** `      `

---

## 97. `4221 S 184TH ST 98188`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `4221` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `184TH` | StreetName |
| `ST` | StreetNamePostType |
| `98188` | ZipCode |

**Your answer:** `      `

---

## 98. `853 S 327TH ST 98003`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `853` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `327TH` | StreetName |
| `ST` | StreetNamePostType |
| `98003` | ZipCode |

**Your answer:** `      `

---

## 99. `6228 S 119TH ST 98178`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `6228` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `119TH` | StreetName |
| `ST` | StreetNamePostType |
| `98178` | ZipCode |

**Your answer:** `      `

---

## 100. `ATTN REAL ESTATE 3 LINCOLN CENTER OAKBROOK TERR IL 60181`
*IL · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `ATTN` | Recipient |
| `REAL` | Recipient |
| `ESTATE` | Recipient |
| `3` | AddressNumber |
| `LINCOLN` | StreetName |
| `CENTER` | StreetNamePostType |
| `OAKBROOK` | PlaceName |
| `TERR` | PlaceName |
| `IL` | StateName |
| `60181` | ZipCode |

**Your answer:** `      `

---

## 101. `344 E CUSTER ST RAPID CITY SD 57701-1012`
*SD · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `344` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `CUSTER` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-1012` | ZipCode |

**Your answer:** `      `

---

## 102. `121 E NOWLIN ST RAPID CITY SD 57701-1003`
*SD · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `121` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `NOWLIN` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-1003` | ZipCode |

**Your answer:** `      `

---

## 103. `513 1ST ST W HUNTER ND 58048`
*ND · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `513` | AddressNumber |
| `1ST` | StreetName |
| `ST` | StreetNamePostType |
| `W` | StreetNamePostDirectional |
| `HUNTER` | PlaceName |
| `ND` | StateName |
| `58048` | ZipCode |

**Your answer:** `      `

---

## 104. `1103 7TH ST W TAYLOR TX 76574`
*TX · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `1103` | AddressNumber |
| `7TH` | StreetName |
| `ST` | StreetNamePostType |
| `W` | StreetNamePostDirectional |
| `TAYLOR` | PlaceName |
| `TX` | StateName |
| `76574` | ZipCode |

**Your answer:** `      `

---

## 105. `77 SOUTH ST GRANBY MA 01033`
*MA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `77` | AddressNumber |
| `SOUTH` | StreetNamePostDirectional |
| `ST` | PlaceName |
| `GRANBY` | PlaceName |
| `MA` | StateName |
| `01033` | ZipCode |

**Your answer:** `      `

---

## 106. `612 HERMAN ST RAPID CITY SD 57701-1531`
*SD · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `612` | AddressNumber |
| `HERMAN` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-1531` | ZipCode |

**Your answer:** `      `

---

## 107. `11928 SE 260TH PL 98030`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `11928` | AddressNumber |
| `SE` | StreetNamePreDirectional |
| `260TH` | StreetName |
| `PL` | StreetNamePostType |
| `98030` | ZipCode |

**Your answer:** `      `

---

## 108. `1415 RACINE ST RAPID CITY SD 57701`
*SD · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `1415` | AddressNumber |
| `RACINE` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701` | ZipCode |

**Your answer:** `      `

---

## 109. `1123 RACINE ST RAPID CITY SD 57701-1093`
*SD · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `1123` | AddressNumber |
| `RACINE` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-1093` | ZipCode |

**Your answer:** `      `

---

## 110. `1725 HERMAN ST RAPID CITY SD 57701`
*SD · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `1725` | AddressNumber |
| `HERMAN` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701` | ZipCode |

**Your answer:** `      `

---

## 111. `20650 NE 79TH ST 98053`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `20650` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `79TH` | StreetName |
| `ST` | StreetNamePostType |
| `98053` | ZipCode |

**Your answer:** `      `

---

## 112. `20530 NE 78TH ST 98053`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `20530` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `78TH` | StreetName |
| `ST` | StreetNamePostType |
| `98053` | ZipCode |

**Your answer:** `      `

---

## 113. `14535 NE 91ST ST 98052`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `14535` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `91ST` | StreetName |
| `ST` | StreetNamePostType |
| `98052` | ZipCode |

**Your answer:** `      `

---

## 114. `4416 NE 68TH ST 98115`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `4416` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `68TH` | StreetName |
| `ST` | StreetNamePostType |
| `98115` | ZipCode |

**Your answer:** `      `

---

## 115. `7701 NE 28TH ST 98039`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `7701` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `28TH` | StreetName |
| `ST` | StreetNamePostType |
| `98039` | ZipCode |

**Your answer:** `      `

---

## 116. `3801 NE 62ND ST 98115`
*WA · model confidence 0.49*

| Token | Proposed label |
|---|---|
| `3801` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `62ND` | StreetName |
| `ST` | StreetNamePostType |
| `98115` | ZipCode |

**Your answer:** `      `

---

## 117. `#300 PMB 187 FORT MYERS FL 33908`
*FL · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `#` | OccupancyIdentifier |
| `300` | OccupancyIdentifier |
| `PMB` | SubaddressType |
| `187` | SubaddressIdentifier |
| `FORT` | PlaceName |
| `MYERS` | PlaceName |
| `FL` | StateName |
| `33908` | ZipCode |

**Your answer:** `      `

---

## 118. `10226 SE 23RD ST 98004`
*WA · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `10226` | AddressNumber |
| `SE` | StreetNamePreDirectional |
| `23RD` | StreetName |
| `ST` | StreetNamePostType |
| `98004` | ZipCode |

**Your answer:** `      `

---

## 119. `26626 SE 31ST ST 98075`
*WA · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `26626` | AddressNumber |
| `SE` | StreetNamePreDirectional |
| `31ST` | StreetName |
| `ST` | StreetNamePostType |
| `98075` | ZipCode |

**Your answer:** `      `

---

## 120. `275 N 17TH ST 07003`
*NJ · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `275` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `17TH` | StreetName |
| `ST` | StreetNamePostType |
| `07003` | ZipCode |

**Your answer:** `      `

---

## 121. `1 GREEN ACRES SWANTON VT 05488`
*VT · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `1` | AddressNumber |
| `GREEN` | StreetName |
| `ACRES` | StreetName |
| `SWANTON` | PlaceName |
| `VT` | StateName |
| `05488` | ZipCode |

**Your answer:** `      `

---

## 122. `10018 SOUTHAMPTON COMMONS DR 28277 CHARLOTTE NC 28277`
*NC · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `10018` | AddressNumber |
| `SOUTHAMPTON` | StreetName |
| `COMMONS` | StreetName |
| `DR` | StreetNamePostType |
| `28277` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28277` | ZipCode |

**Your answer:** `      `

---

## 123. `5025 ISAAC DR 28216 CHARLOTTE NC 28216`
*NC · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `5025` | AddressNumber |
| `ISAAC` | StreetName |
| `DR` | StreetNamePostType |
| `28216` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28216` | ZipCode |

**Your answer:** `      `

---

## 124. `123 TOM WHEELER NORTH STONINGTON CT 6359`
*CT · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `123` | AddressNumber |
| `TOM` | StreetName |
| `WHEELER` | StreetName |
| `NORTH` | PlaceName |
| `STONINGTON` | PlaceName |
| `CT` | StateName |
| `6359` | ZipCode |

**Your answer:** `      `

---

## 125. `21415 CIVIC CENTER STE 209 SOUTHFIELD MI 48076`
*MI · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `21415` | AddressNumber |
| `CIVIC` | StreetName |
| `CENTER` | StreetName |
| `STE` | OccupancyType |
| `209` | OccupancyIdentifier |
| `SOUTHFIELD` | PlaceName |
| `MI` | StateName |
| `48076` | ZipCode |

**Your answer:** `      `

---

## 126. `HIGH SCHOOL BLDG EL RENO OK 73036-0000`
*OK · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `HIGH` | Recipient |
| `SCHOOL` | Recipient |
| `BLDG` | SubaddressType |
| `EL` | SubaddressIdentifier |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036-0000` | ZipCode |

**Your answer:** `      `

---

## 127. `5928 MT HIGHWAY 13 WOLF POINT MT 59201-9227`
*MT · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `5928` | AddressNumber |
| `MT` | StreetNamePreType |
| `HIGHWAY` | StreetNamePreType |
| `13` | StreetName |
| `WOLF` | StreetName |
| `POINT` | StreetName |
| `MT` | StreetNamePostType |
| `59201-9227` | ZipCode |

**Your answer:** `      `

---

## 128. `8212 GERA EMMA DR 28215 CHARLOTTE NC 28215`
*NC · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `8212` | AddressNumber |
| `GERA` | StreetName |
| `EMMA` | StreetName |
| `DR` | StreetNamePostType |
| `28215` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28215` | ZipCode |

**Your answer:** `      `

---

## 129. `3 LATIMER DR EAST LYME CT 06333`
*CT · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `3` | AddressNumber |
| `LATIMER` | StreetName |
| `DR` | StreetNamePostType |
| `EAST` | PlaceName |
| `LYME` | PlaceName |
| `CT` | StateName |
| `06333` | ZipCode |

**Your answer:** `      `

---

## 130. `700 ROUTE 32 NORTH FRANKLIN CT 06254`
*CT · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `700` | AddressNumber |
| `ROUTE` | StreetNamePreType |
| `32` | StreetName |
| `NORTH` | StreetNamePostDirectional |
| `FRANKLIN` | PlaceName |
| `CT` | StateName |
| `06254` | ZipCode |

**Your answer:** `      `

---

## 131. `720 SAINT ANNE ST RAPID CITY SD 57701-4670`
*SD · model confidence 0.50*

| Token | Proposed label |
|---|---|
| `720` | AddressNumber |
| `SAINT` | StreetName |
| `ANNE` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-4670` | ZipCode |

**Your answer:** `      `

---

## 132. `11233 LAUREL VIEW DR 28273 CHARLOTTE NC 28273`
*NC · model confidence 0.51*

| Token | Proposed label |
|---|---|
| `11233` | AddressNumber |
| `LAUREL` | StreetName |
| `VIEW` | StreetName |
| `DR` | StreetNamePostType |
| `28273` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28273` | ZipCode |

**Your answer:** `      `

---

## 133. `1213 QUEEN LYON CT 28205 CHARLOTTE NC 28205`
*NC · model confidence 0.51*

| Token | Proposed label |
|---|---|
| `1213` | AddressNumber |
| `QUEEN` | StreetName |
| `LYON` | StreetName |
| `CT` | StreetNamePostType |
| `28205` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28205` | ZipCode |

**Your answer:** `      `

---

## 134. `LINDA H 903 DON MIGUEL PL SANTA FE NM 87505`
*NM · model confidence 0.51*

| Token | Proposed label |
|---|---|
| `LINDA` | Recipient |
| `H` | Recipient |
| `903` | AddressNumber |
| `DON` | StreetName |
| `MIGUEL` | StreetName |
| `PL` | StreetNamePostType |
| `SANTA` | PlaceName |
| `FE` | PlaceName |
| `NM` | StateName |
| `87505` | ZipCode |

**Your answer:** `      `

---

## 135. `871 LONG PLAINS RD 6 LINCOLN AVE #B SCARBOROUGH ME`
*ME · model confidence 0.51*

| Token | Proposed label |
|---|---|
| `871` | AddressNumber |
| `LONG` | StreetName |
| `PLAINS` | StreetName |
| `RD` | StreetName |
| `6` | StreetName |
| `LINCOLN` | StreetName |
| `AVE` | StreetNamePostType |
| `#` | OccupancyIdentifier |
| `B` | OccupancyIdentifier |
| `SCARBOROUGH` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 136. `1225 NE 17TH WAY FORT LAUDERDALE FL 33304`
*OH · model confidence 0.51*

| Token | Proposed label |
|---|---|
| `1225` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `17TH` | StreetName |
| `WAY` | StreetNamePostType |
| `FORT` | PlaceName |
| `LAUDERDALE` | PlaceName |
| `FL` | StateName |
| `33304` | ZipCode |

**Your answer:** `      `

---

## 137. `502 BOX ELDER RD W BOX ELDER SD 57719-9583`
*SD · model confidence 0.51*

| Token | Proposed label |
|---|---|
| `502` | AddressNumber |
| `BOX` | StreetName |
| `ELDER` | StreetName |
| `RD` | StreetNamePostType |
| `W` | PlaceName |
| `BOX` | PlaceName |
| `ELDER` | PlaceName |
| `SD` | StateName |
| `57719-9583` | ZipCode |

**Your answer:** `      `

---

## 138. `2108 E SW 59TH ST MUSTANG OK 73064-`
*OK · model confidence 0.51*

| Token | Proposed label |
|---|---|
| `2108` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `SW` | StreetNamePreType |
| `59TH` | StreetName |
| `ST` | StreetNamePostType |
| `MUSTANG` | PlaceName |
| `OK` | StateName |
| `73064-` | ZipCode |

**Your answer:** `      `

---

## 139. `4237 SEVERSON ST RAPID CITY SD 57702`
*SD · model confidence 0.51*

| Token | Proposed label |
|---|---|
| `4237` | AddressNumber |
| `SEVERSON` | StreetName |
| `ST` | PlaceName |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57702` | ZipCode |

**Your answer:** `      `

---

## 140. `1570 N LACROSSE ST RAPID CITY SD 57701-6963`
*SD · model confidence 0.51*

| Token | Proposed label |
|---|---|
| `1570` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `LACROSSE` | StreetName |
| `ST` | PlaceName |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-6963` | ZipCode |

**Your answer:** `      `

---

## 141. `110 E MADISON ST RAPID CITY SD 57701`
*SD · model confidence 0.52*

| Token | Proposed label |
|---|---|
| `110` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `MADISON` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701` | ZipCode |

**Your answer:** `      `

---

## 142. `4201 HALL ST RAPID CITY SD 57702-2234`
*SD · model confidence 0.52*

| Token | Proposed label |
|---|---|
| `4201` | AddressNumber |
| `HALL` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57702-2234` | ZipCode |

**Your answer:** `      `

---

## 143. `7427 S 97TH ST LA VISTA NE 68128`
*NE · model confidence 0.52*

| Token | Proposed label |
|---|---|
| `7427` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `97TH` | StreetName |
| `ST` | PlaceName |
| `LA` | PlaceName |
| `VISTA` | PlaceName |
| `NE` | StateName |
| `68128` | ZipCode |

**Your answer:** `      `

---

## 144. `320 E ADAMS ST RAPID CITY SD 57701`
*SD · model confidence 0.52*

| Token | Proposed label |
|---|---|
| `320` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `ADAMS` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701` | ZipCode |

**Your answer:** `      `

---

## 145. `1 DARROWS RIDGE ROAD EAST LYME CT 6333`
*CT · model confidence 0.52*

| Token | Proposed label |
|---|---|
| `1` | AddressNumber |
| `DARROWS` | StreetName |
| `RIDGE` | StreetName |
| `ROAD` | StreetNamePostType |
| `EAST` | NotAddress |
| `LYME` | NotAddress |
| `CT` | NotAddress |
| `6333` | OccupancyIdentifier |

**Your answer:** `      `

---

## 146. `4 A ARROYO GRIEGO RD SANTA FE NM 87501-1006`
*NM · model confidence 0.52*

| Token | Proposed label |
|---|---|
| `4` | AddressNumber |
| `A` | StreetName |
| `ARROYO` | StreetName |
| `GRIEGO` | StreetName |
| `RD` | StreetNamePostType |
| `SANTA` | PlaceName |
| `FE` | PlaceName |
| `NM` | StateName |
| `87501-1006` | ZipCode |

**Your answer:** `      `

---

## 147. `1206 DOWNING ST RAPID CITY SD 57701-0774`
*SD · model confidence 0.52*

| Token | Proposed label |
|---|---|
| `1206` | AddressNumber |
| `DOWNING` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-0774` | ZipCode |

**Your answer:** `      `

---

## 148. `1416 DOWNING ST RAPID CITY SD 57701-0737`
*SD · model confidence 0.52*

| Token | Proposed label |
|---|---|
| `1416` | AddressNumber |
| `DOWNING` | StreetName |
| `ST` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-0737` | ZipCode |

**Your answer:** `      `

---

## 149. `11730 SW 188 ST MIAMI FL 0`
*FL · model confidence 0.53*

| Token | Proposed label |
|---|---|
| `11730` | AddressNumber |
| `SW` | StreetNamePostDirectional |
| `188` | OccupancyIdentifier |
| `ST` | PlaceName |
| `MIAMI` | PlaceName |
| `FL` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 150. `10 STONEWALL CIRCLE WEST HARRISON NY 10604`
*VT · model confidence 0.53*

| Token | Proposed label |
|---|---|
| `10` | AddressNumber |
| `STONEWALL` | StreetName |
| `CIRCLE` | StreetNamePostType |
| `WEST` | StreetNamePostDirectional |
| `HARRISON` | PlaceName |
| `NY` | StateName |
| `10604` | ZipCode |

**Your answer:** `      `

---

## 151. `2504 CAMINO ENTRADA SANTA FE NM 87507-4851`
*NM · model confidence 0.53*

| Token | Proposed label |
|---|---|
| `2504` | AddressNumber |
| `CAMINO` | StreetNamePreType |
| `ENTRADA` | StreetName |
| `SANTA` | PlaceName |
| `FE` | PlaceName |
| `NM` | StateName |
| `87507-4851` | ZipCode |

**Your answer:** `      `

---

## 152. `PO BOX 442 WHT SPHR SPGS MT 59645-0442`
*MT · model confidence 0.53*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `442` | USPSBoxID |
| `WHT` | PlaceName |
| `SPHR` | PlaceName |
| `SPGS` | PlaceName |
| `MT` | StateName |
| `59645-0442` | ZipCode |

**Your answer:** `      `

---

## 153. `712 S WILLIAMS EL RENO OK 73036`
*OK · model confidence 0.53*

| Token | Proposed label |
|---|---|
| `712` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `WILLIAMS` | StreetName |
| `EL` | PlaceName |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036` | ZipCode |

**Your answer:** `      `

---

## 154. `21 WALKER STREET GLOUCESTER MA 01930 0000`
*MA · model confidence 0.54*

| Token | Proposed label |
|---|---|
| `21` | AddressNumber |
| `WALKER` | StreetName |
| `STREET` | StreetNamePostType |
| `GLOUCESTER` | PlaceName |
| `MA` | StateName |
| `01930` | ZipCode |
| `0000` | ZipPlus4 |

**Your answer:** `      `

---

## 155. `5030 A SAND POINT PL NE 98105`
*WA · model confidence 0.54*

| Token | Proposed label |
|---|---|
| `5030` | AddressNumber |
| `A` | AddressNumberSuffix |
| `SAND` | StreetName |
| `POINT` | StreetName |
| `PL` | StreetNamePostType |
| `NE` | StreetNamePostDirectional |
| `98105` | ZipCode |

**Your answer:** `      `

---

## 156. `6613 NE 1ST ST 98059`
*WA · model confidence 0.54*

| Token | Proposed label |
|---|---|
| `6613` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `1ST` | StreetName |
| `ST` | PlaceName |
| `98059` | ZipCode |

**Your answer:** `      `

---

## 157. `4770 VIENTO DEL NORTE SANTA FE NM 87507-0866`
*NM · model confidence 0.54*

| Token | Proposed label |
|---|---|
| `4770` | AddressNumber |
| `VIENTO` | StreetName |
| `DEL` | StreetName |
| `NORTE` | StreetName |
| `SANTA` | PlaceName |
| `FE` | PlaceName |
| `NM` | StateName |
| `87507-0866` | ZipCode |

**Your answer:** `      `

---

## 158. `16011 SE 8TH ST 98004`
*WA · model confidence 0.54*

| Token | Proposed label |
|---|---|
| `16011` | AddressNumber |
| `SE` | StreetNamePreDirectional |
| `8TH` | StreetName |
| `ST` | PlaceName |
| `98004` | ZipCode |

**Your answer:** `      `

---

## 159. `2110 E CIRCULO SOLAZ TUCSON AZ 85718-1153`
*AZ · model confidence 0.54*

| Token | Proposed label |
|---|---|
| `2110` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `CIRCULO` | StreetName |
| `SOLAZ` | PlaceName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85718-1153` | ZipCode |

**Your answer:** `      `

---

## 160. `2227 E LAKE WASHINGTON BV 98112`
*WA · model confidence 0.54*

| Token | Proposed label |
|---|---|
| `2227` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `LAKE` | StreetName |
| `WASHINGTON` | PlaceName |
| `BV` | StateName |
| `98112` | ZipCode |

**Your answer:** `      `

---

## 161. `570 E 260 ST EUCLID OH 44132`
*OH · model confidence 0.54*

| Token | Proposed label |
|---|---|
| `570` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `260` | StreetName |
| `ST` | StreetNamePostType |
| `EUCLID` | PlaceName |
| `OH` | StateName |
| `44132` | ZipCode |

**Your answer:** `      `

---

## 162. `4738 VIENTO DEL NORTE SANTA FE NM 87507-0866`
*NM · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `4738` | AddressNumber |
| `VIENTO` | StreetName |
| `DEL` | StreetName |
| `NORTE` | StreetName |
| `SANTA` | PlaceName |
| `FE` | PlaceName |
| `NM` | StateName |
| `87507-0866` | ZipCode |

**Your answer:** `      `

---

## 163. `111 JACKSON ST FORT MILL SC 29715`
*SC · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `111` | AddressNumber |
| `JACKSON` | StreetName |
| `ST` | StreetNamePostType |
| `FORT` | PlaceName |
| `MILL` | PlaceName |
| `SC` | StateName |
| `29715` | ZipCode |

**Your answer:** `      `

---

## 164. `1427 NFS 566F RD LIBBY MT 59923-8570`
*MT · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `1427` | AddressNumber |
| `NFS` | StreetName |
| `566F` | StreetName |
| `RD` | StreetNamePostType |
| `LIBBY` | PlaceName |
| `MT` | StateName |
| `59923-8570` | ZipCode |

**Your answer:** `      `

---

## 165. `34 OLD EVERGREEN LANE 29585`
*NJ · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `34` | AddressNumber |
| `OLD` | StreetName |
| `EVERGREEN` | StreetName |
| `LANE` | StreetNamePostType |
| `29585` | ZipCode |

**Your answer:** `      `

---

## 166. `713 W CALLE SUR TUCSON AZ 85705-5327`
*AZ · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `713` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `SUR` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85705-5327` | ZipCode |

**Your answer:** `      `

---

## 167. `511 NC 87 REIDSVILLE NC 27320`
*NC · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `511` | AddressNumber |
| `NC` | StreetNamePreType |
| `87` | StreetName |
| `REIDSVILLE` | PlaceName |
| `NC` | StateName |
| `27320` | ZipCode |

**Your answer:** `      `

---

## 168. `209 TILLERY LN MT GILEAD NC 27306`
*NC · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `209` | AddressNumber |
| `TILLERY` | StreetName |
| `LN` | StreetName |
| `MT` | StreetNamePostType |
| `GILEAD` | PlaceName |
| `NC` | StateName |
| `27306` | ZipCode |

**Your answer:** `      `

---

## 169. `1192 AVENIDA GANDARA RIO RICO AZ 85648-3317`
*AZ · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `1192` | AddressNumber |
| `AVENIDA` | StreetName |
| `GANDARA` | StreetName |
| `RIO` | PlaceName |
| `RICO` | PlaceName |
| `AZ` | StateName |
| `85648-3317` | ZipCode |

**Your answer:** `      `

---

## 170. `1317 DONELSON AVE OLD HICKORY TN 37138`
*TN · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `1317` | AddressNumber |
| `DONELSON` | StreetName |
| `AVE` | StreetNamePostType |
| `OLD` | StreetNamePreModifier |
| `HICKORY` | PlaceName |
| `TN` | StateName |
| `37138` | ZipCode |

**Your answer:** `      `

---

## 171. `18 ANDREW DRIVELANE CANTON CT 06019`
*CT · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `18` | AddressNumber |
| `ANDREW` | StreetName |
| `DRIVELANE` | StreetName |
| `CANTON` | PlaceName |
| `CT` | StateName |
| `06019` | ZipCode |

**Your answer:** `      `

---

## 172. `520 N MO HWY 7 INDEPENDENCE MO 64056`
*MO · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `520` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `MO` | StreetName |
| `HWY` | StreetNamePostType |
| `7` | OccupancyIdentifier |
| `INDEPENDENCE` | PlaceName |
| `MO` | StateName |
| `64056` | ZipCode |

**Your answer:** `      `

---

## 173. `4202 VIA DE VENTURA SANTA FE NM 87507-6305`
*NM · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `4202` | AddressNumber |
| `VIA` | StreetNamePreType |
| `DE` | StreetName |
| `VENTURA` | StreetName |
| `SANTA` | PlaceName |
| `FE` | PlaceName |
| `NM` | StateName |
| `87507-6305` | ZipCode |

**Your answer:** `      `

---

## 174. `74 STAPLES POINT ROAD SANDRA J BROWN (TRUSTEE) SOUTH FREEPORT ME`
*ME · model confidence 0.55*

| Token | Proposed label |
|---|---|
| `74` | AddressNumber |
| `STAPLES` | StreetName |
| `POINT` | StreetName |
| `ROAD` | StreetNamePostType |
| `SANDRA` | Recipient |
| `J` | Recipient |
| `BROWN` | Recipient |
| `(TRUSTEE)` | Recipient |
| `SOUTH` | Recipient |
| `FREEPORT` | Recipient |
| `ME` | Recipient |

**Your answer:** `      `

---

## 175. `6632 SANDALWOOD CLOSE ROCKFORD IL 61108`
*IL · model confidence 0.56*

| Token | Proposed label |
|---|---|
| `6632` | AddressNumber |
| `SANDALWOOD` | StreetName |
| `CLOSE` | PlaceName |
| `ROCKFORD` | PlaceName |
| `IL` | StateName |
| `61108` | ZipCode |

**Your answer:** `      `

---

## 176. `42 MARQUISE OAKS PLACE THE WOODLANDS TX 77382`
*MA · model confidence 0.56*

| Token | Proposed label |
|---|---|
| `42` | AddressNumber |
| `MARQUISE` | StreetName |
| `OAKS` | StreetName |
| `PLACE` | StreetNamePostType |
| `THE` | PlaceName |
| `WOODLANDS` | PlaceName |
| `TX` | StateName |
| `77382` | ZipCode |

**Your answer:** `      `

---

## 177. `813 Avenue C Fort Pierce FL 34950`
*FL · model confidence 0.56*

| Token | Proposed label |
|---|---|
| `813` | AddressNumber |
| `Avenue` | StreetNamePreType |
| `C` | StreetName |
| `Fort` | StreetNamePostType |
| `Pierce` | PlaceName |
| `FL` | StateName |
| `34950` | ZipCode |

**Your answer:** `      `

---

## 178. `18775 229TH ST WALL SD 57790-6104`
*SD · model confidence 0.56*

| Token | Proposed label |
|---|---|
| `18775` | AddressNumber |
| `229TH` | StreetName |
| `ST` | PlaceName |
| `WALL` | PlaceName |
| `SD` | StateName |
| `57790-6104` | ZipCode |

**Your answer:** `      `

---

## 179. `1107 CHILDS RD W BELLEVUE NE 68147`
*NE · model confidence 0.56*

| Token | Proposed label |
|---|---|
| `1107` | AddressNumber |
| `CHILDS` | StreetName |
| `RD` | StreetNamePostType |
| `W` | PlaceName |
| `BELLEVUE` | PlaceName |
| `NE` | StateName |
| `68147` | ZipCode |

**Your answer:** `      `

---

## 180. `140 NO 10TH STREET 19107`
*NJ · model confidence 0.56*

| Token | Proposed label |
|---|---|
| `140` | AddressNumber |
| `NO` | StreetNamePreDirectional |
| `10TH` | StreetName |
| `STREET` | StreetNamePostType |
| `19107` | ZipCode |

**Your answer:** `      `

---

## 181. `19423 NW 28 CT MIAMI GARDENS FL 0`
*FL · model confidence 0.56*

| Token | Proposed label |
|---|---|
| `19423` | AddressNumber |
| `NW` | StreetNamePreDirectional |
| `28` | StreetName |
| `CT` | StreetNamePostType |
| `MIAMI` | PlaceName |
| `GARDENS` | PlaceName |
| `FL` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 182. `99 Bedford ST, Unit Lbby 5 Boston MA 02111`
*MA · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `99` | AddressNumber |
| `Bedford` | StreetName |
| `ST,` | StreetNamePostType |
| `Unit` | OccupancyType |
| `Lbby` | SubaddressType |
| `5` | SubaddressIdentifier |
| `Boston` | PlaceName |
| `MA` | StateName |
| `02111` | ZipCode |

**Your answer:** `      `

---

## 183. `309 ATLANTIC AVENUE 081041013`
*NJ · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `309` | AddressNumber |
| `ATLANTIC` | StreetName |
| `AVENUE` | StreetNamePostType |
| `081041013` | ZipCode |

**Your answer:** `      `

---

## 184. `17 WAKE FOREST TR 07843`
*NJ · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `17` | AddressNumber |
| `WAKE` | StreetName |
| `FOREST` | PlaceName |
| `TR` | StateName |
| `07843` | ZipCode |

**Your answer:** `      `

---

## 185. `1 BOUL DE MAISONNEUVE OUEST PH20.01 MONTREAL, PQ CANADA 0`
*FL · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `1` | AddressNumber |
| `BOUL` | StreetName |
| `DE` | StreetName |
| `MAISONNEUVE` | StreetName |
| `OUEST` | StreetName |
| `PH20.01` | StreetName |
| `MONTREAL,` | PlaceName |
| `PQ` | StateName |
| `CANADA` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 186. `13063 VENTURA BLVD STE 200 ATTN MICHAEL THOM STUDIO CITY CA 91604-2237`
*IN · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `13063` | AddressNumber |
| `VENTURA` | StreetName |
| `BLVD` | StreetNamePostType |
| `STE` | OccupancyType |
| `200` | OccupancyIdentifier |
| `ATTN` | Recipient |
| `MICHAEL` | Recipient |
| `THOM` | Recipient |
| `STUDIO` | PlaceName |
| `CITY` | PlaceName |
| `CA` | StateName |
| `91604-2237` | ZipCode |

**Your answer:** `      `

---

## 187. `16 OAKDENE TERR UNIT A 07020`
*NJ · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `16` | AddressNumber |
| `OAKDENE` | StreetName |
| `TERR` | StreetNamePostType |
| `UNIT` | OccupancyType |
| `A` | OccupancyIdentifier |
| `07020` | ZipCode |

**Your answer:** `      `

---

## 188. `160 HILL RANCH RD W EDGEWOOD NM 87015-8097`
*NM · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `160` | AddressNumber |
| `HILL` | StreetName |
| `RANCH` | StreetName |
| `RD` | StreetNamePostType |
| `W` | PlaceName |
| `EDGEWOOD` | PlaceName |
| `NM` | StateName |
| `87015-8097` | ZipCode |

**Your answer:** `      `

---

## 189. `3312 STEAMRIDGE CT W ANTIOCH TN 37013`
*TN · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `3312` | AddressNumber |
| `STEAMRIDGE` | StreetName |
| `CT` | StreetNamePostType |
| `W` | StreetNamePostDirectional |
| `ANTIOCH` | PlaceName |
| `TN` | StateName |
| `37013` | ZipCode |

**Your answer:** `      `

---

## 190. `1730 CIRCULO BADAJADA RIO RICO AZ 85648-0000`
*AZ · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `1730` | AddressNumber |
| `CIRCULO` | StreetName |
| `BADAJADA` | StreetName |
| `RIO` | PlaceName |
| `RICO` | PlaceName |
| `AZ` | StateName |
| `85648-0000` | ZipCode |

**Your answer:** `      `

---

## 191. `8 CARLY CT 08090`
*NJ · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `8` | AddressNumber |
| `CARLY` | StreetName |
| `CT` | StreetNamePostType |
| `08090` | ZipCode |

**Your answer:** `      `

---

## 192. `11249 SE 315TH COURT 98092`
*WA · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `11249` | AddressNumber |
| `SE` | StreetNamePreDirectional |
| `315TH` | StreetName |
| `COURT` | StreetNamePostType |
| `98092` | ZipCode |

**Your answer:** `      `

---

## 193. `9804 GENTIAN D MACHESNEY PARK IL 61115`
*IL · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `9804` | AddressNumber |
| `GENTIAN` | StreetName |
| `D` | StreetNamePostType |
| `MACHESNEY` | PlaceName |
| `PARK` | PlaceName |
| `IL` | StateName |
| `61115` | ZipCode |

**Your answer:** `      `

---

## 194. `310 4TH ST LAKE PARK Florida 33403`
*FL · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `310` | AddressNumber |
| `4TH` | StreetName |
| `ST` | PlaceName |
| `LAKE` | PlaceName |
| `PARK` | PlaceName |
| `Florida` | StateName |
| `33403` | ZipCode |

**Your answer:** `      `

---

## 195. `262 US ROUTE ONE 145 LITCHFIELD ROAD HOLLOWELL ME`
*ME · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `262` | AddressNumber |
| `US` | StreetNamePreType |
| `ROUTE` | StreetNamePreType |
| `ONE` | StreetName |
| `145` | StreetName |
| `LITCHFIELD` | StreetName |
| `ROAD` | StreetNamePostType |
| `HOLLOWELL` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 196. `807 W CALLE ADELANTO TUCSON AZ 85705-6422`
*AZ · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `807` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `ADELANTO` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85705-6422` | ZipCode |

**Your answer:** `      `

---

## 197. `768 W CALLE ADELANTO TUCSON AZ 85705-6421`
*AZ · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `768` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `ADELANTO` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85705-6421` | ZipCode |

**Your answer:** `      `

---

## 198. `1932 W CALLE MECEDORA TUCSON AZ 85745-2125`
*AZ · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `1932` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `MECEDORA` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-2125` | ZipCode |

**Your answer:** `      `

---

## 199. `1935 W CALLE PACIFICA TUCSON AZ 85745-2118`
*AZ · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `1935` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `PACIFICA` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-2118` | ZipCode |

**Your answer:** `      `

---

## 200. `2231 SAHALEE DR EAST 98074`
*WA · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `2231` | AddressNumber |
| `SAHALEE` | StreetName |
| `DR` | StreetNamePostType |
| `EAST` | PlaceName |
| `98074` | ZipCode |

**Your answer:** `      `

---

## 201. `1010 WESTPORT PKWY WEST FARGO ND 58078`
*ND · model confidence 0.57*

| Token | Proposed label |
|---|---|
| `1010` | AddressNumber |
| `WESTPORT` | StreetName |
| `PKWY` | StreetNamePostType |
| `WEST` | PlaceName |
| `FARGO` | PlaceName |
| `ND` | StateName |
| `58078` | ZipCode |

**Your answer:** `      `

---

## 202. `966 SOUTH ST DALTON MA 01226`
*MA · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `966` | AddressNumber |
| `SOUTH` | StreetName |
| `ST` | StreetNamePostType |
| `DALTON` | PlaceName |
| `MA` | StateName |
| `01226` | ZipCode |

**Your answer:** `      `

---

## 203. `0 ROUTE 116 R5/1 P O BOX 189 LINCOLN ME`
*ME · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `0` | BuildingName |
| `ROUTE` | BuildingName |
| `116` | AddressNumber |
| `R5/1` | StreetName |
| `P` | USPSBoxType |
| `O` | USPSBoxType |
| `BOX` | USPSBoxType |
| `189` | USPSBoxID |
| `LINCOLN` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 204. `336 STEVENS STREET 081031130`
*NJ · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `336` | AddressNumber |
| `STEVENS` | StreetName |
| `STREET` | StreetNamePostType |
| `081031130` | ZipCode |

**Your answer:** `      `

---

## 205. `13461 NE 105TH CT 98033`
*WA · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `13461` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `105TH` | StreetName |
| `CT` | StreetNamePostType |
| `98033` | ZipCode |

**Your answer:** `      `

---

## 206. `18527 NE 102ND CT 98052`
*WA · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `18527` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `102ND` | StreetName |
| `CT` | StreetNamePostType |
| `98052` | ZipCode |

**Your answer:** `      `

---

## 207. `343 MECHANIC STREET 081041050`
*NJ · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `343` | AddressNumber |
| `MECHANIC` | StreetName |
| `STREET` | StreetNamePostType |
| `081041050` | ZipCode |

**Your answer:** `      `

---

## 208. `P O BOX 4900 C/O RYAN LLC SCOTTSDALE AZ 85261`
*TN · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `P` | USPSBoxType |
| `O` | USPSBoxType |
| `BOX` | USPSBoxType |
| `4900` | USPSBoxID |
| `C/O` | Recipient |
| `RYAN` | Recipient |
| `LLC` | Recipient |
| `SCOTTSDALE` | PlaceName |
| `AZ` | StateName |
| `85261` | ZipCode |

**Your answer:** `      `

---

## 209. `25 LONGWORTH AV U 6 BROCKTON MA 02301`
*MA · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `25` | AddressNumber |
| `LONGWORTH` | StreetName |
| `AV` | StreetNamePostType |
| `U` | OccupancyIdentifier |
| `6` | OccupancyIdentifier |
| `BROCKTON` | PlaceName |
| `MA` | StateName |
| `02301` | ZipCode |

**Your answer:** `      `

---

## 210. `12811 Griffing Blvd North Miami FL 33161`
*FL · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `12811` | AddressNumber |
| `Griffing` | StreetName |
| `Blvd` | StreetNamePostType |
| `North` | PlaceName |
| `Miami` | PlaceName |
| `FL` | StateName |
| `33161` | ZipCode |

**Your answer:** `      `

---

## 211. `5228 W OLD US 421 HWY HAMPTONVILLE NC 27020`
*NC · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `5228` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `OLD` | StreetName |
| `US` | StreetName |
| `421` | StreetName |
| `HWY` | StreetNamePostType |
| `HAMPTONVILLE` | PlaceName |
| `NC` | StateName |
| `27020` | ZipCode |

**Your answer:** `      `

---

## 212. `24785 VIA LAGUNARIA 92677`
*WA · model confidence 0.58*

| Token | Proposed label |
|---|---|
| `24785` | AddressNumber |
| `VIA` | StreetName |
| `LAGUNARIA` | PlaceName |
| `92677` | ZipCode |

**Your answer:** `      `

---

## 213. `19 BAY AVENUE EAST HULL MA 02045`
*MA · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `19` | AddressNumber |
| `BAY` | StreetName |
| `AVENUE` | StreetNamePostType |
| `EAST` | PlaceName |
| `HULL` | PlaceName |
| `MA` | StateName |
| `02045` | ZipCode |

**Your answer:** `      `

---

## 214. `1640 NIA RD 28215 CHARLOTTE NC 28215`
*NC · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `1640` | AddressNumber |
| `NIA` | StreetName |
| `RD` | StreetNamePostType |
| `28215` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28215` | ZipCode |

**Your answer:** `      `

---

## 215. `# 645 7362 W PARKS HWY WASILLA AK 99623`
*AK · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `#` | OccupancyIdentifier |
| `645` | OccupancyIdentifier |
| `7362` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `PARKS` | StreetName |
| `HWY` | StreetNamePostType |
| `WASILLA` | PlaceName |
| `AK` | StateName |
| `99623` | ZipCode |

**Your answer:** `      `

---

## 216. `405 N 21st ST Fort Pierce FL 34950`
*FL · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `405` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `21st` | StreetName |
| `ST` | PlaceName |
| `Fort` | PlaceName |
| `Pierce` | PlaceName |
| `FL` | StateName |
| `34950` | ZipCode |

**Your answer:** `      `

---

## 217. `E BROADWAY SOUTH BOSTON MA 02127`
*MA · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `E` | StreetNamePreDirectional |
| `BROADWAY` | StreetName |
| `SOUTH` | PlaceName |
| `BOSTON` | PlaceName |
| `MA` | StateName |
| `02127` | ZipCode |

**Your answer:** `      `

---

## 218. `6067 VT RTE 14 E CALAIS VT 05650`
*VT · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `6067` | AddressNumber |
| `VT` | StreetNamePreType |
| `RTE` | StreetNamePreType |
| `14` | StreetName |
| `E` | StreetNamePostDirectional |
| `CALAIS` | PlaceName |
| `VT` | StateName |
| `05650` | ZipCode |

**Your answer:** `      `

---

## 219. `3802 N 135TH ST W MAIZE KS 67101`
*KS · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `3802` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `135TH` | StreetName |
| `ST` | StreetNamePostType |
| `W` | StreetNamePostDirectional |
| `MAIZE` | PlaceName |
| `KS` | StateName |
| `67101` | ZipCode |

**Your answer:** `      `

---

## 220. `514 N 10th St Fort Pierce FL 34950`
*FL · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `514` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `10th` | StreetName |
| `St` | PlaceName |
| `Fort` | PlaceName |
| `Pierce` | PlaceName |
| `FL` | StateName |
| `34950` | ZipCode |

**Your answer:** `      `

---

## 221. `714 S 10th ST Fort Pierce FL 34950`
*FL · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `714` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `10th` | StreetName |
| `ST` | PlaceName |
| `Fort` | PlaceName |
| `Pierce` | PlaceName |
| `FL` | StateName |
| `34950` | ZipCode |

**Your answer:** `      `

---

## 222. `726 S 11th ST Fort Pierce FL 34950`
*FL · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `726` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `11th` | StreetName |
| `ST` | PlaceName |
| `Fort` | PlaceName |
| `Pierce` | PlaceName |
| `FL` | StateName |
| `34950` | ZipCode |

**Your answer:** `      `

---

## 223. `716 S 12th St Fort Pierce FL 34950`
*FL · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `716` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `12th` | StreetName |
| `St` | PlaceName |
| `Fort` | PlaceName |
| `Pierce` | PlaceName |
| `FL` | StateName |
| `34950` | ZipCode |

**Your answer:** `      `

---

## 224. `210 S 24th ST Fort Pierce FL 34950`
*FL · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `210` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `24th` | StreetName |
| `ST` | PlaceName |
| `Fort` | PlaceName |
| `Pierce` | PlaceName |
| `FL` | StateName |
| `34950` | ZipCode |

**Your answer:** `      `

---

## 225. `4127 SOUTHWEST 327TH PLACE 98023`
*WA · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `4127` | AddressNumber |
| `SOUTHWEST` | StreetNamePreDirectional |
| `327TH` | StreetName |
| `PLACE` | StreetNamePostType |
| `98023` | ZipCode |

**Your answer:** `      `

---

## 226. `390 MAIDEN CUTOFF LEWISTOWN MT 59457-8069`
*MT · model confidence 0.59*

| Token | Proposed label |
|---|---|
| `390` | AddressNumber |
| `MAIDEN` | StreetName |
| `CUTOFF` | StreetName |
| `LEWISTOWN` | PlaceName |
| `MT` | StateName |
| `59457-8069` | ZipCode |

**Your answer:** `      `

---

## 227. `16932 NW 10TH ST EL RENO OK 73036-9149`
*OK · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `16932` | AddressNumber |
| `NW` | StreetNamePreDirectional |
| `10TH` | StreetName |
| `ST` | StreetNamePostType |
| `EL` | PlaceName |
| `RENO` | PlaceName |
| `OK` | StateName |
| `73036-9149` | ZipCode |

**Your answer:** `      `

---

## 228. `5914 VANISHING TRAIL CT RAPID CITY SD 57702-8806`
*SD · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `5914` | AddressNumber |
| `VANISHING` | StreetName |
| `TRAIL` | StreetName |
| `CT` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57702-8806` | ZipCode |

**Your answer:** `      `

---

## 229. `111W W FORREST FEEZOR CORONA AZ 85641-2109`
*AZ · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `111W` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `FORREST` | StreetName |
| `FEEZOR` | StreetName |
| `CORONA` | PlaceName |
| `AZ` | StateName |
| `85641-2109` | ZipCode |

**Your answer:** `      `

---

## 230. `HOPKINS ROAD (DISC) 25 DW DRIVE CARMEL ME`
*ME · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `HOPKINS` | StreetName |
| `ROAD` | StreetNamePostType |
| `(DISC)` | SubaddressType |
| `25` | AddressNumber |
| `DW` | StreetName |
| `DRIVE` | StreetNamePostType |
| `CARMEL` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 231. `6 DOE CT 08080`
*NJ · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `6` | AddressNumber |
| `DOE` | StreetName |
| `CT` | StreetNamePostType |
| `08080` | ZipCode |

**Your answer:** `      `

---

## 232. `1900 AVE OF THE STARS STE 2475 LOS ANGELES CA 90067`
*NM · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `1900` | AddressNumber |
| `AVE` | StreetNamePreType |
| `OF` | StreetName |
| `THE` | StreetName |
| `STARS` | StreetName |
| `STE` | OccupancyType |
| `2475` | OccupancyIdentifier |
| `LOS` | PlaceName |
| `ANGELES` | PlaceName |
| `CA` | StateName |
| `90067` | ZipCode |

**Your answer:** `      `

---

## 233. `175 WOODLAND MEAD SOUTH HAMILTON MA 01982`
*MA · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `175` | AddressNumber |
| `WOODLAND` | StreetName |
| `MEAD` | StreetName |
| `SOUTH` | PlaceName |
| `HAMILTON` | PlaceName |
| `MA` | StateName |
| `01982` | ZipCode |

**Your answer:** `      `

---

## 234. `7341 PINON JAY CIR RAPID CITY SD 57702-9022`
*SD · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `7341` | AddressNumber |
| `PINON` | StreetName |
| `JAY` | StreetName |
| `CIR` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57702-9022` | ZipCode |

**Your answer:** `      `

---

## 235. `7361 PINON JAY CIR RAPID CITY SD 57702-9022`
*SD · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `7361` | AddressNumber |
| `PINON` | StreetName |
| `JAY` | StreetName |
| `CIR` | StreetNamePostType |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57702-9022` | ZipCode |

**Your answer:** `      `

---

## 236. `1129 VUELTA DE LAS ACEQUIAS SANTA FE NM 87507-7107`
*NM · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `1129` | AddressNumber |
| `VUELTA` | StreetName |
| `DE` | StreetName |
| `LAS` | StreetName |
| `ACEQUIAS` | StreetName |
| `SANTA` | PlaceName |
| `FE` | PlaceName |
| `NM` | StateName |
| `87507-7107` | ZipCode |

**Your answer:** `      `

---

## 237. `1347 W PLACITA BRONCE TUCSON AZ 85745-2730`
*AZ · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `1347` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `PLACITA` | StreetName |
| `BRONCE` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-2730` | ZipCode |

**Your answer:** `      `

---

## 238. `605 N AVENIDA ALEGRE TUCSON AZ 85745-2258`
*AZ · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `605` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `AVENIDA` | StreetName |
| `ALEGRE` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-2258` | ZipCode |

**Your answer:** `      `

---

## 239. `10725 SW 134 TERR MIAMI FL 33176`
*FL · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `10725` | AddressNumber |
| `SW` | StreetNamePreDirectional |
| `134` | StreetName |
| `TERR` | PlaceName |
| `MIAMI` | PlaceName |
| `FL` | StateName |
| `33176` | ZipCode |

**Your answer:** `      `

---

## 240. `4517 B 8TH AVE NE 98105`
*WA · model confidence 0.60*

| Token | Proposed label |
|---|---|
| `4517` | AddressNumber |
| `B` | StreetNamePreDirectional |
| `8TH` | StreetName |
| `AVE` | StreetNamePostType |
| `NE` | StreetNamePostDirectional |
| `98105` | ZipCode |

**Your answer:** `      `

---

## 241. `7508 TERRY DR LA VISTA NE 68128`
*NE · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `7508` | AddressNumber |
| `TERRY` | StreetName |
| `DR` | StreetNamePostType |
| `LA` | PlaceName |
| `VISTA` | PlaceName |
| `NE` | StateName |
| `68128` | ZipCode |

**Your answer:** `      `

---

## 242. `2810 SW MORGAN ST 98126`
*WA · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `2810` | AddressNumber |
| `SW` | StreetNamePostDirectional |
| `MORGAN` | PlaceName |
| `ST` | StateName |
| `98126` | ZipCode |

**Your answer:** `      `

---

## 243. `3230 SW MORGAN ST 98126`
*WA · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `3230` | AddressNumber |
| `SW` | StreetNamePostDirectional |
| `MORGAN` | PlaceName |
| `ST` | StateName |
| `98126` | ZipCode |

**Your answer:** `      `

---

## 244. `2312 27TH ST W BIRMINGHAM AL 35208-2815`
*AL · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `2312` | AddressNumber |
| `27TH` | StreetName |
| `ST` | StreetNamePostType |
| `W` | StreetNamePostDirectional |
| `BIRMINGHAM` | PlaceName |
| `AL` | StateName |
| `35208-2815` | ZipCode |

**Your answer:** `      `

---

## 245. `2100 31ST ST W BIRMINGHAM AL 35208-2710`
*AL · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `2100` | AddressNumber |
| `31ST` | StreetName |
| `ST` | StreetNamePostType |
| `W` | StreetNamePostDirectional |
| `BIRMINGHAM` | PlaceName |
| `AL` | StateName |
| `35208-2710` | ZipCode |

**Your answer:** `      `

---

## 246. `2937 CORONET WAY 28208 CHARLOTTE NC 28208`
*NC · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `2937` | AddressNumber |
| `CORONET` | StreetName |
| `WAY` | StreetNamePostType |
| `28208` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28208` | ZipCode |

**Your answer:** `      `

---

## 247. `526 W CALLE SIGLO TUCSON AZ 85705-2607`
*AZ · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `526` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `SIGLO` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85705-2607` | ZipCode |

**Your answer:** `      `

---

## 248. `1437 W CALLE PLOMO TUCSON AZ 85745-2767`
*AZ · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `1437` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `PLOMO` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-2767` | ZipCode |

**Your answer:** `      `

---

## 249. `1042 38 1/2 AVE W WEST FARGO ND 58078`
*ND · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `1042` | AddressNumber |
| `38` | StreetName |
| `1/2` | StreetName |
| `AVE` | StreetNamePostType |
| `W` | StreetNamePostDirectional |
| `WEST` | PlaceName |
| `FARGO` | PlaceName |
| `ND` | StateName |
| `58078` | ZipCode |

**Your answer:** `      `

---

## 250. `1625 34 1/2 AVE S FARGO ND 58104`
*ND · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `1625` | AddressNumber |
| `34` | StreetName |
| `1/2` | StreetName |
| `AVE` | StreetNamePostType |
| `S` | StreetNamePostDirectional |
| `FARGO` | PlaceName |
| `ND` | StateName |
| `58104` | ZipCode |

**Your answer:** `      `

---

## 251. `1 CLARKS FALLS NORTH STONINGTON CT 6359`
*CT · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `1` | AddressNumber |
| `CLARKS` | StreetName |
| `FALLS` | StreetNamePostType |
| `NORTH` | StreetNamePostDirectional |
| `STONINGTON` | PlaceName |
| `CT` | StateName |
| `6359` | ZipCode |

**Your answer:** `      `

---

## 252. `62 E CLARKS FALLS NORTH STONINGTON CT 6359`
*CT · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `62` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `CLARKS` | StreetName |
| `FALLS` | StreetNamePostType |
| `NORTH` | StreetNamePostDirectional |
| `STONINGTON` | PlaceName |
| `CT` | StateName |
| `6359` | ZipCode |

**Your answer:** `      `

---

## 253. `1825 DRY GULCH HELENA MT 59601`
*MT · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `1825` | AddressNumber |
| `DRY` | StreetName |
| `GULCH` | StreetName |
| `HELENA` | PlaceName |
| `MT` | StateName |
| `59601` | ZipCode |

**Your answer:** `      `

---

## 254. `2437 SANTA BARBARA LOOP ROUND ROCK TX 78665`
*TX · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `2437` | AddressNumber |
| `SANTA` | StreetName |
| `BARBARA` | StreetName |
| `LOOP` | StreetNamePostType |
| `ROUND` | PlaceName |
| `ROCK` | PlaceName |
| `TX` | StateName |
| `78665` | ZipCode |

**Your answer:** `      `

---

## 255. `2004 26TH ST W BIRMINGHAM AL 35211`
*AL · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `2004` | AddressNumber |
| `26TH` | StreetName |
| `ST` | StreetNamePostType |
| `W` | StreetNamePostDirectional |
| `BIRMINGHAM` | PlaceName |
| `AL` | StateName |
| `35211` | ZipCode |

**Your answer:** `      `

---

## 256. `9614 S 219TH PLACE 98031`
*WA · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `9614` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `219TH` | StreetName |
| `PLACE` | StreetNamePostType |
| `98031` | ZipCode |

**Your answer:** `      `

---

## 257. `1700 S IH 35 ROUND ROCK TX 78681`
*TX · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `1700` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `IH` | StreetName |
| `35` | StreetName |
| `ROUND` | PlaceName |
| `ROCK` | PlaceName |
| `TX` | StateName |
| `78681` | ZipCode |

**Your answer:** `      `

---

## 258. `12020 SW 182 TER MIAMI FL 0`
*FL · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `12020` | AddressNumber |
| `SW` | StreetNamePostDirectional |
| `182` | OccupancyIdentifier |
| `TER` | PlaceName |
| `MIAMI` | PlaceName |
| `FL` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 259. `80 SOUTH ST WATERBURY CT 06706`
*CT · model confidence 0.61*

| Token | Proposed label |
|---|---|
| `80` | AddressNumber |
| `SOUTH` | StreetNamePostDirectional |
| `ST` | StreetNamePostType |
| `WATERBURY` | PlaceName |
| `CT` | StateName |
| `06706` | ZipCode |

**Your answer:** `      `

---

## 260. `5549 NC 67 HWY BOONVILLE NC 27011`
*NC · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `5549` | AddressNumber |
| `NC` | StreetName |
| `67` | StreetName |
| `HWY` | StreetNamePostType |
| `BOONVILLE` | PlaceName |
| `NC` | StateName |
| `27011` | ZipCode |

**Your answer:** `      `

---

## 261. `143 DUNE DRIVE 42 BRIANS WAY NORRIDGEWOCK ME`
*ME · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `143` | AddressNumber |
| `DUNE` | StreetName |
| `DRIVE` | StreetName |
| `42` | StreetName |
| `BRIANS` | StreetName |
| `WAY` | StreetNamePostType |
| `NORRIDGEWOCK` | PlaceName |
| `ME` | StateName |

**Your answer:** `      `

---

## 262. `1315 KESSLER BOULEVARD EAST DR INDIANAPOLIS IN 462202744`
*IN · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `1315` | AddressNumber |
| `KESSLER` | StreetName |
| `BOULEVARD` | StreetName |
| `EAST` | StreetName |
| `DR` | StreetNamePostType |
| `INDIANAPOLIS` | PlaceName |
| `IN` | StateName |
| `462202744` | ZipCode |

**Your answer:** `      `

---

## 263. `268 COLD SPRING AVE WEST SPRINGFIELD MA 01089`
*MA · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `268` | AddressNumber |
| `COLD` | StreetName |
| `SPRING` | StreetName |
| `AVE` | StreetNamePostType |
| `WEST` | StreetNamePostDirectional |
| `SPRINGFIELD` | PlaceName |
| `MA` | StateName |
| `01089` | ZipCode |

**Your answer:** `      `

---

## 264. `7401 OLD CONCORD RD 28213 CHARLOTTE NC 28213`
*NC · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `7401` | AddressNumber |
| `OLD` | StreetName |
| `CONCORD` | StreetName |
| `RD` | StreetNamePostType |
| `28213` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28213` | ZipCode |

**Your answer:** `      `

---

## 265. `3965 W 83RD ST PRAIRIE VILLAGE KS 66208`
*MO · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `3965` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `83RD` | StreetName |
| `ST` | StreetNamePostType |
| `PRAIRIE` | PlaceName |
| `VILLAGE` | PlaceName |
| `KS` | StateName |
| `66208` | ZipCode |

**Your answer:** `      `

---

## 266. `86 HAMILTON TRAIL 07512`
*NJ · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `86` | AddressNumber |
| `HAMILTON` | StreetName |
| `TRAIL` | StreetNamePostType |
| `07512` | ZipCode |

**Your answer:** `      `

---

## 267. `1901 W CALLE DEL REPOSO TUCSON AZ 85745-2127`
*AZ · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `1901` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `DEL` | StreetName |
| `REPOSO` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-2127` | ZipCode |

**Your answer:** `      `

---

## 268. `209B PENDLETON HILL ROAD NORTH STONINGTON CT 6359`
*CT · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `209B` | AddressNumber |
| `PENDLETON` | StreetName |
| `HILL` | StreetName |
| `ROAD` | StreetNamePostType |
| `NORTH` | PlaceName |
| `STONINGTON` | PlaceName |
| `CT` | StateName |
| `6359` | ZipCode |

**Your answer:** `      `

---

## 269. `531 HERRICKS COVE RD E CALAIS VT 05650`
*VT · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `531` | AddressNumber |
| `HERRICKS` | StreetName |
| `COVE` | StreetName |
| `RD` | StreetNamePostType |
| `E` | StreetNamePostDirectional |
| `CALAIS` | PlaceName |
| `VT` | StateName |
| `05650` | ZipCode |

**Your answer:** `      `

---

## 270. `1760 OAK GROVE DRIVE NORTH DIGHTON MA 02764`
*MA · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `1760` | AddressNumber |
| `OAK` | StreetName |
| `GROVE` | StreetName |
| `DRIVE` | StreetNamePostType |
| `NORTH` | StreetNamePostDirectional |
| `DIGHTON` | PlaceName |
| `MA` | StateName |
| `02764` | ZipCode |

**Your answer:** `      `

---

## 271. `53395 VIA STRADA`
*OR · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `53395` | AddressNumber |
| `VIA` | StreetName |
| `STRADA` | StreetName |

**Your answer:** `      `

---

## 272. `20 1/2 ELM ST SWANTON VT 05488`
*VT · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `20` | AddressNumber |
| `1/2` | AddressNumberSuffix |
| `ELM` | StreetName |
| `ST` | StreetNamePostType |
| `SWANTON` | PlaceName |
| `VT` | StateName |
| `05488` | ZipCode |

**Your answer:** `      `

---

## 273. `991 PRIVATE ROAD 905 LIBERTY HILL TX 78642`
*TX · model confidence 0.62*

| Token | Proposed label |
|---|---|
| `991` | AddressNumber |
| `PRIVATE` | StreetName |
| `ROAD` | StreetNamePostType |
| `905` | OccupancyIdentifier |
| `LIBERTY` | PlaceName |
| `HILL` | PlaceName |
| `TX` | StateName |
| `78642` | ZipCode |

**Your answer:** `      `

---

## 274. `197 OLD NORTH STATE LN NEW LONDON NC 28127`
*NC · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `197` | AddressNumber |
| `OLD` | StreetName |
| `NORTH` | StreetName |
| `STATE` | StreetName |
| `LN` | StreetNamePostType |
| `NEW` | PlaceName |
| `LONDON` | PlaceName |
| `NC` | StateName |
| `28127` | ZipCode |

**Your answer:** `      `

---

## 275. `18311 NE 99TH WAY 98052`
*WA · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `18311` | AddressNumber |
| `NE` | StreetNamePreDirectional |
| `99TH` | StreetName |
| `WAY` | StreetNamePostType |
| `98052` | ZipCode |

**Your answer:** `      `

---

## 276. `1321 BULL HORN LOOP ROUND ROCK TX 78665`
*TX · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `1321` | AddressNumber |
| `BULL` | StreetName |
| `HORN` | StreetName |
| `LOOP` | StreetNamePostType |
| `ROUND` | PlaceName |
| `ROCK` | PlaceName |
| `TX` | StateName |
| `78665` | ZipCode |

**Your answer:** `      `

---

## 277. `1864 ASTON MILL PL 28273 CHARLOTTE NC 28273`
*NC · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `1864` | AddressNumber |
| `ASTON` | StreetName |
| `MILL` | StreetName |
| `PL` | StreetNamePostType |
| `28273` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28273` | ZipCode |

**Your answer:** `      `

---

## 278. `29 LOTUS AVENUE WEST SPRINGFIELD MA 01089`
*MA · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `29` | AddressNumber |
| `LOTUS` | StreetName |
| `AVENUE` | StreetNamePostType |
| `WEST` | StreetNamePostDirectional |
| `SPRINGFIELD` | PlaceName |
| `MA` | StateName |
| `01089` | ZipCode |

**Your answer:** `      `

---

## 279. `15624 SUMMERBROOKE LANE SOUTH BELOIT IL 61080`
*IL · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `15624` | AddressNumber |
| `SUMMERBROOKE` | StreetName |
| `LANE` | StreetNamePostType |
| `SOUTH` | PlaceName |
| `BELOIT` | PlaceName |
| `IL` | StateName |
| `61080` | ZipCode |

**Your answer:** `      `

---

## 280. `114 BROOKLYN STANHOPE RD 07843`
*NJ · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `114` | AddressNumber |
| `BROOKLYN` | StreetName |
| `STANHOPE` | PlaceName |
| `RD` | StateName |
| `07843` | ZipCode |

**Your answer:** `      `

---

## 281. `6832 IDLEWILD RD 28212 CHARLOTTE NC 28212`
*NC · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `6832` | AddressNumber |
| `IDLEWILD` | StreetName |
| `RD` | StreetNamePostType |
| `28212` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28212` | ZipCode |

**Your answer:** `      `

---

## 282. `15928 HENRY LN 28078 HUNTERSVILLE NC 28078`
*NC · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `15928` | AddressNumber |
| `HENRY` | StreetName |
| `LN` | StreetNamePostType |
| `28078` | OccupancyIdentifier |
| `HUNTERSVILLE` | PlaceName |
| `NC` | StateName |
| `28078` | ZipCode |

**Your answer:** `      `

---

## 283. `24 CHRISTMAS TREE HILL CANTON CT 06019`
*CT · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `24` | AddressNumber |
| `CHRISTMAS` | StreetName |
| `TREE` | StreetName |
| `HILL` | StreetName |
| `CANTON` | PlaceName |
| `CT` | StateName |
| `06019` | ZipCode |

**Your answer:** `      `

---

## 284. `2143 A BURNS ST A NASHVILLE TN 37216`
*TN · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `2143` | AddressNumber |
| `A` | AddressNumberSuffix |
| `BURNS` | StreetName |
| `ST` | StreetNamePostType |
| `A` | OccupancyIdentifier |
| `NASHVILLE` | PlaceName |
| `TN` | StateName |
| `37216` | ZipCode |

**Your answer:** `      `

---

## 285. `130 KANSAS CITY ST RAPID CITY SD 57701-2818`
*SD · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `130` | AddressNumber |
| `KANSAS` | StreetName |
| `CITY` | PlaceName |
| `ST` | PlaceName |
| `RAPID` | PlaceName |
| `CITY` | PlaceName |
| `SD` | StateName |
| `57701-2818` | ZipCode |

**Your answer:** `      `

---

## 286. `838 W CALLE VENTURA TUCSON AZ 85705-5333`
*AZ · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `838` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `VENTURA` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85705-5333` | ZipCode |

**Your answer:** `      `

---

## 287. `425 WARREN LANE KEY BISCAYNE FL 0`
*FL · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `425` | AddressNumber |
| `WARREN` | StreetName |
| `LANE` | StreetName |
| `KEY` | StreetNamePostType |
| `BISCAYNE` | PlaceName |
| `FL` | StateName |
| `0` | ZipCode |

**Your answer:** `      `

---

## 288. `1 COOPER PLAZA 08103`
*NJ · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `1` | AddressNumber |
| `COOPER` | StreetName |
| `PLAZA` | StreetNamePostType |
| `08103` | ZipCode |

**Your answer:** `      `

---

## 289. `1445 W CALLE PLATINO TUCSON AZ 85745-2776`
*AZ · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `1445` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `PLATINO` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-2776` | ZipCode |

**Your answer:** `      `

---

## 290. `2016 W CALLE NIAGARA TUCSON AZ 85745-2121`
*AZ · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `2016` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `NIAGARA` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-2121` | ZipCode |

**Your answer:** `      `

---

## 291. `1441 W CALLE PLATINO TUCSON AZ 85745-0000`
*AZ · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `1441` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `CALLE` | StreetName |
| `PLATINO` | StreetName |
| `TUCSON` | PlaceName |
| `AZ` | StateName |
| `85745-0000` | ZipCode |

**Your answer:** `      `

---

## 292. `PO BOX 184 E BARRE VT 05649`
*VT · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `184` | USPSBoxID |
| `E` | PlaceName |
| `BARRE` | PlaceName |
| `VT` | StateName |
| `05649` | ZipCode |

**Your answer:** `      `

---

## 293. `PO BOX 311 E BARRE VT 05649-0311`
*VT · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `311` | USPSBoxID |
| `E` | PlaceName |
| `BARRE` | PlaceName |
| `VT` | StateName |
| `05649-0311` | ZipCode |

**Your answer:** `      `

---

## 294. `PO BOX 322 E BARRE VT 05649-0322`
*VT · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `322` | USPSBoxID |
| `E` | PlaceName |
| `BARRE` | PlaceName |
| `VT` | StateName |
| `05649-0322` | ZipCode |

**Your answer:** `      `

---

## 295. `PO BOX 237 E BARRE VT 05649-0237`
*VT · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `237` | USPSBoxID |
| `E` | PlaceName |
| `BARRE` | PlaceName |
| `VT` | StateName |
| `05649-0237` | ZipCode |

**Your answer:** `      `

---

## 296. `PO BOX 302 E BARRE VT 05649-0302`
*VT · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `302` | USPSBoxID |
| `E` | PlaceName |
| `BARRE` | PlaceName |
| `VT` | StateName |
| `05649-0302` | ZipCode |

**Your answer:** `      `

---

## 297. `PO BOX 274 E BARRE VT 05649-0274`
*VT · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `274` | USPSBoxID |
| `E` | PlaceName |
| `BARRE` | PlaceName |
| `VT` | StateName |
| `05649-0274` | ZipCode |

**Your answer:** `      `

---

## 298. `PO BOX 446 E BARRE VT 05649-0446`
*VT · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `446` | USPSBoxID |
| `E` | PlaceName |
| `BARRE` | PlaceName |
| `VT` | StateName |
| `05649-0446` | ZipCode |

**Your answer:** `      `

---

## 299. `3 INDIAN DAWN WAYLAND MA 01778`
*MA · model confidence 0.63*

| Token | Proposed label |
|---|---|
| `3` | AddressNumber |
| `INDIAN` | StreetName |
| `DAWN` | StreetName |
| `WAYLAND` | PlaceName |
| `MA` | StateName |
| `01778` | ZipCode |

**Your answer:** `      `

---

## 300. `27305 US 79 THRALL TX 76578`
*TX · model confidence 0.64*

| Token | Proposed label |
|---|---|
| `27305` | AddressNumber |
| `US` | StreetNamePreType |
| `79` | StreetName |
| `THRALL` | PlaceName |
| `TX` | StateName |
| `76578` | ZipCode |

**Your answer:** `      `

---

## When you're done

Paste answers back in any form. They're stored as approved label sequences and join the training corpus for the next v2 attempt. This is a dev/training asset, not an exam: gold-2b's final scoring attempt stays untouched, and any model this produces still has to clear gold-2c (your absolute labels) and then the exam before it could ship.

Batch size is yours to set — this is records 1-300; there are 5000 in value order. Label as far as your budget allows; ask for the next batch when ready.