# Address review — Round 9 (gold-2b): 136 parses

## What this is

Gold-2b is the replacement national exam, built after gold-2's two attempts were spent: 2,912 records across 32 states in the strict cohort, drawn only from datasets that neither the previous exam nor any training corpus ever touched. This is scoring attempt 1 of 2 for its lifetime.

These are every record where the two parsers disagree (136 of 3,569 records; under the 150 tripwire, so you're seeing all of them).

**114 are in the strict cohort**, which is the primary analysis. The rest sit in the two labelled sensitivity cohorts and are marked as such — your verdicts on them feed the secondary numbers only.

Models are blinded as **A** / **B** under a fresh key. Answer **A** · **B** · **neither** · **skip** per entry. Only human verdicts enter any gate.

---

## 1. `8233 GRAYSON GROVE MONTGOMERY AL 36117`
*AL — https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/Sex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `8233` | AddressNumber | AddressNumber |
| | `GRAYSON` | StreetName | StreetName |
| **←** | `GROVE` | **StreetNamePostType** | **StreetName** |
| | `MONTGOMERY` | PlaceName | PlaceName |
| | `AL` | StateName | StateName |
| | `36117` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 2. `8316 GRAYSON GROVE MONTGOMERY AL 36117`
*AL — https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/Sex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `8316` | AddressNumber | AddressNumber |
| | `GRAYSON` | StreetName | StreetName |
| **←** | `GROVE` | **StreetNamePostType** | **StreetName** |
| | `MONTGOMERY` | PlaceName | PlaceName |
| | `AL` | StateName | StateName |
| | `36117` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 3. `8281 GRAYSON GROVE MONTGOMERY AL 36117`
*AL — https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/Sex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `8281` | AddressNumber | AddressNumber |
| | `GRAYSON` | StreetName | StreetName |
| **←** | `GROVE` | **StreetNamePostType** | **StreetName** |
| | `MONTGOMERY` | PlaceName | PlaceName |
| | `AL` | StateName | StateName |
| | `36117` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 4. `8275 GRAYSON GROVE MONTGOMERY AL 36117`
*AL — https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/Sex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `8275` | AddressNumber | AddressNumber |
| | `GRAYSON` | StreetName | StreetName |
| **←** | `GROVE` | **StreetNamePostType** | **StreetName** |
| | `MONTGOMERY` | PlaceName | PlaceName |
| | `AL` | StateName | StateName |
| | `36117` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 5. `440 MERRY WAY PIKE ROAD AL 36064-2282`
*AL — https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/Sex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `440` | AddressNumber | AddressNumber |
| | `MERRY` | StreetName | StreetName |
| **←** | `WAY` | **StreetName** | **StreetNamePostType** |
| **←** | `PIKE` | **StreetName** | **PlaceName** |
| **←** | `ROAD` | **StreetName** | **PlaceName** |
| **←** | `AL` | **StreetNamePostType** | **StateName** |
| | `36064-2282` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 6. `221 HEMPSTEAD 22 P.O. BOX 46 OZAN AR 71855`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `221` | AddressNumber | AddressNumber |
| **←** | `HEMPSTEAD` | **StreetName** | **SubaddressType** |
| **←** | `22` | **StreetName** | **SubaddressIdentifier** |
| | `P.O.` | USPSBoxType | USPSBoxType |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `46` | USPSBoxID | USPSBoxID |
| | `OZAN` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `71855` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 7. `255 HEMPSTEAD 314 OZAN AR 71855`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `255` | AddressNumber | AddressNumber |
| | `HEMPSTEAD` | StreetName | StreetName |
| **←** | `314` | **StreetName** | **OccupancyIdentifier** |
| | `OZAN` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `71855` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 8. `348 HEMPSTEAD 104 HOPE AR 71801`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `348` | AddressNumber | AddressNumber |
| | `HEMPSTEAD` | StreetName | StreetName |
| **←** | `104` | **StreetName** | **OccupancyIdentifier** |
| | `HOPE` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `71801` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 9. `PO BOX 83 308 NE CONWAY ST, WASHINGTON AR HOPE AR 71802`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `PO` | USPSBoxType | USPSBoxType |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `83` | USPSBoxID | USPSBoxID |
| | `308` | AddressNumber | AddressNumber |
| | `NE` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `CONWAY` | StreetName | StreetName |
| | `ST,` | StreetNamePostType | StreetNamePostType |
| | `WASHINGTON` | PlaceName | PlaceName |
| **←** | `AR` | **StateName** | **PlaceName** |
| | `HOPE` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `71802` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 10. `698 HEMPSTEAD 28 MCCASKILL AR 71847`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `698` | AddressNumber | AddressNumber |
| | `HEMPSTEAD` | StreetName | StreetName |
| **←** | `28` | **StreetName** | **OccupancyIdentifier** |
| | `MCCASKILL` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `71847` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 11. `12 BECKY'S COVE LANE CAPE ELIZABETH ME 04107`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `12` | AddressNumber | AddressNumber |
| | `BECKY'S` | StreetName | StreetName |
| | `COVE` | StreetName | StreetName |
| **←** | `LANE` | **StreetName** | **StreetNamePostType** |
| **←** | `CAPE` | **StreetNamePostType** | **PlaceName** |
| | `ELIZABETH` | PlaceName | PlaceName |
| | `ME` | StateName | StateName |
| | `04107` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 12. `350 HEMPSTEAD 269 MC CASKILL AR 71847`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `350` | AddressNumber | AddressNumber |
| | `HEMPSTEAD` | StreetName | StreetName |
| **←** | `269` | **StreetName** | **OccupancyIdentifier** |
| **←** | `MC` | **StreetNamePostType** | **PlaceName** |
| | `CASKILL` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `71847` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 13. `ONE CAPITOL MALL LITTLE ROCK AR 72201`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `ONE` | **AddressNumber** | **LandmarkName** |
| **←** | `CAPITOL` | **StreetName** | **LandmarkName** |
| **←** | `MALL` | **StreetNamePostType** | **LandmarkName** |
| | `LITTLE` | PlaceName | PlaceName |
| | `ROCK` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `72201` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 14. `11995 EL CAMINO REAL SAN DIEGO CA 92130`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `11995` | AddressNumber | AddressNumber |
| | `EL` | StreetName | StreetName |
| **←** | `CAMINO` | **PlaceName** | **StreetName** |
| **←** | `REAL` | **PlaceName** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `DIEGO` | PlaceName | PlaceName |
| | `CA` | StateName | StateName |
| | `92130` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 15. `#1 CAPITOL MALL LITTLE ROCK AR 72201`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `#` | **OccupancyIdentifier** | **AddressNumberPrefix** |
| **←** | `1` | **OccupancyIdentifier** | **AddressNumber** |
| **←** | `CAPITOL` | **PlaceName** | **StreetName** |
| **←** | `MALL` | **PlaceName** | **StreetNamePostType** |
| | `LITTLE` | PlaceName | PlaceName |
| | `ROCK` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `72201` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 16. `805 E 7TH ST 1406 ALLEN ST HOPE AR 71801`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `805` | AddressNumber | AddressNumber |
| | `E` | StreetNamePreDirectional | StreetNamePreDirectional |
| **←** | `7TH` | **StreetNamePreType** | **StreetName** |
| **←** | `ST` | **StreetNamePreType** | **StreetName** |
| | `1406` | StreetName | StreetName |
| | `ALLEN` | StreetName | StreetName |
| | `ST` | StreetNamePostType | StreetNamePostType |
| | `HOPE` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `71801` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 17. `323 HEMPSTEAD 10 FULTON AR 71838-9013`
*AR — https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `323` | AddressNumber | AddressNumber |
| **←** | `HEMPSTEAD` | **StreetNamePreType** | **StreetName** |
| **←** | `10` | **StreetName** | **OccupancyIdentifier** |
| | `FULTON` | PlaceName | PlaceName |
| | `AR` | StateName | StateName |
| | `71838-9013` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 18. `2150 CENTRE AVE UNIT E FORT COLLINS CO 805268116`
*CO — https://maps1.larimer.org/arcgis/rest/services/MapServices/Parcels/Map*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2150` | AddressNumber | AddressNumber |
| | `CENTRE` | StreetName | StreetName |
| **←** | `AVE` | **StreetNamePostType** | **StreetName** |
| **←** | `UNIT` | **OccupancyType** | **StreetName** |
| **←** | `E` | **OccupancyIdentifier** | **StreetNamePostDirectional** |
| | `FORT` | PlaceName | PlaceName |
| | `COLLINS` | PlaceName | PlaceName |
| | `CO` | StateName | StateName |
| | `805268116` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 19. `702 W DRAKE RD BLDG F STE B FORT COLLINS CO 805265528`
*CO — https://maps1.larimer.org/arcgis/rest/services/MapServices/Parcels/Map*

| | Token | Model A | Model B |
|---|---|---|---|
| | `702` | AddressNumber | AddressNumber |
| | `W` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `DRAKE` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `BLDG` | **SubaddressType** | **BuildingName** |
| **←** | `F` | **SubaddressIdentifier** | **BuildingName** |
| | `STE` | OccupancyType | OccupancyType |
| | `B` | OccupancyIdentifier | OccupancyIdentifier |
| | `FORT` | PlaceName | PlaceName |
| | `COLLINS` | PlaceName | PlaceName |
| | `CO` | StateName | StateName |
| | `805265528` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 20. `1610 LOWER BROADVIEW ESTES PARK CO 805178219`
*CO — https://maps1.larimer.org/arcgis/rest/services/MapServices/Parcels/Map*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1610` | AddressNumber | AddressNumber |
| | `LOWER` | StreetName | StreetName |
| **←** | `BROADVIEW` | **StreetName** | **PlaceName** |
| | `ESTES` | PlaceName | PlaceName |
| | `PARK` | PlaceName | PlaceName |
| | `CO` | StateName | StateName |
| | `805178219` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 21. `144 TIDBURY CROSSING CAMDEN WYOMING DE 19934`
*DE — https://gis.kentcountyde.gov/server/rest/services/Parcels/Parcels/Feat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `144` | AddressNumber | AddressNumber |
| | `TIDBURY` | StreetName | StreetName |
| **←** | `CROSSING` | **StreetNamePostType** | **StreetName** |
| | `CAMDEN` | PlaceName | PlaceName |
| | `WYOMING` | PlaceName | PlaceName |
| | `DE` | StateName | StateName |
| | `19934` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 22. `27 S MARKET ST PLZ SMYRNA DE 19977`
*DE — https://gis.kentcountyde.gov/server/rest/services/Parcels/Parcels/Feat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `27` | AddressNumber | AddressNumber |
| | `S` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `MARKET` | StreetName | StreetName |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `PLZ` | **StreetNamePostType** | **PlaceName** |
| | `SMYRNA` | PlaceName | PlaceName |
| | `DE` | StateName | StateName |
| | `19977` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 23. `31263 SATINLEAF RUN BROOKSVILLE FL 34602-7719`
*FL — https://services2.arcgis.com/x5zvhhxfUuRDntRe/arcgis/rest/services/Bas  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `31263` | AddressNumber | AddressNumber |
| | `SATINLEAF` | StreetName | StreetName |
| **←** | `RUN` | **StreetNamePostType** | **StreetName** |
| | `BROOKSVILLE` | PlaceName | PlaceName |
| | `FL` | StateName | StateName |
| | `34602-7719` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 24. `3290 CANTERBURY DR SURREY, BC V3S 0J4`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3290` | AddressNumber | AddressNumber |
| | `CANTERBURY` | StreetName | StreetName |
| | `DR` | StreetNamePostType | StreetNamePostType |
| | `SURREY,` | PlaceName | PlaceName |
| | `BC` | StateName | StateName |
| **←** | `V3S` | **StateName** | **USPSBoxID** |
| **←** | `0J4` | **ZipCode** | **USPSBoxID** |

**Your verdict:** `      `

---

## 25. `201-1461 ST PAUL ST KELOWNA, BRITISH COLUMBIA V1Y2E4`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `201-1461` | **Recipient** | **AddressNumber** |
| **←** | `ST` | **Recipient** | **StreetName** |
| **←** | `PAUL` | **Recipient** | **StreetName** |
| **←** | `ST` | **Recipient** | **StreetNamePostType** |
| **←** | `KELOWNA,` | **Recipient** | **BuildingName** |
| **←** | `BRITISH` | **Recipient** | **BuildingName** |
| **←** | `COLUMBIA` | **Recipient** | **BuildingName** |
| **←** | `V1Y2E4` | **Recipient** | **OccupancyIdentifier** |

**Your verdict:** `      `

---

## 26. `216 MACEWAN VALLEY MEWS NW CALGARY, ALBERTA T3K 3T3`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `216` | AddressNumber | AddressNumber |
| | `MACEWAN` | StreetName | StreetName |
| | `VALLEY` | StreetName | StreetName |
| | `MEWS` | StreetNamePostType | StreetNamePostType |
| | `NW` | StreetNamePostDirectional | StreetNamePostDirectional |
| | `CALGARY,` | PlaceName | PlaceName |
| | `ALBERTA` | StateName | StateName |
| **←** | `T3K` | **StateName** | **USPSBoxID** |
| **←** | `3T3` | **ZipCode** | **USPSBoxID** |

**Your verdict:** `      `

---

## 27. `#330, 4392 WEST SAANICH RD VICTORIA, BC V8Z 3E9`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `#` | **OccupancyIdentifier** | **Recipient** |
| **←** | `330,` | **OccupancyIdentifier** | **Recipient** |
| | `4392` | AddressNumber | AddressNumber |
| | `WEST` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `SAANICH` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| | `VICTORIA,` | PlaceName | PlaceName |
| | `BC` | StateName | StateName |
| **←** | `V8Z` | **OccupancyIdentifier** | **USPSBoxID** |
| **←** | `3E9` | **OccupancyIdentifier** | **USPSBoxID** |

**Your verdict:** `      `

---

## 28. `C/O LAW OFFICE OF HOWARD GREEN P O BOX 3467 HONOLULU HI 96801`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `LAW` | Recipient | Recipient |
| | `OFFICE` | Recipient | Recipient |
| | `OF` | Recipient | Recipient |
| | `HOWARD` | Recipient | Recipient |
| | `GREEN` | Recipient | Recipient |
| **←** | `P` | **USPSBoxType** | **Recipient** |
| **←** | `O` | **USPSBoxType** | **Recipient** |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `3467` | USPSBoxID | USPSBoxID |
| | `HONOLULU` | PlaceName | PlaceName |
| | `HI` | StateName | StateName |
| | `96801` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 29. `3162 W 15TH AVE VANCOUVER, BC V6K 3A6`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3162` | AddressNumber | AddressNumber |
| | `W` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `15TH` | StreetName | StreetName |
| | `AVE` | StreetNamePostType | StreetNamePostType |
| | `VANCOUVER,` | PlaceName | PlaceName |
| | `BC` | StateName | StateName |
| **←** | `V6K` | **OccupancyIdentifier** | **USPSBoxID** |
| **←** | `3A6` | **OccupancyIdentifier** | **USPSBoxID** |

**Your verdict:** `      `

---

## 30. `254 POPLAR POINT DR KELOWNA, BC V1Y 1Y1`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `254` | AddressNumber | AddressNumber |
| | `POPLAR` | StreetName | StreetName |
| | `POINT` | StreetName | StreetName |
| | `DR` | StreetNamePostType | StreetNamePostType |
| | `KELOWNA,` | PlaceName | PlaceName |
| | `BC` | StateName | StateName |
| **←** | `V1Y` | **StateName** | **USPSBoxID** |
| **←** | `1Y1` | **ZipCode** | **USPSBoxID** |

**Your verdict:** `      `

---

## 31. `14014 BAYVIEW AVE AURORA,ONTARIO L4G 0L1`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `14014` | AddressNumber | AddressNumber |
| | `BAYVIEW` | StreetName | StreetName |
| | `AVE` | StreetNamePostType | StreetNamePostType |
| | `AURORA,` | PlaceName | PlaceName |
| | `ONTARIO` | StateName | StateName |
| **←** | `L4G` | **StateName** | **USPSBoxID** |
| **←** | `0L1` | **ZipCode** | **USPSBoxID** |

**Your verdict:** `      `

---

## 32. `C/O YVONNE M KEKONA P O BOX 924 AIEA HI 96701`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `YVONNE` | Recipient | Recipient |
| | `M` | Recipient | Recipient |
| | `KEKONA` | Recipient | Recipient |
| **←** | `P` | **USPSBoxType** | **Recipient** |
| **←** | `O` | **USPSBoxType** | **Recipient** |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `924` | USPSBoxID | USPSBoxID |
| | `AIEA` | PlaceName | PlaceName |
| | `HI` | StateName | StateName |
| | `96701` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 33. `C/O KOZMA,ANDREW/MARIA 130 KAI MALINA PKWY UNIT SR 347 LAHAINA HI 96761`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `KOZMA,` | Recipient | Recipient |
| | `ANDREW/MARIA` | Recipient | Recipient |
| | `130` | AddressNumber | AddressNumber |
| | `KAI` | StreetName | StreetName |
| | `MALINA` | StreetName | StreetName |
| **←** | `PKWY` | **StreetName** | **StreetNamePostType** |
| **←** | `UNIT` | **StreetName** | **OccupancyType** |
| **←** | `SR` | **StreetName** | **OccupancyIdentifier** |
| **←** | `347` | **StreetName** | **OccupancyIdentifier** |
| | `LAHAINA` | PlaceName | PlaceName |
| | `HI` | StateName | StateName |
| | `96761` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 34. `C/O KOZMA,ANDREW/MARIA 504-3500 LAKESHORE RD W OAKVILLE ONTARIO L6L 0B4`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `KOZMA,` | Recipient | Recipient |
| | `ANDREW/MARIA` | Recipient | Recipient |
| | `504-3500` | Recipient | Recipient |
| | `LAKESHORE` | Recipient | Recipient |
| | `RD` | Recipient | Recipient |
| | `W` | Recipient | Recipient |
| | `OAKVILLE` | Recipient | Recipient |
| | `ONTARIO` | Recipient | Recipient |
| | `L6L` | Recipient | Recipient |
| **←** | `0B4` | **Recipient** | **AddressNumber** |

**Your verdict:** `      `

---

## 35. `PO BOX 12222 LLOYDMINSTER, ALBERTA T9V 3C4`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `PO` | USPSBoxType | USPSBoxType |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `12222` | USPSBoxID | USPSBoxID |
| | `LLOYDMINSTER,` | PlaceName | PlaceName |
| | `ALBERTA` | StateName | StateName |
| **←** | `T9V` | **StateName** | **USPSBoxID** |
| **←** | `3C4` | **ZipCode** | **USPSBoxID** |

**Your verdict:** `      `

---

## 36. `1515 SPRING RD MISSISSAUGA, ON L5J 1M8`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1515` | AddressNumber | AddressNumber |
| | `SPRING` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| | `MISSISSAUGA,` | PlaceName | PlaceName |
| | `ON` | StateName | StateName |
| **←** | `L5J` | **StateName** | **USPSBoxID** |
| **←** | `1M8` | **ZipCode** | **USPSBoxID** |

**Your verdict:** `      `

---

## 37. `2902-1455 HOWE ST VANCOUVER BC V6Z 1C2`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2902-1455` | AddressNumber | AddressNumber |
| | `HOWE` | StreetName | StreetName |
| | `ST` | StreetNamePostType | StreetNamePostType |
| | `VANCOUVER` | PlaceName | PlaceName |
| | `BC` | StateName | StateName |
| **←** | `V6Z` | **StateName** | **USPSBoxID** |
| **←** | `1C2` | **ZipCode** | **USPSBoxID** |

**Your verdict:** `      `

---

## 38. `5-2142 ARGYLE AVE WEST VANCOUVER, BC V7V 1A4`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5-2142` | AddressNumber | AddressNumber |
| | `ARGYLE` | StreetName | StreetName |
| | `AVE` | StreetNamePostType | StreetNamePostType |
| | `WEST` | PlaceName | PlaceName |
| | `VANCOUVER,` | PlaceName | PlaceName |
| | `BC` | StateName | StateName |
| **←** | `V7V` | **OccupancyIdentifier** | **USPSBoxID** |
| **←** | `1A4` | **OccupancyIdentifier** | **USPSBoxID** |

**Your verdict:** `      `

---

## 39. `LOYL & LYNELLE WILLIAMS TTEES 649 CYPRESS RUN WOODBRIDGE CA 95258`
*HI — https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `LOYL` | Recipient | Recipient |
| | `&` | Recipient | Recipient |
| | `LYNELLE` | Recipient | Recipient |
| | `WILLIAMS` | Recipient | Recipient |
| | `TTEES` | Recipient | Recipient |
| | `649` | AddressNumber | AddressNumber |
| | `CYPRESS` | StreetName | StreetName |
| **←** | `RUN` | **StreetNamePostType** | **StreetName** |
| | `WOODBRIDGE` | PlaceName | PlaceName |
| | `CA` | StateName | StateName |
| | `95258` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 40. `5828 PINTO PLACE RANCH GUCAMONGA, CA 91739`
*IA — https://services.arcgis.com/ovln19YRWV44nBqV/arcgis/rest/services/Cada*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5828` | AddressNumber | AddressNumber |
| | `PINTO` | StreetName | StreetName |
| **←** | `PLACE` | **StreetName** | **StreetNamePostType** |
| **←** | `RANCH` | **StreetNamePostType** | **PlaceName** |
| | `GUCAMONGA,` | PlaceName | PlaceName |
| | `CA` | StateName | StateName |
| | `91739` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 41. `#1908 DEPT 8088 PO BOX 2198 MEMPHIS, TN 38101-2198`
*IA — https://services.arcgis.com/ovln19YRWV44nBqV/arcgis/rest/services/Cada*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `#` | **SubaddressIdentifier** | **SubaddressType** |
| | `1908` | SubaddressIdentifier | SubaddressIdentifier |
| | `DEPT` | SubaddressType | SubaddressType |
| | `8088` | SubaddressIdentifier | SubaddressIdentifier |
| | `PO` | USPSBoxType | USPSBoxType |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `2198` | USPSBoxID | USPSBoxID |
| | `MEMPHIS,` | PlaceName | PlaceName |
| | `TN` | StateName | StateName |
| | `38101-2198` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 42. `UTD 2-12-2020 549 AUDUBON PL HIGHLAND PARK IL 60035-1203`
*IL — https://services3.arcgis.com/HESxeTbDliKKvec2/arcgis/rest/services/Ope*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `UTD` | **SubaddressType** | **Recipient** |
| **←** | `2-12-2020` | **SubaddressIdentifier** | **Recipient** |
| | `549` | AddressNumber | AddressNumber |
| | `AUDUBON` | StreetName | StreetName |
| | `PL` | StreetNamePostType | StreetNamePostType |
| | `HIGHLAND` | PlaceName | PlaceName |
| | `PARK` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `60035-1203` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 43. `4109 QUAIL HOLLOW EVANSVILLE IN 47715-1536`
*IN — https://maps.evansvillegis.com/arcgis_server/rest/services/ASSESSOR/PA*

| | Token | Model A | Model B |
|---|---|---|---|
| | `4109` | AddressNumber | AddressNumber |
| | `QUAIL` | StreetName | StreetName |
| **←** | `HOLLOW` | **StreetNamePostType** | **StreetName** |
| | `EVANSVILLE` | PlaceName | PlaceName |
| | `IN` | StateName | StateName |
| | `47715-1536` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 44. `1252 ST SCHOLASTICA SLIDELL LA 70458`
*LA — https://services2.arcgis.com/LJwIycC0yIuqCBxq/arcgis/rest/services/Sli*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `1252` | **StreetName** | **AddressNumber** |
| **←** | `ST` | **StreetNamePostType** | **StreetName** |
| **←** | `SCHOLASTICA` | **PlaceName** | **StreetName** |
| | `SLIDELL` | PlaceName | PlaceName |
| | `LA` | StateName | StateName |
| | `70458` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 45. `219 SOUTHERN STAR SLIDELL LA 70458`
*LA — https://services2.arcgis.com/LJwIycC0yIuqCBxq/arcgis/rest/services/Sli*

| | Token | Model A | Model B |
|---|---|---|---|
| | `219` | AddressNumber | AddressNumber |
| | `SOUTHERN` | StreetName | StreetName |
| **←** | `STAR` | **PlaceName** | **StreetName** |
| | `SLIDELL` | PlaceName | PlaceName |
| | `LA` | StateName | StateName |
| | `70458` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 46. `124 RUE D'AZUR SLIDELL LA 70461`
*LA — https://services2.arcgis.com/LJwIycC0yIuqCBxq/arcgis/rest/services/Sli*

| | Token | Model A | Model B |
|---|---|---|---|
| | `124` | AddressNumber | AddressNumber |
| **←** | `RUE` | **StreetName** | **StreetNamePreType** |
| | `D'AZUR` | StreetName | StreetName |
| | `SLIDELL` | PlaceName | PlaceName |
| | `LA` | StateName | StateName |
| | `70461` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 47. `1 WESTINGHOUSE PZ, Unit C:303 HYDE PARK MA 02136`
*MA — https://gisportal.boston.gov/arcgis/rest/services/Assessing/PROPERTY_A  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1` | AddressNumber | AddressNumber |
| | `WESTINGHOUSE` | StreetName | StreetName |
| **←** | `PZ,` | **StreetNamePostType** | **StreetName** |
| | `Unit` | OccupancyType | OccupancyType |
| | `C:303` | OccupancyIdentifier | OccupancyIdentifier |
| | `HYDE` | PlaceName | PlaceName |
| | `PARK` | PlaceName | PlaceName |
| | `MA` | StateName | StateName |
| | `02136` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 48. `CENTRE DORCHESTER MA 02124`
*MA — https://gisportal.boston.gov/arcgis/rest/services/Assessing/PROPERTY_A  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `CENTRE` | **PlaceName** | **StreetName** |
| | `DORCHESTER` | PlaceName | PlaceName |
| | `MA` | StateName | StateName |
| | `02124` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 49. `770 CUMMINS HW, Unit 21 MATTAPAN MA 02126`
*MA — https://gisportal.boston.gov/arcgis/rest/services/Assessing/PROPERTY_A  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `770` | AddressNumber | AddressNumber |
| | `CUMMINS` | StreetName | StreetName |
| **←** | `HW,` | **StreetNamePostType** | **StreetName** |
| | `Unit` | OccupancyType | OccupancyType |
| | `21` | OccupancyIdentifier | OccupancyIdentifier |
| | `MATTAPAN` | PlaceName | PlaceName |
| | `MA` | StateName | StateName |
| | `02126` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 50. `1 WESTINGHOUSE PZ, Unit C:217 HYDE PARK MA 02136`
*MA — https://gisportal.boston.gov/arcgis/rest/services/Assessing/PROPERTY_A  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1` | AddressNumber | AddressNumber |
| | `WESTINGHOUSE` | StreetName | StreetName |
| **←** | `PZ,` | **StreetNamePostType** | **StreetName** |
| | `Unit` | OccupancyType | OccupancyType |
| | `C:217` | OccupancyIdentifier | OccupancyIdentifier |
| | `HYDE` | PlaceName | PlaceName |
| | `PARK` | PlaceName | PlaceName |
| | `MA` | StateName | StateName |
| | `02136` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 51. `1 WESTINGHOUSE PZ, Unit C:220 HYDE PARK MA 02136`
*MA — https://gisportal.boston.gov/arcgis/rest/services/Assessing/PROPERTY_A  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1` | AddressNumber | AddressNumber |
| | `WESTINGHOUSE` | StreetName | StreetName |
| **←** | `PZ,` | **StreetNamePostType** | **StreetName** |
| | `Unit` | OccupancyType | OccupancyType |
| | `C:220` | OccupancyIdentifier | OccupancyIdentifier |
| | `HYDE` | PlaceName | PlaceName |
| | `PARK` | PlaceName | PlaceName |
| | `MA` | StateName | StateName |
| | `02136` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 52. `973 A RUSSELL AVE 4202 GAITHERSBURG MD 20879`
*MD — https://services8.arcgis.com/cbDaIA5xFnHBUlC1/arcgis/rest/services/Gai*

| | Token | Model A | Model B |
|---|---|---|---|
| | `973` | AddressNumber | AddressNumber |
| **←** | `A` | **AddressNumberSuffix** | **StreetName** |
| | `RUSSELL` | StreetName | StreetName |
| | `AVE` | StreetNamePostType | StreetNamePostType |
| | `4202` | OccupancyIdentifier | OccupancyIdentifier |
| | `GAITHERSBURG` | PlaceName | PlaceName |
| | `MD` | StateName | StateName |
| | `20879` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 53. `C/O JEM HOLDINGS LLC MIKAEL J 10 EAST 53RD ST 18TH FL NEW YORK NY 10022`
*MD — https://services8.arcgis.com/cbDaIA5xFnHBUlC1/arcgis/rest/services/Gai*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `JEM` | Recipient | Recipient |
| | `HOLDINGS` | Recipient | Recipient |
| | `LLC` | Recipient | Recipient |
| | `MIKAEL` | Recipient | Recipient |
| | `J` | Recipient | Recipient |
| | `10` | AddressNumber | AddressNumber |
| | `EAST` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `53RD` | StreetName | StreetName |
| | `ST` | StreetNamePostType | StreetNamePostType |
| | `18TH` | OccupancyIdentifier | OccupancyIdentifier |
| **←** | `FL` | **OccupancyType** | **OccupancyIdentifier** |
| | `NEW` | PlaceName | PlaceName |
| | `YORK` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10022` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 54. `Cotrustees, Moore Fam Rev Tr 409 East Patton St Sturgeon, MO 65284`
*MN — https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_mng  ·  _aggregate-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `Cotrustees,` | Recipient | Recipient |
| | `Moore` | Recipient | Recipient |
| | `Fam` | Recipient | Recipient |
| | `Rev` | Recipient | Recipient |
| **←** | `Tr` | **StreetNamePreType** | **Recipient** |
| **←** | `409` | **StreetName** | **AddressNumber** |
| **←** | `East` | **StreetName** | **StreetNamePreDirectional** |
| | `Patton` | StreetName | StreetName |
| | `St` | StreetNamePostType | StreetNamePostType |
| | `Sturgeon,` | PlaceName | PlaceName |
| | `MO` | StateName | StateName |
| | `65284` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 55. `C/O Land & Minerals Dept 320 W 2nd St Ste 302 Duluth, MN 55802`
*MN — https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_mng  ·  _aggregate-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `Land` | Recipient | Recipient |
| | `&` | Recipient | Recipient |
| | `Minerals` | Recipient | Recipient |
| **←** | `Dept` | **Recipient** | **SubaddressType** |
| **←** | `320` | **AddressNumber** | **SubaddressIdentifier** |
| | `W` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `2nd` | StreetName | StreetName |
| | `St` | StreetNamePostType | StreetNamePostType |
| | `Ste` | OccupancyType | OccupancyType |
| | `302` | OccupancyIdentifier | OccupancyIdentifier |
| | `Duluth,` | PlaceName | PlaceName |
| | `MN` | StateName | StateName |
| | `55802` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 56. `1544 RIDGEPOINTE PLACE DR, LAKE ST LOUIS MO, 63367`
*MO — https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Informat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1544` | AddressNumber | AddressNumber |
| | `RIDGEPOINTE` | StreetName | StreetName |
| | `PLACE` | StreetName | StreetName |
| | `DR,` | StreetNamePostType | StreetNamePostType |
| | `LAKE` | PlaceName | PlaceName |
| **←** | `ST` | **PlaceName** | **StateName** |
| | `LOUIS` | PlaceName | PlaceName |
| | `MO,` | StateName | StateName |
| | `63367` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 57. `93 RUE GRAND DR, LAKE ST LOUIS MO, 63367`
*MO — https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Informat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `93` | AddressNumber | AddressNumber |
| **←** | `RUE` | **StreetName** | **StreetNamePreType** |
| | `GRAND` | StreetName | StreetName |
| | `DR,` | StreetNamePostType | StreetNamePostType |
| | `LAKE` | PlaceName | PlaceName |
| **←** | `ST` | **PlaceName** | **StateName** |
| | `LOUIS` | PlaceName | PlaceName |
| | `MO,` | StateName | StateName |
| | `63367` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 58. `3333 RUE ROYALE APT 4, ST CHARLES MO, 63301-8237`
*MO — https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Informat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3333` | AddressNumber | AddressNumber |
| **←** | `RUE` | **StreetName** | **StreetNamePreType** |
| | `ROYALE` | StreetName | StreetName |
| | `APT` | OccupancyType | OccupancyType |
| | `4,` | OccupancyIdentifier | OccupancyIdentifier |
| | `ST` | PlaceName | PlaceName |
| | `CHARLES` | PlaceName | PlaceName |
| | `MO,` | StateName | StateName |
| | `63301-8237` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 59. `213 SILENT MEADOW DR, LAKE ST LOUIS MO, 63367`
*MO — https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Informat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `213` | AddressNumber | AddressNumber |
| | `SILENT` | StreetName | StreetName |
| | `MEADOW` | StreetName | StreetName |
| | `DR,` | StreetNamePostType | StreetNamePostType |
| | `LAKE` | PlaceName | PlaceName |
| **←** | `ST` | **PlaceName** | **StateName** |
| | `LOUIS` | PlaceName | PlaceName |
| | `MO,` | StateName | StateName |
| | `63367` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 60. `225 ARPENT ALLEY, ST CHARLES MO, 63301`
*MO — https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Informat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `225` | AddressNumber | AddressNumber |
| | `ARPENT` | StreetName | StreetName |
| **←** | `ALLEY,` | **StreetNamePostType** | **StreetName** |
| **←** | `ST` | **PlaceName** | **StreetNamePostType** |
| | `CHARLES` | PlaceName | PlaceName |
| | `MO,` | StateName | StateName |
| | `63301` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 61. `1 ST PETERS CENTRE BLVD, ST PETERS MO, 63376`
*MO — https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Informat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1` | AddressNumber | AddressNumber |
| | `ST` | StreetName | StreetName |
| | `PETERS` | StreetName | StreetName |
| | `CENTRE` | StreetName | StreetName |
| **←** | `BLVD,` | **StreetNamePostType** | **StreetName** |
| **←** | `ST` | **PlaceName** | **StreetNamePostType** |
| | `PETERS` | PlaceName | PlaceName |
| | `MO,` | StateName | StateName |
| | `63376` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 62. `425 FILIPP LN, LAKE ST LOUIS MO, 63367`
*MO — https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Informat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `425` | AddressNumber | AddressNumber |
| | `FILIPP` | StreetName | StreetName |
| | `LN,` | StreetNamePostType | StreetNamePostType |
| | `LAKE` | PlaceName | PlaceName |
| **←** | `ST` | **PlaceName** | **StateName** |
| | `LOUIS` | PlaceName | PlaceName |
| | `MO,` | StateName | StateName |
| | `63367` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 63. `2130 HAWKS LANDING DR, LAKE ST LOUIS MO, 63367`
*MO — https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Informat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2130` | AddressNumber | AddressNumber |
| | `HAWKS` | StreetName | StreetName |
| | `LANDING` | StreetName | StreetName |
| | `DR,` | StreetNamePostType | StreetNamePostType |
| | `LAKE` | PlaceName | PlaceName |
| **←** | `ST` | **PlaceName** | **StateName** |
| | `LOUIS` | PlaceName | PlaceName |
| | `MO,` | StateName | StateName |
| | `63367` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 64. `1524 RIDGEPOINTE PLACE DR, LAKE ST LOUIS MO, 63367`
*MO — https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Informat*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1524` | AddressNumber | AddressNumber |
| | `RIDGEPOINTE` | StreetName | StreetName |
| | `PLACE` | StreetName | StreetName |
| | `DR,` | StreetNamePostType | StreetNamePostType |
| | `LAKE` | PlaceName | PlaceName |
| **←** | `ST` | **PlaceName** | **StateName** |
| | `LOUIS` | PlaceName | PlaceName |
| | `MO,` | StateName | StateName |
| | `63367` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 65. `C/O RIGHT OF WAY DIV P O BO JACKSON MS 392151850`
*MS — https://services1.arcgis.com/XwK5zAS8O0b6s3Tp/arcgis/rest/services/Pub*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `RIGHT` | Recipient | Recipient |
| | `OF` | Recipient | Recipient |
| | `WAY` | Recipient | Recipient |
| | `DIV` | Recipient | Recipient |
| | `P` | Recipient | Recipient |
| | `O` | Recipient | Recipient |
| | `BO` | Recipient | Recipient |
| **←** | `JACKSON` | **PlaceName** | **Recipient** |
| **←** | `MS` | **StateName** | **SubaddressType** |
| **←** | `392151850` | **ZipCode** | **SubaddressIdentifier** |

**Your verdict:** `      `

---

## 66. `23499 STABLEWOOD CIRCLE PASS CHRISTIA MS 39571`
*MS — https://services1.arcgis.com/XwK5zAS8O0b6s3Tp/arcgis/rest/services/Pub*

| | Token | Model A | Model B |
|---|---|---|---|
| | `23499` | AddressNumber | AddressNumber |
| | `STABLEWOOD` | StreetName | StreetName |
| **←** | `CIRCLE` | **StreetName** | **StreetNamePostType** |
| **←** | `PASS` | **StreetNamePostType** | **PlaceName** |
| | `CHRISTIA` | PlaceName | PlaceName |
| | `MS` | StateName | StateName |
| | `39571` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 67. `C/O P O BOX 211 BILOXI MS 39533`
*MS — https://services1.arcgis.com/XwK5zAS8O0b6s3Tp/arcgis/rest/services/Pub*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `C/O` | **USPSBoxType** | **Recipient** |
| **←** | `P` | **USPSBoxType** | **Recipient** |
| **←** | `O` | **USPSBoxType** | **Recipient** |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `211` | USPSBoxID | USPSBoxID |
| | `BILOXI` | PlaceName | PlaceName |
| | `MS` | StateName | StateName |
| | `39533` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 68. `2178 HARMANSON VUE BILOXI MS 39531`
*MS — https://services1.arcgis.com/XwK5zAS8O0b6s3Tp/arcgis/rest/services/Pub*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2178` | AddressNumber | AddressNumber |
| | `HARMANSON` | StreetName | StreetName |
| **←** | `VUE` | **PlaceName** | **StreetName** |
| | `BILOXI` | PlaceName | PlaceName |
| | `MS` | StateName | StateName |
| | `39531` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 69. `OLSEN TERRY R TRUSTEE 24680 CRYSTAL BAY SWAN LAKE MT 59911-7857`
*MT — https://services2.arcgis.com/qQ6tqy9VSUry3ySt/arcgis/rest/services/9_1  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `OLSEN` | Recipient | Recipient |
| | `TERRY` | Recipient | Recipient |
| | `R` | Recipient | Recipient |
| | `TRUSTEE` | Recipient | Recipient |
| **←** | `24680` | **Recipient** | **AddressNumber** |
| **←** | `CRYSTAL` | **Recipient** | **StreetName** |
| **←** | `BAY` | **Recipient** | **StreetName** |
| | `SWAN` | PlaceName | PlaceName |
| | `LAKE` | PlaceName | PlaceName |
| | `MT` | StateName | StateName |
| | `59911-7857` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 70. `MYERS LOUIS 23148 MT HIGHWAY 35 BIGFORK MT 59911-8249`
*MT — https://services2.arcgis.com/qQ6tqy9VSUry3ySt/arcgis/rest/services/9_1  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `MYERS` | PlaceName | PlaceName |
| **←** | `LOUIS` | **StateName** | **PlaceName** |
| | `23148` | ZipCode | ZipCode |
| | `MT` | StreetNamePreType | StreetNamePreType |
| | `HIGHWAY` | StreetNamePreType | StreetNamePreType |
| | `35` | StreetName | StreetName |
| | `BIGFORK` | PlaceName | PlaceName |
| | `MT` | StateName | StateName |
| | `59911-8249` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 71. `8041 BELEWS CREEK STOKESDALE NC 27357`
*NC — https://gcgis.guilfordcountync.gov/arcgis/rest/services/GC_Cadastral_C  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `8041` | AddressNumber | AddressNumber |
| | `BELEWS` | StreetName | StreetName |
| **←** | `CREEK` | **StreetNamePostType** | **StreetName** |
| | `STOKESDALE` | PlaceName | PlaceName |
| | `NC` | StateName | StateName |
| | `27357` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 72. `%KP HAVENS LLC 2705 E AVE F BISMARCK ND 58501-3170`
*ND — https://services2.arcgis.com/8r0lsT7QHelkANsD/arcgis/rest/services/Tax*

| | Token | Model A | Model B |
|---|---|---|---|
| | `KP` | Recipient | Recipient |
| | `HAVENS` | Recipient | Recipient |
| | `LLC` | Recipient | Recipient |
| | `2705` | AddressNumber | AddressNumber |
| **←** | `E` | **StreetName** | **StreetNamePreDirectional** |
| **←** | `AVE` | **StreetNamePostType** | **StreetNamePreType** |
| **←** | `F` | **PlaceName** | **StreetName** |
| | `BISMARCK` | PlaceName | PlaceName |
| | `ND` | StateName | StateName |
| | `58501-3170` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 73. `1910 ROAD M GUIDE ROCK NE 68942`
*NE — https://services2.arcgis.com/iTf0MCf7KYGMrPY1/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1910` | AddressNumber | AddressNumber |
| | `ROAD` | StreetNamePreType | StreetNamePreType |
| | `M` | StreetName | StreetName |
| | `GUIDE` | StreetName | StreetName |
| **←** | `ROCK` | **StreetName** | **PlaceName** |
| **←** | `NE` | **StreetNamePostDirectional** | **StateName** |
| | `68942` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 74. `2854 COUNTY ROAD A VALPARAISO NE 68065-0000`
*NE — https://services2.arcgis.com/iTf0MCf7KYGMrPY1/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2854` | AddressNumber | AddressNumber |
| | `COUNTY` | StreetNamePreType | StreetNamePreType |
| | `ROAD` | StreetNamePreType | StreetNamePreType |
| | `A` | StreetName | StreetName |
| **←** | `VALPARAISO` | **PlaceName** | **StreetName** |
| **←** | `NE` | **StateName** | **StreetNamePostDirectional** |
| **←** | `68065-0000` | **ZipCode** | **OccupancyIdentifier** |

**Your verdict:** `      `

---

## 75. `2946 COUNTY ROAD B VALPARAISO NE 68065-8675`
*NE — https://services2.arcgis.com/iTf0MCf7KYGMrPY1/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2946` | AddressNumber | AddressNumber |
| **←** | `COUNTY` | **StreetNamePreType** | **StreetName** |
| **←** | `ROAD` | **StreetNamePreType** | **StreetName** |
| **←** | `B` | **StreetName** | **StreetNamePostType** |
| | `VALPARAISO` | PlaceName | PlaceName |
| | `NE` | StateName | StateName |
| | `68065-8675` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 76. `132 CASE DRIVE SOUTH PLAINFIELD, NJ 07080`
*NJ — https://services1.arcgis.com/WAUuvHqqP3le2PMh/arcgis/rest/services/New  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `132` | AddressNumber | AddressNumber |
| | `CASE` | StreetName | StreetName |
| | `DRIVE` | StreetNamePostType | StreetNamePostType |
| **←** | `SOUTH` | **StreetNamePostDirectional** | **PlaceName** |
| | `PLAINFIELD,` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07080` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 77. `162-64 IRVINE TURNER NEWARK, NJ 07103`
*NJ — https://services1.arcgis.com/WAUuvHqqP3le2PMh/arcgis/rest/services/New  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `162-64` | AddressNumber | AddressNumber |
| | `IRVINE` | StreetName | StreetName |
| **←** | `TURNER` | **PlaceName** | **StreetName** |
| | `NEWARK,` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07103` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 78. `260CHESTNUT ST. 2ND FLOOR NEWARK, NJ 07105`
*NJ — https://services1.arcgis.com/WAUuvHqqP3le2PMh/arcgis/rest/services/New  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `260CHESTNUT` | **StreetName** | **AddressNumber** |
| | `ST.` | StreetNamePostType | StreetNamePostType |
| | `2ND` | OccupancyIdentifier | OccupancyIdentifier |
| | `FLOOR` | OccupancyType | OccupancyType |
| | `NEWARK,` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07105` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 79. `58 VOSE AVENUE SOUTH ORANGE, NJ 07079`
*NJ — https://services1.arcgis.com/WAUuvHqqP3le2PMh/arcgis/rest/services/New  ·  _lineage-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `58` | AddressNumber | AddressNumber |
| | `VOSE` | StreetName | StreetName |
| | `AVENUE` | StreetNamePostType | StreetNamePostType |
| **←** | `SOUTH` | **PlaceName** | **StreetNamePostDirectional** |
| | `ORANGE,` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07079` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 80. `4895 CAMINO DOS VIDAS LAS CRUCES NM 88012`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `4895` | AddressNumber | AddressNumber |
| **←** | `CAMINO` | **StreetNamePreType** | **StreetName** |
| | `DOS` | StreetName | StreetName |
| **←** | `VIDAS` | **StreetName** | **PlaceName** |
| **←** | `LAS` | **StreetName** | **PlaceName** |
| | `CRUCES` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88012` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 81. `2962 VALLE VISTA LAS CRUCES NM 88011`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2962` | AddressNumber | AddressNumber |
| | `VALLE` | StreetName | StreetName |
| **←** | `VISTA` | **StreetNamePostType** | **StreetName** |
| | `LAS` | PlaceName | PlaceName |
| | `CRUCES` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88011` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 82. `5424 HORSE RIDGE WAY BONITA CA 91902`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5424` | AddressNumber | AddressNumber |
| | `HORSE` | StreetName | StreetName |
| **←** | `RIDGE` | **StreetNamePostType** | **StreetName** |
| **←** | `WAY` | **PlaceName** | **StreetNamePostType** |
| | `BONITA` | PlaceName | PlaceName |
| | `CA` | StateName | StateName |
| | `91902` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 83. `5800 STERN DRIVE H 5 LAS CRUCES NM 88001`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5800` | AddressNumber | AddressNumber |
| | `STERN` | StreetName | StreetName |
| | `DRIVE` | StreetNamePostType | StreetNamePostType |
| **←** | `H` | **SubaddressType** | **OccupancyIdentifier** |
| **←** | `5` | **SubaddressIdentifier** | **OccupancyIdentifier** |
| | `LAS` | PlaceName | PlaceName |
| | `CRUCES` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88001` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 84. `3250 CALLE RANCHO CABALLO LAS CRUCES NM 88012`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3250` | AddressNumber | AddressNumber |
| | `CALLE` | StreetName | StreetName |
| | `RANCHO` | StreetName | StreetName |
| **←** | `CABALLO` | **StreetName** | **PlaceName** |
| | `LAS` | PlaceName | PlaceName |
| | `CRUCES` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88012` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 85. `7 CAM MONTUOSO SANTA FE NM 87506`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `7` | AddressNumber | AddressNumber |
| **←** | `CAM` | **StreetName** | **StreetNamePreType** |
| | `MONTUOSO` | StreetName | StreetName |
| | `SANTA` | PlaceName | PlaceName |
| | `FE` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `87506` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 86. `4871 CAMINO DOS VIDAS LAS CRUCES NM 88012`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `4871` | AddressNumber | AddressNumber |
| **←** | `CAMINO` | **StreetNamePreType** | **StreetName** |
| | `DOS` | StreetName | StreetName |
| **←** | `VIDAS` | **StreetName** | **PlaceName** |
| **←** | `LAS` | **StreetName** | **PlaceName** |
| | `CRUCES` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88012` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 87. `RT 2 1600 W OHARA RD ANTHONY NM 88021`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `RT` | **SubaddressType** | **OccupancyType** |
| **←** | `2` | **SubaddressIdentifier** | **OccupancyIdentifier** |
| **←** | `1600` | **AddressNumber** | **OccupancyIdentifier** |
| | `W` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `OHARA` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| | `ANTHONY` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88021` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 88. `4883 CAMINO DOS VIDAS LAS CRUCES NM 88012`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `4883` | AddressNumber | AddressNumber |
| **←** | `CAMINO` | **StreetNamePreType** | **StreetName** |
| | `DOS` | StreetName | StreetName |
| **←** | `VIDAS` | **StreetName** | **PlaceName** |
| **←** | `LAS` | **StreetName** | **PlaceName** |
| | `CRUCES` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88012` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 89. `1704 CALLE DE SUENOS LAS CRUCES NM 88001`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1704` | AddressNumber | AddressNumber |
| | `CALLE` | StreetName | StreetName |
| | `DE` | StreetName | StreetName |
| **←** | `SUENOS` | **StreetName** | **PlaceName** |
| | `LAS` | PlaceName | PlaceName |
| | `CRUCES` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88001` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 90. `3220 CALLE RANCHO CABALLO LAS CRUCES NM 88012`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3220` | AddressNumber | AddressNumber |
| | `CALLE` | StreetName | StreetName |
| | `RANCHO` | StreetName | StreetName |
| **←** | `CABALLO` | **StreetName** | **PlaceName** |
| | `LAS` | PlaceName | PlaceName |
| | `CRUCES` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88012` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 91. `210 E IDAHO LAS CRUCES NM 88005`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `210` | AddressNumber | AddressNumber |
| | `E` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `IDAHO` | StreetName | StreetName |
| **←** | `LAS` | **StreetName** | **PlaceName** |
| | `CRUCES` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `88005` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 92. `1575 NORTH GREEN MOUNATIN ROAD SUITE 300 O FALLON IL 62269`
*NM — https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1575` | AddressNumber | AddressNumber |
| | `NORTH` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `GREEN` | StreetName | StreetName |
| | `MOUNATIN` | StreetName | StreetName |
| | `ROAD` | StreetNamePostType | StreetNamePostType |
| | `SUITE` | OccupancyType | OccupancyType |
| | `300` | OccupancyIdentifier | OccupancyIdentifier |
| **←** | `O` | **PlaceName** | **OccupancyIdentifier** |
| | `FALLON` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `62269` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 93. `PO BOX 18451 SERIES S LLC RENO NV 89511`
*NV — https://services.arcgis.com/iCGWaR7ZHc5saRIl/arcgis/rest/services/Nigh*

| | Token | Model A | Model B |
|---|---|---|---|
| | `PO` | USPSBoxType | USPSBoxType |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `18451` | USPSBoxID | USPSBoxID |
| **←** | `SERIES` | **NotAddress** | **PlaceName** |
| **←** | `S` | **NotAddress** | **PlaceName** |
| **←** | `LLC` | **NotAddress** | **PlaceName** |
| | `RENO` | PlaceName | PlaceName |
| | `NV` | StateName | StateName |
| | `89511` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 94. `NOT SUPPLIED NV 00000`
*NV — https://services.arcgis.com/iCGWaR7ZHc5saRIl/arcgis/rest/services/Nigh*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `NOT` | **PlaceName** | **StreetName** |
| | `SUPPLIED` | PlaceName | PlaceName |
| | `NV` | StateName | StateName |
| | `00000` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 95. `PO BOX 1900 C/O PROPERTY MANAGEMENT RENO NV 89505`
*NV — https://services.arcgis.com/iCGWaR7ZHc5saRIl/arcgis/rest/services/Nigh*

| | Token | Model A | Model B |
|---|---|---|---|
| | `PO` | USPSBoxType | USPSBoxType |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `1900` | USPSBoxID | USPSBoxID |
| **←** | `C/O` | **PlaceName** | **Recipient** |
| **←** | `PROPERTY` | **PlaceName** | **Recipient** |
| **←** | `MANAGEMENT` | **PlaceName** | **Recipient** |
| | `RENO` | PlaceName | PlaceName |
| | `NV` | StateName | StateName |
| | `89505` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 96. `4232 DESERT HIGHLANDS DR C/O MICHAEL MCTIGUE SPARKS NV 89436`
*NV — https://services.arcgis.com/iCGWaR7ZHc5saRIl/arcgis/rest/services/Nigh*

| | Token | Model A | Model B |
|---|---|---|---|
| | `4232` | AddressNumber | AddressNumber |
| | `DESERT` | StreetName | StreetName |
| | `HIGHLANDS` | StreetName | StreetName |
| | `DR` | StreetNamePostType | StreetNamePostType |
| **←** | `C/O` | **Recipient** | **PlaceName** |
| **←** | `MICHAEL` | **Recipient** | **PlaceName** |
| **←** | `MCTIGUE` | **Recipient** | **PlaceName** |
| | `SPARKS` | PlaceName | PlaceName |
| | `NV` | StateName | StateName |
| | `89436` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 97. `1001 E 9TH ST BLDG A ATTN COMMUNITY SERVICES DEPT RENO NV 89512`
*NV — https://services.arcgis.com/iCGWaR7ZHc5saRIl/arcgis/rest/services/Nigh*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1001` | AddressNumber | AddressNumber |
| | `E` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `9TH` | StreetName | StreetName |
| | `ST` | StreetNamePostType | StreetNamePostType |
| **←** | `BLDG` | **SubaddressType** | **OccupancyType** |
| **←** | `A` | **SubaddressIdentifier** | **OccupancyIdentifier** |
| | `ATTN` | Recipient | Recipient |
| | `COMMUNITY` | Recipient | Recipient |
| | `SERVICES` | Recipient | Recipient |
| | `DEPT` | Recipient | Recipient |
| | `RENO` | PlaceName | PlaceName |
| | `NV` | StateName | StateName |
| | `89512` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 98. `11661 SAN VICENTE BLVD STE 301 C/O HOROWITZ GROUP LOS ANGELES CA 90049`
*NV — https://services.arcgis.com/iCGWaR7ZHc5saRIl/arcgis/rest/services/Nigh*

| | Token | Model A | Model B |
|---|---|---|---|
| | `11661` | AddressNumber | AddressNumber |
| | `SAN` | StreetName | StreetName |
| | `VICENTE` | StreetName | StreetName |
| | `BLVD` | StreetNamePostType | StreetNamePostType |
| | `STE` | OccupancyType | OccupancyType |
| | `301` | OccupancyIdentifier | OccupancyIdentifier |
| **←** | `C/O` | **Recipient** | **PlaceName** |
| **←** | `HOROWITZ` | **Recipient** | **PlaceName** |
| **←** | `GROUP` | **Recipient** | **PlaceName** |
| **←** | `LOS` | **Recipient** | **PlaceName** |
| | `ANGELES` | PlaceName | PlaceName |
| | `CA` | StateName | StateName |
| | `90049` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 99. `843 County Route 16 Beaver Dams NY 14812`
*NY — https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `843` | AddressNumber | AddressNumber |
| | `County` | StreetNamePreType | StreetNamePreType |
| | `Route` | StreetNamePreType | StreetNamePreType |
| | `16` | StreetName | StreetName |
| **←** | `Beaver` | **StreetName** | **PlaceName** |
| | `Dams` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `14812` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 100. `38 Reeves Ave East Farmingdale NY 11735`
*NY — https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `38` | AddressNumber | AddressNumber |
| | `Reeves` | StreetName | StreetName |
| | `Ave` | StreetNamePostType | StreetNamePostType |
| **←** | `East` | **StreetNamePostDirectional** | **PlaceName** |
| | `Farmingdale` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `11735` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 101. `877 A Riverview Rd Rexford NY 12148`
*NY — https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `877` | AddressNumber | AddressNumber |
| **←** | `A` | **AddressNumberSuffix** | **StreetName** |
| | `Riverview` | StreetName | StreetName |
| | `Rd` | StreetNamePostType | StreetNamePostType |
| | `Rexford` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `12148` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 102. `30 LEDGEWOOD COMMONS MILLWOOD NY 10546`
*NY — https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `30` | AddressNumber | AddressNumber |
| | `LEDGEWOOD` | StreetName | StreetName |
| **←** | `COMMONS` | **StreetNamePostType** | **StreetName** |
| | `MILLWOOD` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10546` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 103. `422 Druid Rd W Clearwater FL 33756`
*NY — https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `422` | AddressNumber | AddressNumber |
| | `Druid` | StreetName | StreetName |
| | `Rd` | StreetNamePostType | StreetNamePostType |
| **←** | `W` | **PlaceName** | **StreetNamePostDirectional** |
| | `Clearwater` | PlaceName | PlaceName |
| | `FL` | StateName | StateName |
| | `33756` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 104. `876 HERITAGE HILLS - UNIT SOMERS NY 10589`
*NY — https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `876` | AddressNumber | AddressNumber |
| | `HERITAGE` | StreetName | StreetName |
| **←** | `HILLS` | **StreetNamePostType** | **StreetName** |
| **←** | `UNIT` | **OccupancyType** | **StreetName** |
| | `SOMERS` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10589` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 105. `6116 Wilkins Trak Livonia NY 14487`
*NY — https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `6116` | AddressNumber | AddressNumber |
| | `Wilkins` | StreetName | StreetName |
| **←** | `Trak` | **StreetNamePostType** | **StreetName** |
| | `Livonia` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `14487` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 106. `52 East St 324 Nunda NY 14517`
*NY — https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `52` | AddressNumber | AddressNumber |
| **←** | `East` | **StreetNamePreDirectional** | **StreetName** |
| **←** | `St` | **StreetName** | **StreetNamePostType** |
| **←** | `324` | **StreetName** | **OccupancyIdentifier** |
| | `Nunda` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `14517` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 107. `870 HERITAGE HILLS SOMERS NY 10589`
*NY — https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `870` | AddressNumber | AddressNumber |
| | `HERITAGE` | StreetName | StreetName |
| **←** | `HILLS` | **StreetNamePostType** | **StreetName** |
| | `SOMERS` | PlaceName | PlaceName |
| | `NY` | StateName | StateName |
| | `10589` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 108. `6517 CLAY CT W CANAL WINCHESTER OH 43110-8519`
*OH — https://gis.franklincountyohio.gov/hosting/rest/services/ParcelFeature*

| | Token | Model A | Model B |
|---|---|---|---|
| | `6517` | AddressNumber | AddressNumber |
| | `CLAY` | StreetName | StreetName |
| | `CT` | StreetNamePostType | StreetNamePostType |
| **←** | `W` | **StreetNamePostDirectional** | **PlaceName** |
| | `CANAL` | PlaceName | PlaceName |
| | `WINCHESTER` | PlaceName | PlaceName |
| | `OH` | StateName | StateName |
| | `43110-8519` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 109. `5256 BETHEL REED PARK COLUMBUS OH 43220-1811`
*OH — https://gis.franklincountyohio.gov/hosting/rest/services/ParcelFeature*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5256` | AddressNumber | AddressNumber |
| | `BETHEL` | StreetName | StreetName |
| | `REED` | StreetName | StreetName |
| **←** | `PARK` | **StreetNamePostType** | **StreetName** |
| | `COLUMBUS` | PlaceName | PlaceName |
| | `OH` | StateName | StateName |
| | `43220-1811` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 110. `15141 COUNTY STREET 2720 MINCO OK 73059-9702`
*OK — https://services8.arcgis.com/euhkr1dAJeQBIjV0/arcgis/rest/services/Tax*

| | Token | Model A | Model B |
|---|---|---|---|
| | `15141` | AddressNumber | AddressNumber |
| | `COUNTY` | StreetName | StreetName |
| **←** | `STREET` | **StreetNamePostType** | **StreetName** |
| | `2720` | OccupancyIdentifier | OccupancyIdentifier |
| | `MINCO` | PlaceName | PlaceName |
| | `OK` | StateName | StateName |
| | `73059-9702` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 111. `3355 N Delta Hwy Space 99 Eugene OR 97408`
*OR — https://services3.arcgis.com/NbWCmkRTtvyr63CT/arcgis/rest/services/Tax*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3355` | AddressNumber | AddressNumber |
| | `N` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `Delta` | StreetName | StreetName |
| **←** | `Hwy` | **StreetName** | **StreetNamePostType** |
| **←** | `Space` | **StreetName** | **OccupancyType** |
| **←** | `99` | **StreetName** | **OccupancyIdentifier** |
| | `Eugene` | PlaceName | PlaceName |
| | `OR` | StateName | StateName |
| | `97408` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 112. `1515 A DOWEY CR LUGOFF SC 29078`
*SC — https://services9.arcgis.com/RvqSyw3diI7dTKo5/arcgis/rest/services/Fai*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1515` | AddressNumber | AddressNumber |
| **←** | `A` | **AddressNumberSuffix** | **StreetName** |
| | `DOWEY` | StreetName | StreetName |
| | `CR` | StreetNamePostType | StreetNamePostType |
| | `LUGOFF` | PlaceName | PlaceName |
| | `SC` | StateName | StateName |
| | `29078` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 113. `104 INWOOD ST - W BETHUNE SC 29009`
*SC — https://services9.arcgis.com/RvqSyw3diI7dTKo5/arcgis/rest/services/Fai*

| | Token | Model A | Model B |
|---|---|---|---|
| | `104` | AddressNumber | AddressNumber |
| | `INWOOD` | StreetName | StreetName |
| | `ST` | StreetNamePostType | StreetNamePostType |
| **←** | `W` | **PlaceName** | **StreetNamePostDirectional** |
| | `BETHUNE` | PlaceName | PlaceName |
| | `SC` | StateName | StateName |
| | `29009` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 114. `6500 E DAN RIDGE SIOUX FALLS SD 57110`
*SD — https://gis.siouxfalls.gov/arcgis/rest/services/Data/Property/MapServe*

| | Token | Model A | Model B |
|---|---|---|---|
| | `6500` | AddressNumber | AddressNumber |
| | `E` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `DAN` | StreetName | StreetName |
| **←** | `RIDGE` | **StreetNamePostType** | **StreetName** |
| | `SIOUX` | PlaceName | PlaceName |
| | `FALLS` | PlaceName | PlaceName |
| | `SD` | StateName | StateName |
| | `57110` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 115. `372 PARK CT N LA VERGNE TN 37086`
*TN — https://services5.arcgis.com/A5C0MR9xfkxVRwat/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `372` | AddressNumber | AddressNumber |
| | `PARK` | StreetName | StreetName |
| | `CT` | StreetNamePostType | StreetNamePostType |
| **←** | `N` | **StreetNamePostDirectional** | **PlaceName** |
| | `LA` | PlaceName | PlaceName |
| | `VERGNE` | PlaceName | PlaceName |
| | `TN` | StateName | StateName |
| | `37086` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 116. `5001 PLAZA ON THE LAKE, STE 200 AUSTIN TX 78746`
*TN — https://services5.arcgis.com/A5C0MR9xfkxVRwat/arcgis/rest/services/Par*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5001` | AddressNumber | AddressNumber |
| **←** | `PLAZA` | **StreetName** | **StreetNamePreType** |
| | `ON` | StreetName | StreetName |
| | `THE` | StreetName | StreetName |
| **←** | `LAKE,` | **StreetNamePostType** | **StreetName** |
| | `STE` | OccupancyType | OccupancyType |
| | `200` | OccupancyIdentifier | OccupancyIdentifier |
| | `AUSTIN` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78746` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 117. `5103 VILLAGE CREST SAN ANTONIO TX 78218`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5103` | AddressNumber | AddressNumber |
| | `VILLAGE` | StreetName | StreetName |
| **←** | `CREST` | **StreetNamePostType** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `ANTONIO` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78218` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 118. `3402 HEATHER BLF SAN ANTONIO TX 78259`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3402` | AddressNumber | AddressNumber |
| | `HEATHER` | StreetName | StreetName |
| **←** | `BLF` | **StreetNamePostType** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `ANTONIO` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78259` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 119. `19547 AZURE OAK SAN ANTONIO TX 78258`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `19547` | AddressNumber | AddressNumber |
| | `AZURE` | StreetName | StreetName |
| **←** | `OAK` | **PlaceName** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `ANTONIO` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78258` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 120. `3803 SPANISH BRANCH SAN ANTONIO TX 78222`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3803` | AddressNumber | AddressNumber |
| | `SPANISH` | StreetName | StreetName |
| **←** | `BRANCH` | **StreetNamePostType** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `ANTONIO` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78222` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 121. `7526 MONTE CRISTO SAN ANTONIO TX 78239`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `7526` | AddressNumber | AddressNumber |
| | `MONTE` | StreetName | StreetName |
| **←** | `CRISTO` | **StreetName** | **PlaceName** |
| | `SAN` | PlaceName | PlaceName |
| | `ANTONIO` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78239` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 122. `24903 SHINING ARROW SAN ANTONIO TX 78258`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `24903` | AddressNumber | AddressNumber |
| | `SHINING` | StreetName | StreetName |
| **←** | `ARROW` | **PlaceName** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `ANTONIO` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78258` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 123. `24930 FLYING ARROW SAN ANTONIO TX 78258`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `24930` | AddressNumber | AddressNumber |
| | `FLYING` | StreetName | StreetName |
| **←** | `ARROW` | **PlaceName** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `ANTONIO` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78258` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 124. `7030 GLEN PARK SAN ANTONIO TX 78239`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `7030` | AddressNumber | AddressNumber |
| | `GLEN` | StreetName | StreetName |
| **←** | `PARK` | **StreetNamePostType** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `ANTONIO` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78239` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 125. `15744 VIA SANTA PRADERA SAN DIEGO CA 92131`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `15744` | AddressNumber | AddressNumber |
| | `VIA` | StreetName | StreetName |
| **←** | `SANTA` | **PlaceName** | **StreetName** |
| **←** | `PRADERA` | **PlaceName** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `DIEGO` | PlaceName | PlaceName |
| | `CA` | StateName | StateName |
| | `92131` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 126. `7313 LAZY CANYON SAN ANTONIO TX 78252`
*TX — https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bex*

| | Token | Model A | Model B |
|---|---|---|---|
| | `7313` | AddressNumber | AddressNumber |
| | `LAZY` | StreetName | StreetName |
| **←** | `CANYON` | **StreetNamePostType** | **StreetName** |
| | `SAN` | PlaceName | PlaceName |
| | `ANTONIO` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78252` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 127. `5012 S TIMBER WY 413 MILLCREEK UT 84117`
*UT — https://services9.arcgis.com/XRrSFvEwSsReIxuA/arcgis/rest/services/Mil*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5012` | AddressNumber | AddressNumber |
| | `S` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `TIMBER` | StreetName | StreetName |
| **←** | `WY` | **StreetNamePostType** | **StreetName** |
| **←** | `413` | **OccupancyIdentifier** | **StreetName** |
| | `MILLCREEK` | PlaceName | PlaceName |
| | `UT` | StateName | StateName |
| | `84117` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 128. `5012 S TIMBER WY 309 MILLCREEK UT 84117`
*UT — https://services9.arcgis.com/XRrSFvEwSsReIxuA/arcgis/rest/services/Mil*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5012` | AddressNumber | AddressNumber |
| | `S` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `TIMBER` | StreetName | StreetName |
| **←** | `WY` | **StreetNamePostType** | **StreetName** |
| **←** | `309` | **OccupancyIdentifier** | **StreetName** |
| | `MILLCREEK` | PlaceName | PlaceName |
| | `UT` | StateName | StateName |
| | `84117` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 129. `REAL ESTATE DEPT # S3200 PO BOX 144575 SALT LAKE CITY UT 84114`
*UT — https://services9.arcgis.com/XRrSFvEwSsReIxuA/arcgis/rest/services/Mil*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `REAL` | **StreetName** | **LandmarkName** |
| **←** | `ESTATE` | **StreetNamePostType** | **LandmarkName** |
| | `DEPT` | SubaddressType | SubaddressType |
| | `#` | SubaddressIdentifier | SubaddressIdentifier |
| | `S3200` | SubaddressIdentifier | SubaddressIdentifier |
| | `PO` | USPSBoxType | USPSBoxType |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `144575` | USPSBoxID | USPSBoxID |
| | `SALT` | PlaceName | PlaceName |
| | `LAKE` | PlaceName | PlaceName |
| | `CITY` | PlaceName | PlaceName |
| | `UT` | StateName | StateName |
| | `84114` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 130. `23438 CTY HWY AA 8 RICHLAND CENTER WI 53581`
*WI — https://services3.arcgis.com/n6uYoouQZW75n5WI/arcgis/rest/services/Wis  ·  _aggregate-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `23438` | AddressNumber | AddressNumber |
| | `CTY` | StreetName | StreetName |
| **←** | `HWY` | **StreetNamePostType** | **StreetName** |
| **←** | `AA` | **SubaddressType** | **StreetName** |
| **←** | `8` | **SubaddressIdentifier** | **StreetName** |
| | `RICHLAND` | PlaceName | PlaceName |
| | `CENTER` | PlaceName | PlaceName |
| | `WI` | StateName | StateName |
| | `53581` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 131. `19731 COUNTY HWY Z RICHLAND CENTER WI 53581`
*WI — https://services3.arcgis.com/n6uYoouQZW75n5WI/arcgis/rest/services/Wis  ·  _aggregate-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `19731` | AddressNumber | AddressNumber |
| | `COUNTY` | StreetNamePreType | StreetNamePreType |
| | `HWY` | StreetNamePreType | StreetNamePreType |
| | `Z` | StreetName | StreetName |
| **←** | `RICHLAND` | **StreetName** | **PlaceName** |
| | `CENTER` | PlaceName | PlaceName |
| | `WI` | StateName | StateName |
| | `53581` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 132. `177 OAK DRIVE ADN, SPENCER, WV 25276`
*WV — https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/  ·  _aggregate-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `177` | AddressNumber | AddressNumber |
| | `OAK` | StreetName | StreetName |
| | `DRIVE` | StreetNamePostType | StreetNamePostType |
| **←** | `ADN,` | **StreetNamePostDirectional** | **PlaceName** |
| | `SPENCER,` | PlaceName | PlaceName |
| | `WV` | StateName | StateName |
| | `25276` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 133. `201 OAK DRIVE ADN, SPENCER, WV 25276`
*WV — https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/  ·  _aggregate-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `201` | AddressNumber | AddressNumber |
| | `OAK` | StreetName | StreetName |
| | `DRIVE` | StreetNamePostType | StreetNamePostType |
| **←** | `ADN,` | **StreetNamePostDirectional** | **PlaceName** |
| | `SPENCER,` | PlaceName | PlaceName |
| | `WV` | StateName | StateName |
| | `25276` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 134. `306 KEFFER HILL, SPENCER, WV 25276`
*WV — https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/  ·  _aggregate-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `306` | AddressNumber | AddressNumber |
| | `KEFFER` | StreetName | StreetName |
| **←** | `HILL,` | **StreetNamePostType** | **StreetName** |
| | `SPENCER,` | PlaceName | PlaceName |
| | `WV` | StateName | StateName |
| | `25276` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 135. `1244 COAL RIVER MTN RD, MT HOPE, WV 25880`
*WV — https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/  ·  _aggregate-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1244` | AddressNumber | AddressNumber |
| | `COAL` | StreetName | StreetName |
| | `RIVER` | StreetName | StreetName |
| **←** | `MTN` | **StreetNamePostType** | **StreetName** |
| **←** | `RD,` | **StreetNamePostDirectional** | **StreetNamePostType** |
| | `MT` | PlaceName | PlaceName |
| | `HOPE,` | PlaceName | PlaceName |
| | `WV` | StateName | StateName |
| | `25880` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 136. `205 OAK DRIVE ADN, SPENCER, WV 25276`
*WV — https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/  ·  _aggregate-sensitivity_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `205` | AddressNumber | AddressNumber |
| | `OAK` | StreetName | StreetName |
| | `DRIVE` | StreetNamePostType | StreetNamePostType |
| **←** | `ADN,` | **StreetNamePostDirectional** | **PlaceName** |
| | `SPENCER,` | PlaceName | PlaceName |
| | `WV` | StateName | StateName |
| | `25276` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## When you're done

Paste answers back in any form. They get un-blinded, stored with the approved label sequences, and the pre-registered gates compute from human verdicts only. Four numbers get reported together, per your rulings: the strict-cohort primary, both sensitivity cohorts labelled separately, and the primary repeated without Wyoming.

This is scoring attempt 1 of 2 against gold-2b. After the second, the set is spent and a fresh one is required for any further claim.