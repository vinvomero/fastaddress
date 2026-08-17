# Gold-2c label approval — 129 addresses

## What this is, and how it differs from rounds 7-9

Those rounds asked which of two parses was better. Those verdicts died with the candidate pair that produced them, which is why the last dev surface had only 69 usable records and could not tell a winner from a loser.

**This asks a different question: is the proposed parse correct?** Your answer is stored as the approved labelling for that address, and every future candidate gets scored against it forever, with no further review from you. Build it once, use it for the rest of the project.

## How to answer

- **`ok`** — the proposed labels are right.
- **A correction** — write what the disputed token(s) should be, e.g. `ST = StreetNamePostType` or `WEST, CALDWELL = PlaceName`. Only the tokens you mention change; everything else stands as proposed.
- **`skip`** — genuinely ambiguous, or you would be guessing. Stored unscoreable, never counted. Skipping is a real answer here, not a failure to answer.

Where a candidate model reads a token differently, its reading is shown in the **Alternative** column so you can see the live disagreement — but the question is still "what is correct", not "who wins". 84 records carry a disagreement; 45 are a seeded random audit of records where every model already agrees (those catch the cases where everyone is wrong together, like the Canadian postal codes in round 9).

---

## 1. `207 DAPHNEMONT DR EXT DAPHNE AL 36526`
*AL*

| Token | Proposed | Alternative |
|---|---|---|
| `207` | AddressNumber |  |
| `DAPHNEMONT` | StreetName |  |
| `DR` | StreetNamePostType |  |
| `EXT` **←** | **StreetNamePostModifier** | PlaceName (v43), PlaceName (v50) |
| `DAPHNE` | PlaceName |  |
| `AL` | StateName |  |
| `36526` | ZipCode |  |

**Your answer:** `      `

---

## 2. `22421 PHILLIPSVILLE ROAD EXT BAY MINETTE AL 36507`
*AL*

| Token | Proposed | Alternative |
|---|---|---|
| `22421` | AddressNumber |  |
| `PHILLIPSVILLE` | StreetName |  |
| `ROAD` | StreetNamePostType |  |
| `EXT` **←** | **StreetNamePostModifier** | PlaceName (v43), PlaceName (v50) |
| `BAY` | PlaceName |  |
| `MINETTE` | PlaceName |  |
| `AL` | StateName |  |
| `36507` | ZipCode |  |

**Your answer:** `      `

---

## 3. `7258 CO RD B WINNECONNE WI 54986`
*AL*

| Token | Proposed | Alternative |
|---|---|---|
| `7258` | AddressNumber |  |
| `CO` **←** | **StreetName** | StreetNamePreType (v43), StreetNamePreType (v50) |
| `RD` **←** | **StreetNamePostType** | StreetNamePreType (v43), StreetNamePreType (v50) |
| `B` **←** | **PlaceName** | StreetName (v43), StreetName (v50) |
| `WINNECONNE` | PlaceName |  |
| `WI` | StateName |  |
| `54986` | ZipCode |  |

**Your answer:** `      `

---

## 4. `8401 TIMBER CREEK DRIVE PIKE ROAD AL 36064`
*AL*

| Token | Proposed | Alternative |
|---|---|---|
| `8401` | AddressNumber |  |
| `TIMBER` | StreetName |  |
| `CREEK` | StreetName |  |
| `DRIVE` **←** | **StreetName** | StreetNamePostType (v43), StreetNamePostType (v50) |
| `PIKE` **←** | **StreetName** | PlaceName (v43), PlaceName (v50) |
| `ROAD` **←** | **StreetName** | PlaceName (v43), PlaceName (v50) |
| `AL` **←** | **StreetNamePostType** | StateName (v43), StateName (v50) |
| `36064` | ZipCode |  |

**Your answer:** `      `

---

## 5. `TIMES SQUARE TOWER NEW YORK NY 10036`
*AL*

| Token | Proposed | Alternative |
|---|---|---|
| `TIMES` | BuildingName |  |
| `SQUARE` | BuildingName |  |
| `TOWER` | BuildingName |  |
| `NEW` **←** | **BuildingName** | PlaceName (v43), PlaceName (v50) |
| `YORK` | PlaceName |  |
| `NY` | StateName |  |
| `10036` | ZipCode |  |

**Your answer:** `      `

---

## 6. `%Denise Deluca 10541 Edgerton Rd North Royalton, OH 441335546`
*AZ*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `Denise` | Recipient |
| `Deluca` | Recipient |
| `10541` | AddressNumber |
| `Edgerton` | StreetName |
| `Rd` | StreetNamePostType |
| `North` | PlaceName |
| `Royalton,` | PlaceName |
| `OH` | StateName |
| `441335546` | ZipCode |

**Your answer:** `      `

---

## 7. `10206 Barbeque Bay Converse, TX 781094418`
*AZ*

| Token | Proposed | Alternative |
|---|---|---|
| `10206` | AddressNumber |  |
| `Barbeque` | StreetName |  |
| `Bay` **←** | **PlaceName** | StreetName (v43), StreetName (v50) |
| `Converse,` | PlaceName |  |
| `TX` | StateName |  |
| `781094418` | ZipCode |  |

**Your answer:** `      `

---

## 8. `1525 W Oakland Ave Spc 12 Hemet, CA 925432658`
*AZ*

| Token | Proposed | Alternative |
|---|---|---|
| `1525` | AddressNumber |  |
| `W` | StreetNamePreDirectional |  |
| `Oakland` | StreetName |  |
| `Ave` | StreetNamePostType |  |
| `Spc` **←** | **SubaddressType** | OccupancyType (v43), OccupancyType (v50) |
| `12` **←** | **SubaddressIdentifier** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `Hemet,` | PlaceName |  |
| `CA` | StateName |  |
| `925432658` | ZipCode |  |

**Your answer:** `      `

---

## 9. `2645 E Southern Ave A239 Tempe, AZ 85282`
*AZ*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `2645` | AddressNumber |
| `E` | StreetNamePreDirectional |
| `Southern` | StreetName |
| `Ave` | StreetNamePostType |
| `A239` | OccupancyIdentifier |
| `Tempe,` | PlaceName |
| `AZ` | StateName |
| `85282` | ZipCode |

**Your answer:** `      `

---

## 10. `35108 Harvest Ridge Ln Alpharetta, GA 300228634`
*AZ*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `35108` | AddressNumber |
| `Harvest` | StreetName |
| `Ridge` | StreetName |
| `Ln` | StreetNamePostType |
| `Alpharetta,` | PlaceName |
| `GA` | StateName |
| `300228634` | ZipCode |

**Your answer:** `      `

---

## 11. `6011 E Calle Del Paisano Scottsdale, AZ 852514210`
*AZ*

| Token | Proposed | Alternative |
|---|---|---|
| `6011` | AddressNumber |  |
| `E` | StreetNamePreDirectional |  |
| `Calle` | StreetName |  |
| `Del` | StreetName |  |
| `Paisano` **←** | **PlaceName** | StreetName (v43), StreetName (v50) |
| `Scottsdale,` | PlaceName |  |
| `AZ` | StateName |  |
| `852514210` | ZipCode |  |

**Your answer:** `      `

---

## 12. `6840 N Camino De Fray Marcos Tucson, AZ 857181018`
*AZ*

| Token | Proposed | Alternative |
|---|---|---|
| `6840` | AddressNumber |  |
| `N` | StreetNamePreDirectional |  |
| `Camino` **←** | **StreetNamePreType** | StreetName (v43), StreetName (v50) |
| `De` | StreetName |  |
| `Fray` | StreetName |  |
| `Marcos` **←** | **PlaceName** | StreetName (v43), StreetName (v50) |
| `Tucson,` | PlaceName |  |
| `AZ` | StateName |  |
| `857181018` | ZipCode |  |

**Your answer:** `      `

---

## 13. `C/O Francine Van Der Poel 4035 Us Highway 60 Show Low, AZ 859019770`
*AZ*

| Token | Proposed | Alternative |
|---|---|---|
| `C/O` | Recipient |  |
| `Francine` | Recipient |  |
| `Van` | Recipient |  |
| `Der` | Recipient |  |
| `Poel` | Recipient |  |
| `4035` | AddressNumber |  |
| `Us` | StreetNamePreType |  |
| `Highway` | StreetNamePreType |  |
| `60` | StreetName |  |
| `Show` **←** | **PlaceName** | StreetName (v43), StreetName (v50) |
| `Low,` | PlaceName |  |
| `AZ` | StateName |  |
| `859019770` | ZipCode |  |

**Your answer:** `      `

---

## 14. `C/O Jane Gissi 14228 59Th Ave W Edmonds, WA 980263710`
*AZ*

| Token | Proposed | Alternative |
|---|---|---|
| `C/O` | Recipient |  |
| `Jane` | Recipient |  |
| `Gissi` | Recipient |  |
| `14228` | AddressNumber |  |
| `59Th` | StreetName |  |
| `Ave` | StreetNamePostType |  |
| `W` **←** | **PlaceName** | StreetNamePostDirectional (v43), StreetNamePostDirectional (v50) |
| `Edmonds,` | PlaceName |  |
| `WA` | StateName |  |
| `980263710` | ZipCode |  |

**Your answer:** `      `

---

## 15. `1337 GAY CR LONGMONT CO 80501-1876`
*CO*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `1337` | AddressNumber |
| `GAY` | StreetName |
| `CR` | StreetNamePostType |
| `LONGMONT` | PlaceName |
| `CO` | StateName |
| `80501-1876` | ZipCode |

**Your answer:** `      `

---

## 16. `1514 SIDON CR 144 LAFAYETTE CO 80026`
*CO*

| Token | Proposed | Alternative |
|---|---|---|
| `1514` | AddressNumber |  |
| `SIDON` | StreetName |  |
| `CR` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `144` **←** | **OccupancyIdentifier** | StreetName (v43), StreetName (v50) |
| `LAFAYETTE` | PlaceName |  |
| `CO` | StateName |  |
| `80026` | ZipCode |  |

**Your answer:** `      `

---

## 17. `4800 N BROADWAY BOULDER CO 80304`
*CO*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `4800` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `BROADWAY` | StreetName |
| `BOULDER` | PlaceName |
| `CO` | StateName |
| `80304` | ZipCode |

**Your answer:** `      `

---

## 18. `ADDRESS UNKNOWN ??`
*CO*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `ADDRESS` | Recipient |
| `UNKNOWN` | Recipient |

**Your answer:** `      `

---

## 19. `C/O BOULDER COUNTY PARKS & OPEN SPACE 5201 ST VRAIN RD BLDG 1 LONGMONT CO 80503`
*CO*

| Token | Proposed | Alternative |
|---|---|---|
| `C/O` | Recipient |  |
| `BOULDER` | Recipient |  |
| `COUNTY` | Recipient |  |
| `PARKS` | Recipient |  |
| `&` | Recipient |  |
| `OPEN` | Recipient |  |
| `SPACE` | Recipient |  |
| `5201` | AddressNumber |  |
| `ST` | StreetName |  |
| `VRAIN` | StreetName |  |
| `RD` | StreetNamePostType |  |
| `BLDG` **←** | **SubaddressType** | OccupancyType (v43), OccupancyType (v50) |
| `1` **←** | **SubaddressIdentifier** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `LONGMONT` | PlaceName |  |
| `CO` | StateName |  |
| `80503` | ZipCode |  |

**Your answer:** `      `

---

## 20. `MANUEL GONZALEA 1806 COLLYER ST LONGMONT CO 80501`
*CO*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `MANUEL` | Recipient |
| `GONZALEA` | Recipient |
| `1806` | AddressNumber |
| `COLLYER` | StreetName |
| `ST` | StreetNamePostType |
| `LONGMONT` | PlaceName |
| `CO` | StateName |
| `80501` | ZipCode |

**Your answer:** `      `

---

## 21. `% MCLANE & MCLANE ATTORNEYS 275 N CLEARWATER-LARGO RD LARGO FL 33770`
*FL*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `MCLANE` | Recipient |
| `&` | Recipient |
| `MCLANE` | Recipient |
| `ATTORNEYS` | Recipient |
| `275` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `CLEARWATER-LARGO` | StreetName |
| `RD` | StreetNamePostType |
| `LARGO` | PlaceName |
| `FL` | StateName |
| `33770` | ZipCode |

**Your answer:** `      `

---

## 22. `206 MOORE AVE STE C PMB C DAYTONA BEACH SHORES FL 32118`
*FL*

| Token | Proposed | Alternative |
|---|---|---|
| `206` | AddressNumber |  |
| `MOORE` | StreetName |  |
| `AVE` | StreetNamePostType |  |
| `STE` | OccupancyType |  |
| `C` | OccupancyIdentifier |  |
| `PMB` **←** | **SubaddressType** | OccupancyType (v43), OccupancyType (v50) |
| `C` **←** | **SubaddressIdentifier** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `DAYTONA` | PlaceName |  |
| `BEACH` | PlaceName |  |
| `SHORES` | PlaceName |  |
| `FL` | StateName |  |
| `32118` | ZipCode |  |

**Your answer:** `      `

---

## 23. `3780 MILANO LAKES UNIT 109 NAPLES FL 34114`
*FL*

| Token | Proposed | Alternative |
|---|---|---|
| `3780` | AddressNumber |  |
| `MILANO` | StreetName |  |
| `LAKES` **←** | **StreetNamePostType** | StreetName (v50) |
| `UNIT` | OccupancyType |  |
| `109` | OccupancyIdentifier |  |
| `NAPLES` | PlaceName |  |
| `FL` | StateName |  |
| `34114` | ZipCode |  |

**Your answer:** `      `

---

## 24. `606 N DUSS ST NEW SMYRNA BEACH FL 32168`
*FL*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `606` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `DUSS` | StreetName |
| `ST` | StreetNamePostType |
| `NEW` | PlaceName |
| `SMYRNA` | PlaceName |
| `BEACH` | PlaceName |
| `FL` | StateName |
| `32168` | ZipCode |

**Your answer:** `      `

---

## 25. `770 CR 485 LAKE PANASOFFKEE FL 33538`
*FL*

| Token | Proposed | Alternative |
|---|---|---|
| `770` | AddressNumber |  |
| `CR` | StreetNamePreType |  |
| `485` | StreetName |  |
| `LAKE` **←** | **PlaceName** | StreetName (v43), StreetName (v50) |
| `PANASOFFKEE` | PlaceName |  |
| `FL` | StateName |  |
| `33538` | ZipCode |  |

**Your answer:** `      `

---

## 26. `825 S CR 3 PIERSON FL 32180`
*FL*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `825` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `CR` | StreetNamePreType |
| `3` | StreetName |
| `PIERSON` | PlaceName |
| `FL` | StateName |
| `32180` | ZipCode |

**Your answer:** `      `

---

## 27. `4 CAIRNBRAE HILLS MASON CITY IA 50401`
*IA*

| Token | Proposed | Alternative |
|---|---|---|
| `4` | AddressNumber |  |
| `CAIRNBRAE` | StreetName |  |
| `HILLS` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `MASON` | PlaceName |  |
| `CITY` | PlaceName |  |
| `IA` | StateName |  |
| `50401` | ZipCode |  |

**Your answer:** `      `

---

## 28. `C/O CUSTODIAN FBO PAUL C BEHR IRA 6993 SOUTH ANDES CIR CENTENNIAL CO 80016`
*IA*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `C/O` | Recipient |
| `CUSTODIAN` | Recipient |
| `FBO` | Recipient |
| `PAUL` | Recipient |
| `C` | Recipient |
| `BEHR` | Recipient |
| `IRA` | Recipient |
| `6993` | AddressNumber |
| `SOUTH` | StreetNamePreDirectional |
| `ANDES` | StreetName |
| `CIR` | StreetNamePostType |
| `CENTENNIAL` | PlaceName |
| `CO` | StateName |
| `80016` | ZipCode |

**Your answer:** `      `

---

## 29. `C/O CUSTODIAN FBO PAUL C. BEHR IRA 100% 6993 SOUTH ANDES CIR CENTENNIAL CO 80016`
*IA*

| Token | Proposed | Alternative |
|---|---|---|
| `C/O` | Recipient |  |
| `CUSTODIAN` | Recipient |  |
| `FBO` | Recipient |  |
| `PAUL` | Recipient |  |
| `C.` | Recipient |  |
| `BEHR` | Recipient |  |
| `IRA` **←** | **Recipient** | SubaddressType (v43), SubaddressType (v50) |
| `100%` | SubaddressIdentifier |  |
| `6993` | AddressNumber |  |
| `SOUTH` | StreetNamePreDirectional |  |
| `ANDES` | StreetName |  |
| `CIR` | StreetNamePostType |  |
| `CENTENNIAL` | PlaceName |  |
| `CO` | StateName |  |
| `80016` | ZipCode |  |

**Your answer:** `      `

---

## 30. `C/O TRUSTEE OF THE KATHRYN A. SNYDER TRUST AGMT 2415 S LAKEVIEW CT CLEAR LAKE IA 50428`
*IA*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `C/O` | Recipient |
| `TRUSTEE` | Recipient |
| `OF` | Recipient |
| `THE` | Recipient |
| `KATHRYN` | Recipient |
| `A.` | Recipient |
| `SNYDER` | Recipient |
| `TRUST` | Recipient |
| `AGMT` | Recipient |
| `2415` | AddressNumber |
| `S` | StreetNamePreDirectional |
| `LAKEVIEW` | StreetName |
| `CT` | StreetNamePostType |
| `CLEAR` | PlaceName |
| `LAKE` | PlaceName |
| `IA` | StateName |
| `50428` | ZipCode |

**Your answer:** `      `

---

## 31. `TRUSTEE OF THE RONALD J BEHR REVOCABLE TRUST CREATED AUGUST 11, 2005 PO BOX 670 ROCKWELL IA 50469`
*IA*

| Token | Proposed | Alternative |
|---|---|---|
| `TRUSTEE` | Recipient |  |
| `OF` | Recipient |  |
| `THE` | Recipient |  |
| `RONALD` | Recipient |  |
| `J` | Recipient |  |
| `BEHR` | Recipient |  |
| `REVOCABLE` | Recipient |  |
| `TRUST` | Recipient |  |
| `CREATED` | Recipient |  |
| `AUGUST` **←** | **Recipient** | SubaddressType (v43), SubaddressType (v50) |
| `11,` | SubaddressIdentifier |  |
| `2005` | SubaddressIdentifier |  |
| `PO` | USPSBoxType |  |
| `BOX` | USPSBoxType |  |
| `670` | USPSBoxID |  |
| `ROCKWELL` | PlaceName |  |
| `IA` | StateName |  |
| `50469` | ZipCode |  |

**Your answer:** `      `

---

## 32. `%MARY FISCHBACH 1304 FRANKLIN ST ROCK FALLS IL 61071`
*IL*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `MARY` | Recipient |
| `FISCHBACH` | Recipient |
| `1304` | AddressNumber |
| `FRANKLIN` | StreetName |
| `ST` | StreetNamePostType |
| `ROCK` | PlaceName |
| `FALLS` | PlaceName |
| `IL` | StateName |
| `61071` | ZipCode |

**Your answer:** `      `

---

## 33. `%ROD W COPELAND 106 LAFAYETTE ST, PO BOX 1 PROPHETSTOWN IL 61277`
*IL*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `ROD` | Recipient |
| `W` | Recipient |
| `COPELAND` | Recipient |
| `106` | AddressNumber |
| `LAFAYETTE` | StreetName |
| `ST,` | StreetNamePostType |
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `1` | USPSBoxID |
| `PROPHETSTOWN` | PlaceName |
| `IL` | StateName |
| `61277` | ZipCode |

**Your answer:** `      `

---

## 34. `%SANTIAGO & BERTA MARTINEZ 614 W 14TH ST ROCK FALLS IL 61071`
*IL*

| Token | Proposed | Alternative |
|---|---|---|
| `SANTIAGO` **←** | **Recipient** | BuildingName (v43) |
| `&` **←** | **Recipient** | BuildingName (v43) |
| `BERTA` **←** | **Recipient** | BuildingName (v43) |
| `MARTINEZ` **←** | **Recipient** | BuildingName (v43) |
| `614` | AddressNumber |  |
| `W` | StreetNamePreDirectional |  |
| `14TH` | StreetName |  |
| `ST` | StreetNamePostType |  |
| `ROCK` | PlaceName |  |
| `FALLS` | PlaceName |  |
| `IL` | StateName |  |
| `61071` | ZipCode |  |

**Your answer:** `      `

---

## 35. `1004 AVE B ROCK FALLS IL 610710000`
*IL*

| Token | Proposed | Alternative |
|---|---|---|
| `1004` | AddressNumber |  |
| `AVE` **←** | **StreetNamePostType** | StreetNamePreType (v43), StreetName (v50) |
| `B` **←** | **PlaceName** | StreetName (v43), StreetNamePostType (v50) |
| `ROCK` | PlaceName |  |
| `FALLS` | PlaceName |  |
| `IL` | StateName |  |
| `610710000` | ZipCode |  |

**Your answer:** `      `

---

## 36. `1113 AVE A ROCK FALLS IL 61071`
*IL*

| Token | Proposed | Alternative |
|---|---|---|
| `1113` | AddressNumber |  |
| `AVE` | StreetNamePreType |  |
| `A` | StreetName |  |
| `ROCK` **←** | **StreetName** | PlaceName (v43), PlaceName (v50) |
| `FALLS` | PlaceName |  |
| `IL` | StateName |  |
| `61071` | ZipCode |  |

**Your answer:** `      `

---

## 37. `1215 W 19TH ST ROCK FALLS IL 61071`
*IL*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `1215` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `19TH` | StreetName |
| `ST` | StreetNamePostType |
| `ROCK` | PlaceName |
| `FALLS` | PlaceName |
| `IL` | StateName |
| `61071` | ZipCode |

**Your answer:** `      `

---

## 38. `701 AVE A ROCK FALLS IL 61071`
*IL*

| Token | Proposed | Alternative |
|---|---|---|
| `701` | AddressNumber |  |
| `AVE` | StreetNamePreType |  |
| `A` | StreetName |  |
| `ROCK` **←** | **StreetName** | PlaceName (v43), PlaceName (v50) |
| `FALLS` | PlaceName |  |
| `IL` | StateName |  |
| `61071` | ZipCode |  |

**Your answer:** `      `

---

## 39. `1022 E Victoria South Bend IN 46614`
*IN*

| Token | Proposed | Alternative |
|---|---|---|
| `1022` | AddressNumber |  |
| `E` | StreetNamePreDirectional |  |
| `Victoria` | StreetName |  |
| `South` **←** | **PlaceName** | StreetName (v43), StreetNamePostDirectional (v50) |
| `Bend` | PlaceName |  |
| `IN` | StateName |  |
| `46614` | ZipCode |  |

**Your answer:** `      `

---

## 40. `1106 E Oakside South Bend IN 46614`
*IN*

| Token | Proposed | Alternative |
|---|---|---|
| `1106` | AddressNumber |  |
| `E` | StreetNamePreDirectional |  |
| `Oakside` | StreetName |  |
| `South` **←** | **PlaceName** | StreetName (v43), StreetNamePostDirectional (v50) |
| `Bend` | PlaceName |  |
| `IN` | StateName |  |
| `46614` | ZipCode |  |

**Your answer:** `      `

---

## 41. `1112 E Eckman South Bend IN 46614`
*IN*

| Token | Proposed | Alternative |
|---|---|---|
| `1112` | AddressNumber |  |
| `E` | StreetNamePreDirectional |  |
| `Eckman` | StreetName |  |
| `South` **←** | **PlaceName** | StreetName (v43), StreetNamePostDirectional (v50) |
| `Bend` | PlaceName |  |
| `IN` | StateName |  |
| `46614` | ZipCode |  |

**Your answer:** `      `

---

## 42. `1146 E DONALD South Bend IN 46613`
*IN*

| Token | Proposed | Alternative |
|---|---|---|
| `1146` | AddressNumber |  |
| `E` | StreetNamePreDirectional |  |
| `DONALD` | StreetName |  |
| `South` **←** | **PlaceName** | StreetName (v43), StreetNamePostDirectional (v50) |
| `Bend` | PlaceName |  |
| `IN` | StateName |  |
| `46613` | ZipCode |  |

**Your answer:** `      `

---

## 43. `1157 E Donmoyer Av South Bend IN 46614`
*IN*

| Token | Proposed | Alternative |
|---|---|---|
| `1157` | AddressNumber |  |
| `E` | StreetNamePreDirectional |  |
| `Donmoyer` | StreetName |  |
| `Av` | StreetNamePostType |  |
| `South` **←** | **PlaceName** | StreetNamePostDirectional (v50) |
| `Bend` | PlaceName |  |
| `IN` | StateName |  |
| `46614` | ZipCode |  |

**Your answer:** `      `

---

## 44. `1701 Miami St c/o St Mattews Cathedral South Bend IN 46613`
*IN*

| Token | Proposed | Alternative |
|---|---|---|
| `1701` | AddressNumber |  |
| `Miami` | StreetName |  |
| `St` **←** | **StreetName** | StreetNamePostType (v43) |
| `c/o` **←** | **StreetName** | BuildingName (v43) |
| `St` **←** | **StreetNamePostType** | BuildingName (v43) |
| `Mattews` **←** | **BuildingName** | PlaceName (v50) |
| `Cathedral` **←** | **BuildingName** | PlaceName (v50) |
| `South` **←** | **BuildingName** | PlaceName (v50) |
| `Bend` | PlaceName |  |
| `IN` | StateName |  |
| `46613` | ZipCode |  |

**Your answer:** `      `

---

## 45. `5308 Packard Avenue South Bend IN 46619`
*IN*

| Token | Proposed | Alternative |
|---|---|---|
| `5308` | AddressNumber |  |
| `Packard` | StreetName |  |
| `Avenue` | StreetNamePostType |  |
| `South` **←** | **PlaceName** | StreetNamePostDirectional (v43), StreetNamePostDirectional (v50) |
| `Bend` | PlaceName |  |
| `IN` | StateName |  |
| `46619` | ZipCode |  |

**Your answer:** `      `

---

## 46. `56031 Jefferson Knolls Osceola IN 46561`
*IN*

| Token | Proposed | Alternative |
|---|---|---|
| `56031` | AddressNumber |  |
| `Jefferson` | StreetName |  |
| `Knolls` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `Osceola` | PlaceName |  |
| `IN` | StateName |  |
| `46561` | ZipCode |  |

**Your answer:** `      `

---

## 47. `5776 N GRAPE RD SUITE 51 PMB 175 Mishawaka IN 46545`
*IN*

| Token | Proposed | Alternative |
|---|---|---|
| `5776` | AddressNumber |  |
| `N` | StreetNamePreDirectional |  |
| `GRAPE` | StreetName |  |
| `RD` | StreetNamePostType |  |
| `SUITE` | OccupancyType |  |
| `51` | OccupancyIdentifier |  |
| `PMB` **←** | **SubaddressType** | OccupancyType (v43), OccupancyType (v50) |
| `175` **←** | **SubaddressIdentifier** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `Mishawaka` | PlaceName |  |
| `IN` | StateName |  |
| `46545` | ZipCode |  |

**Your answer:** `      `

---

## 48. `PO Box 510 Ashley IN 46705`
*IN*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `PO` | USPSBoxType |
| `Box` | USPSBoxType |
| `510` | USPSBoxID |
| `Ashley` | PlaceName |
| `IN` | StateName |
| `46705` | ZipCode |

**Your answer:** `      `

---

## 49. `1236 WILLOW GLEN DENHAM SPRINGS, LA 70726`
*LA*

| Token | Proposed | Alternative |
|---|---|---|
| `1236` | AddressNumber |  |
| `WILLOW` | StreetName |  |
| `GLEN` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `DENHAM` | PlaceName |  |
| `SPRINGS,` | PlaceName |  |
| `LA` | StateName |  |
| `70726` | ZipCode |  |

**Your answer:** `      `

---

## 50. `346 CHATEAU JON DENHAM SPRINGS, LA 70726`
*LA*

| Token | Proposed | Alternative |
|---|---|---|
| `346` | AddressNumber |  |
| `CHATEAU` | StreetName |  |
| `JON` **←** | **PlaceName** | StreetName (v43), StreetName (v50) |
| `DENHAM` | PlaceName |  |
| `SPRINGS,` | PlaceName |  |
| `LA` | StateName |  |
| `70726` | ZipCode |  |

**Your answer:** `      `

---

## 51. `20 W WASHINGTON ST STE 500 HAGERSTOWN MD 21740`
*MD*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `20` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `WASHINGTON` | StreetName |
| `ST` | StreetNamePostType |
| `STE` | OccupancyType |
| `500` | OccupancyIdentifier |
| `HAGERSTOWN` | PlaceName |
| `MD` | StateName |
| `21740` | ZipCode |

**Your answer:** `      `

---

## 52. `5805 MT BRIAR RD KEEDYSVILLE MD 21756`
*MD*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `5805` | AddressNumber |
| `MT` | StreetName |
| `BRIAR` | StreetName |
| `RD` | StreetNamePostType |
| `KEEDYSVILLE` | PlaceName |
| `MD` | StateName |
| `21756` | ZipCode |

**Your answer:** `      `

---

## 53. `ATTN: KENNETH WIREMAN 7310 ESQUIRE CT MAILBOX 14 ELKRIDGE MD 21075`
*MD*

| Token | Proposed | Alternative |
|---|---|---|
| `ATTN:` | Recipient |  |
| `KENNETH` | Recipient |  |
| `WIREMAN` | Recipient |  |
| `7310` | AddressNumber |  |
| `ESQUIRE` | StreetName |  |
| `CT` | StreetNamePostType |  |
| `MAILBOX` **←** | **SubaddressType** | OccupancyType (v43), OccupancyType (v50) |
| `14` **←** | **SubaddressIdentifier** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `ELKRIDGE` | PlaceName |  |
| `MD` | StateName |  |
| `21075` | ZipCode |  |

**Your answer:** `      `

---

## 54. `C/O SEAN GRIFFITH, EX DIR 35 W BALTIMORE ST HAGERSTOWN MD 21740`
*MD*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `C/O` | Recipient |
| `SEAN` | Recipient |
| `GRIFFITH,` | Recipient |
| `EX` | Recipient |
| `DIR` | Recipient |
| `35` | AddressNumber |
| `W` | StreetNamePreDirectional |
| `BALTIMORE` | StreetName |
| `ST` | StreetNamePostType |
| `HAGERSTOWN` | PlaceName |
| `MD` | StateName |
| `21740` | ZipCode |

**Your answer:** `      `

---

## 55. `PO BOX 1510 CLARKSBURG MD 20871`
*MD*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `1510` | USPSBoxID |
| `CLARKSBURG` | PlaceName |
| `MD` | StateName |
| `20871` | ZipCode |

**Your answer:** `      `

---

## 56. `TAWES STATE OFFICE BLDG 580 TAYLOR AVE ANNAPOLIS MD 21401`
*MD*

| Token | Proposed | Alternative |
|---|---|---|
| `TAWES` **←** | **BuildingName** | Recipient (v50) |
| `STATE` **←** | **BuildingName** | Recipient (v50) |
| `OFFICE` **←** | **BuildingName** | Recipient (v50) |
| `BLDG` **←** | **BuildingName** | Recipient (v50) |
| `580` | AddressNumber |  |
| `TAYLOR` | StreetName |  |
| `AVE` | StreetNamePostType |  |
| `ANNAPOLIS` | PlaceName |  |
| `MD` | StateName |  |
| `21401` | ZipCode |  |

**Your answer:** `      `

---

## 57. `701 PENNSYLVANIA AVENUE NW CONDO #1211 WASHINGTON DC 20004`
*ME*

| Token | Proposed | Alternative |
|---|---|---|
| `701` | AddressNumber |  |
| `PENNSYLVANIA` | StreetName |  |
| `AVENUE` | StreetNamePostType |  |
| `NW` **←** | **SubaddressIdentifier** | StreetNamePostDirectional (v43), StreetNamePostDirectional (v50) |
| `CONDO` **←** | **SubaddressType** | OccupancyType (v43) |
| `#` **←** | **SubaddressIdentifier** | OccupancyIdentifier (v43) |
| `1211` **←** | **SubaddressIdentifier** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `WASHINGTON` | PlaceName |  |
| `DC` | StateName |  |
| `20004` | ZipCode |  |

**Your answer:** `      `

---

## 58. `97 STARBOARD REACH YARMOUTH ME 04096`
*ME*

| Token | Proposed | Alternative |
|---|---|---|
| `97` | AddressNumber |  |
| `STARBOARD` | StreetName |  |
| `REACH` **←** | **StreetName** | PlaceName (v43), PlaceName (v50) |
| `YARMOUTH` | PlaceName |  |
| `ME` | StateName |  |
| `04096` | ZipCode |  |

**Your answer:** `      `

---

## 59. `LESTER B ORCUTT BLVD BIDDEFORD ME 04005`
*ME*

| Token | Proposed | Alternative |
|---|---|---|
| `LESTER` **←** | **Recipient** | StreetName (v50) |
| `B` **←** | **AddressNumber** | Recipient (v43), StreetName (v50) |
| `ORCUTT` | StreetName |  |
| `BLVD` | StreetNamePostType |  |
| `BIDDEFORD` | PlaceName |  |
| `ME` | StateName |  |
| `04005` | ZipCode |  |

**Your answer:** `      `

---

## 60. `ONE CITY CENTER 5TH FLOOR PORTLAND ME 04101`
*ME*

| Token | Proposed | Alternative |
|---|---|---|
| `ONE` **←** | **BuildingName** | LandmarkName (v50) |
| `CITY` **←** | **BuildingName** | LandmarkName (v50) |
| `CENTER` **←** | **BuildingName** | LandmarkName (v50) |
| `5TH` | OccupancyIdentifier |  |
| `FLOOR` | OccupancyType |  |
| `PORTLAND` | PlaceName |  |
| `ME` | StateName |  |
| `04101` | ZipCode |  |

**Your answer:** `      `

---

## 61. `PO BOX 360 LIMERICK ME 04048`
*ME*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `360` | USPSBoxID |
| `LIMERICK` | PlaceName |
| `ME` | StateName |
| `04048` | ZipCode |

**Your answer:** `      `

---

## 62. `STATION #16 D.E.P. AUGUSTA ME 04330`
*ME*

| Token | Proposed | Alternative |
|---|---|---|
| `STATION` **←** | **Recipient** | StreetNamePostType (v43), StreetNamePreType (v50) |
| `#` **←** | **Recipient** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `16` **←** | **Recipient** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `D.E.P.` **←** | **Recipient** | PlaceName (v43), PlaceName (v50) |
| `AUGUSTA` | PlaceName |  |
| `ME` | StateName |  |
| `04330` | ZipCode |  |

**Your answer:** `      `

---

## 63. `11007 HORSESHOE BEND HERNANDO MS 386320000`
*MS*

| Token | Proposed | Alternative |
|---|---|---|
| `11007` | AddressNumber |  |
| `HORSESHOE` | StreetName |  |
| `BEND` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `HERNANDO` | PlaceName |  |
| `MS` | StateName |  |
| `386320000` | ZipCode |  |

**Your answer:** `      `

---

## 64. `11197 WOODLAND LAKE HERNANDO MS 386320000`
*MS*

| Token | Proposed | Alternative |
|---|---|---|
| `11197` | AddressNumber |  |
| `WOODLAND` | StreetName |  |
| `LAKE` **←** | **StreetNamePostType** | PlaceName (v43), PlaceName (v50) |
| `HERNANDO` | PlaceName |  |
| `MS` | StateName |  |
| `386320000` | ZipCode |  |

**Your answer:** `      `

---

## 65. `1719 HWY 301 SOUTH LAKE CORMORANT MS 386410000`
*MS*

| Token | Proposed | Alternative |
|---|---|---|
| `1719` | AddressNumber |  |
| `HWY` | StreetNamePreType |  |
| `301` | StreetName |  |
| `SOUTH` **←** | **PlaceName** | StreetNamePostDirectional (v43), StreetNamePostDirectional (v50) |
| `LAKE` | PlaceName |  |
| `CORMORANT` | PlaceName |  |
| `MS` | StateName |  |
| `386410000` | ZipCode |  |

**Your answer:** `      `

---

## 66. `3270 SNOWDOWNS RIDGE HERNANDO MS 386320000`
*MS*

| Token | Proposed | Alternative |
|---|---|---|
| `3270` | AddressNumber |  |
| `SNOWDOWNS` | StreetName |  |
| `RIDGE` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `HERNANDO` | PlaceName |  |
| `MS` | StateName |  |
| `386320000` | ZipCode |  |

**Your answer:** `      `

---

## 67. `3454 WOODLAND LAKE HERNANDO MS 386320000`
*MS*

| Token | Proposed | Alternative |
|---|---|---|
| `3454` | AddressNumber |  |
| `WOODLAND` | StreetName |  |
| `LAKE` **←** | **StreetNamePostType** | PlaceName (v43), PlaceName (v50) |
| `HERNANDO` | PlaceName |  |
| `MS` | StateName |  |
| `386320000` | ZipCode |  |

**Your answer:** `      `

---

## 68. `5740 GETWELL RD BLDG 8B SOUTHAVEN MS 38672`
*MS*

| Token | Proposed | Alternative |
|---|---|---|
| `5740` | AddressNumber |  |
| `GETWELL` | StreetName |  |
| `RD` | StreetNamePostType |  |
| `BLDG` **←** | **SubaddressType** | OccupancyType (v43), OccupancyType (v50) |
| `8B` **←** | **SubaddressIdentifier** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `SOUTHAVEN` | PlaceName |  |
| `MS` | StateName |  |
| `38672` | ZipCode |  |

**Your answer:** `      `

---

## 69. `FOREST HILL PROPERTIES INC 5583 MURRAY AVE SUITE 100 MEMPHIS TN 381190000`
*MS*

| Token | Proposed | Alternative |
|---|---|---|
| `FOREST` **←** | **BuildingName** | Recipient (v43), Recipient (v50) |
| `HILL` **←** | **BuildingName** | Recipient (v43), Recipient (v50) |
| `PROPERTIES` **←** | **BuildingName** | Recipient (v43), Recipient (v50) |
| `INC` **←** | **BuildingName** | Recipient (v43), Recipient (v50) |
| `5583` | AddressNumber |  |
| `MURRAY` | StreetName |  |
| `AVE` | StreetNamePostType |  |
| `SUITE` | OccupancyType |  |
| `100` | OccupancyIdentifier |  |
| `MEMPHIS` | PlaceName |  |
| `TN` | StateName |  |
| `381190000` | ZipCode |  |

**Your answer:** `      `

---

## 70. `13190 E CAMINO LA CEBADILLA`
*MT*

| Token | Proposed | Alternative |
|---|---|---|
| `13190` | AddressNumber |  |
| `E` | StreetNamePreDirectional |  |
| `CAMINO` **←** | **StreetNamePreType** | StreetName (v43), StreetName (v50) |
| `LA` **←** | **StreetNamePreType** | StreetName (v43), StreetName (v50) |
| `CEBADILLA` | StreetName |  |

**Your answer:** `      `

---

## 71. `48901 US HIGHWAY 93 STE A PMB 246 HAMILTON, MT 59840`
*MT*

| Token | Proposed | Alternative |
|---|---|---|
| `48901` | AddressNumber |  |
| `US` | StreetNamePreType |  |
| `HIGHWAY` | StreetNamePreType |  |
| `93` | StreetName |  |
| `STE` | OccupancyType |  |
| `A` | OccupancyIdentifier |  |
| `PMB` **←** | **SubaddressType** | OccupancyType (v43), OccupancyType (v50) |
| `246` **←** | **SubaddressIdentifier** | OccupancyIdentifier (v43), OccupancyIdentifier (v50) |
| `HAMILTON,` | PlaceName |  |
| `MT` | StateName |  |
| `59840` | ZipCode |  |

**Your answer:** `      `

---

## 72. `612 N 1ST ST STE 2-246 CORVALLIS, MT 59828`
*MT*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `612` | AddressNumber |
| `N` | StreetNamePreDirectional |
| `1ST` | StreetName |
| `ST` | StreetNamePostType |
| `STE` | OccupancyType |
| `2-246` | OccupancyIdentifier |
| `CORVALLIS,` | PlaceName |
| `MT` | StateName |
| `59828` | ZipCode |

**Your answer:** `      `

---

## 73. `PO BOX 1002 HAMILTON, MT 59840`
*MT*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `1002` | USPSBoxID |
| `HAMILTON,` | PlaceName |
| `MT` | StateName |
| `59840` | ZipCode |

**Your answer:** `      `

---

## 74. `PO BOX 37 SULA, MT 59871`
*MT*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `37` | USPSBoxID |
| `SULA,` | PlaceName |
| `MT` | StateName |
| `59871` | ZipCode |

**Your answer:** `      `

---

## 75. `1204 CEDAR POINT BLVD LOT 48 CEDAR POINT NC 28584-7007`
*NC*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `1204` | AddressNumber |
| `CEDAR` | StreetName |
| `POINT` | StreetName |
| `BLVD` | StreetNamePostType |
| `LOT` | OccupancyType |
| `48` | OccupancyIdentifier |
| `CEDAR` | PlaceName |
| `POINT` | PlaceName |
| `NC` | StateName |
| `28584-7007` | ZipCode |

**Your answer:** `      `

---

## 76. `27361 VISTA AZUL DANA POINT CA 92624-1818`
*NC*

| Token | Proposed | Alternative |
|---|---|---|
| `27361` | AddressNumber |  |
| `VISTA` **←** | **StreetName** | StreetNamePreType (v50) |
| `AZUL` | StreetName |  |
| `DANA` | PlaceName |  |
| `POINT` | PlaceName |  |
| `CA` | StateName |  |
| `92624-1818` | ZipCode |  |

**Your answer:** `      `

---

## 77. `2919 BREEZEWOOD AVE STE 100 FAYETTEVILLE NC 28303-5283`
*NC*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `2919` | AddressNumber |
| `BREEZEWOOD` | StreetName |
| `AVE` | StreetNamePostType |
| `STE` | OccupancyType |
| `100` | OccupancyIdentifier |
| `FAYETTEVILLE` | PlaceName |
| `NC` | StateName |
| `28303-5283` | ZipCode |

**Your answer:** `      `

---

## 78. `903 MAIN ST EXT SWANSBORO NC 28584-9111`
*NC*

| Token | Proposed | Alternative |
|---|---|---|
| `903` | AddressNumber |  |
| `MAIN` | StreetName |  |
| `ST` | StreetNamePostType |  |
| `EXT` **←** | **StreetNamePostModifier** | PlaceName (v43) |
| `SWANSBORO` | PlaceName |  |
| `NC` | StateName |  |
| `28584-9111` | ZipCode |  |

**Your answer:** `      `

---

## 79. `98 -1040 MOANALUA RD APT 1-203 AEIA HI 96701-4604`
*NC*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `98` | AddressNumber |
| `1040` | AddressNumber |
| `MOANALUA` | StreetName |
| `RD` | StreetNamePostType |
| `APT` | OccupancyType |
| `1-203` | OccupancyIdentifier |
| `AEIA` | PlaceName |
| `HI` | StateName |
| `96701-4604` | ZipCode |

**Your answer:** `      `

---

## 80. `ERNST & YOUNG LLP PO BOX 30308 CHARLOTTE NC 28230`
*ND*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `ERNST` | Recipient |
| `&` | Recipient |
| `YOUNG` | Recipient |
| `LLP` | Recipient |
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `30308` | USPSBoxID |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28230` | ZipCode |

**Your answer:** `      `

---

## 81. `LIFE ESTATES 5895 FOUNTAIN VISTA DR GRAND FORKS ND 58201`
*ND*

| Token | Proposed | Alternative |
|---|---|---|
| `LIFE` **←** | **Recipient** | BuildingName (v43) |
| `ESTATES` **←** | **Recipient** | BuildingName (v43) |
| `5895` | AddressNumber |  |
| `FOUNTAIN` | StreetName |  |
| `VISTA` | StreetName |  |
| `DR` | StreetNamePostType |  |
| `GRAND` | PlaceName |  |
| `FORKS` | PlaceName |  |
| `ND` | StateName |  |
| `58201` | ZipCode |  |

**Your answer:** `      `

---

## 82. `SCOTT GREGORY ZUKOWSKI AS TRUSTEE 3002 44TH AVE S GRAND FORKS ND 58201`
*ND*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `SCOTT` | Recipient |
| `GREGORY` | Recipient |
| `ZUKOWSKI` | Recipient |
| `AS` | Recipient |
| `TRUSTEE` | Recipient |
| `3002` | AddressNumber |
| `44TH` | StreetName |
| `AVE` | StreetNamePostType |
| `S` | StreetNamePostDirectional |
| `GRAND` | PlaceName |
| `FORKS` | PlaceName |
| `ND` | StateName |
| `58201` | ZipCode |

**Your answer:** `      `

---

## 83. `1438 RT 17A WARWICK, NY 10990`
*NJ*

| Token | Proposed | Alternative |
|---|---|---|
| `1438` | AddressNumber |  |
| `RT` **←** | **StreetName** | StreetNamePreType (v43), StreetNamePreType (v50) |
| `17A` **←** | **OccupancyIdentifier** | StreetName (v43), StreetName (v50) |
| `WARWICK,` | PlaceName |  |
| `NY` | StateName |  |
| `10990` | ZipCode |  |

**Your answer:** `      `

---

## 84. `3621 RT 94 2ND FLOOR HAMBURG, NJ 07419`
*NJ*

| Token | Proposed | Alternative |
|---|---|---|
| `3621` | AddressNumber |  |
| `RT` **←** | **StreetNamePreType** | StreetName (v43) |
| `94` **←** | **StreetName** | OccupancyIdentifier (v43) |
| `2ND` | OccupancyIdentifier |  |
| `FLOOR` | OccupancyType |  |
| `HAMBURG,` | PlaceName |  |
| `NJ` | StateName |  |
| `07419` | ZipCode |  |

**Your answer:** `      `

---

## 85. `475 SOUTH ST-PO BOX 1905 MORRISTOWN, NJ 07962`
*NJ*

| Token | Proposed | Alternative |
|---|---|---|
| `475` | AddressNumber |  |
| `SOUTH` | StreetNamePreDirectional |  |
| `ST-PO` **←** | **StreetName** | USPSBoxType (v43) |
| `BOX` | USPSBoxType |  |
| `1905` | USPSBoxID |  |
| `MORRISTOWN,` | PlaceName |  |
| `NJ` | StateName |  |
| `07962` | ZipCode |  |

**Your answer:** `      `

---

## 86. `ONE SPRING STREET NEWTON, NJ 07860`
*NJ*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `ONE` | AddressNumber |
| `SPRING` | StreetName |
| `STREET` | StreetNamePostType |
| `NEWTON,` | PlaceName |
| `NJ` | StateName |
| `07860` | ZipCode |

**Your answer:** `      `

---

## 87. `PO BOX 412 TRENTON, NJ 08625`
*NJ*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `412` | USPSBoxID |
| `TRENTON,` | PlaceName |
| `NJ` | StateName |
| `08625` | ZipCode |

**Your answer:** `      `

---

## 88. `160 OAK VIEW CIRCLE LAKE MARY, FL 32746`
*NM*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `160` | AddressNumber |
| `OAK` | StreetName |
| `VIEW` | StreetName |
| `CIRCLE` | StreetNamePostType |
| `LAKE` | PlaceName |
| `MARY,` | PlaceName |
| `FL` | StateName |
| `32746` | ZipCode |

**Your answer:** `      `

---

## 89. `536 LINDA VISTA ALAMOGORDO, NM 88310`
*NM*

| Token | Proposed | Alternative |
|---|---|---|
| `536` | AddressNumber |  |
| `LINDA` | StreetName |  |
| `VISTA` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `ALAMOGORDO,` | PlaceName |  |
| `NM` | StateName |  |
| `88310` | ZipCode |  |

**Your answer:** `      `

---

## 90. `MIKE HAYMES 1214 NEW YORK ALAMOGORDO, NM 88310`
*NM*

| Token | Proposed | Alternative |
|---|---|---|
| `MIKE` | Recipient |  |
| `HAYMES` | Recipient |  |
| `1214` | AddressNumber |  |
| `NEW` | StreetName |  |
| `YORK` **←** | **PlaceName** | StreetName (v43), StreetName (v50) |
| `ALAMOGORDO,` | PlaceName |  |
| `NM` | StateName |  |
| `88310` | ZipCode |  |

**Your answer:** `      `

---

## 91. `TAX DEPT 3 WATERWAY SQUARE PL STE 110 THE WOODLANDS, TX 77380`
*NM*

| Token | Proposed | Alternative |
|---|---|---|
| `TAX` | Recipient |  |
| `DEPT` | Recipient |  |
| `3` | AddressNumber |  |
| `WATERWAY` | StreetName |  |
| `SQUARE` | StreetName |  |
| `PL` | StreetNamePostType |  |
| `STE` | OccupancyType |  |
| `110` | OccupancyIdentifier |  |
| `THE` **←** | **PlaceName** | BuildingName (v50) |
| `WOODLANDS,` | PlaceName |  |
| `TX` | StateName |  |
| `77380` | ZipCode |  |

**Your answer:** `      `

---

## 92. `104 Carr Drive Sandy Creek NY 13145`
*NY*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `104` | AddressNumber |
| `Carr` | StreetName |
| `Drive` | StreetNamePostType |
| `Sandy` | PlaceName |
| `Creek` | PlaceName |
| `NY` | StateName |
| `13145` | ZipCode |

**Your answer:** `      `

---

## 93. `162 Co Rt 23A Constantia NY 13044`
*NY*

| Token | Proposed | Alternative |
|---|---|---|
| `162` | AddressNumber |  |
| `Co` **←** | **StreetName** | StreetNamePreType (v43), StreetNamePreType (v50) |
| `Rt` **←** | **StreetName** | StreetNamePreType (v43), StreetNamePreType (v50) |
| `23A` **←** | **OccupancyIdentifier** | StreetName (v43), StreetName (v50) |
| `Constantia` | PlaceName |  |
| `NY` | StateName |  |
| `13044` | ZipCode |  |

**Your answer:** `      `

---

## 94. `394 Co Rt 41A Pulaski NY 13142`
*NY*

| Token | Proposed | Alternative |
|---|---|---|
| `394` | AddressNumber |  |
| `Co` **←** | **StreetName** | StreetNamePreType (v43), StreetNamePreType (v50) |
| `Rt` **←** | **StreetName** | StreetNamePreType (v43), StreetNamePreType (v50) |
| `41A` **←** | **OccupancyIdentifier** | StreetName (v43), StreetName (v50) |
| `Pulaski` | PlaceName |  |
| `NY` | StateName |  |
| `13142` | ZipCode |  |

**Your answer:** `      `

---

## 95. `54 Kilts Tract Sandy Creek NY 13145`
*NY*

| Token | Proposed | Alternative |
|---|---|---|
| `54` | AddressNumber |  |
| `Kilts` | StreetName |  |
| `Tract` **←** | **StreetName** | PlaceName (v43), PlaceName (v50) |
| `Sandy` | PlaceName |  |
| `Creek` | PlaceName |  |
| `NY` | StateName |  |
| `13145` | ZipCode |  |

**Your answer:** `      `

---

## 96. `7167 St Rt 104 Oswego NY 13126`
*NY*

| Token | Proposed | Alternative |
|---|---|---|
| `7167` | AddressNumber |  |
| `St` **←** | **StreetNamePreType** | StreetName (v43), StreetName (v50) |
| `Rt` **←** | **StreetNamePreType** | StreetName (v43), StreetName (v50) |
| `104` | StreetName |  |
| `Oswego` | PlaceName |  |
| `NY` | StateName |  |
| `13126` | ZipCode |  |

**Your answer:** `      `

---

## 97. `986 St Rt 104-B Mexico NY 13114`
*NY*

| Token | Proposed | Alternative |
|---|---|---|
| `986` | AddressNumber |  |
| `St` **←** | **StreetNamePreType** | StreetName (v43), StreetName (v50) |
| `Rt` **←** | **StreetNamePreType** | StreetName (v43), StreetName (v50) |
| `104-B` | StreetName |  |
| `Mexico` | PlaceName |  |
| `NY` | StateName |  |
| `13114` | ZipCode |  |

**Your answer:** `      `

---

## 98. `PO Box 731166 Patricia Ln Mexico NY 13114`
*NY*

| Token | Proposed | Alternative |
|---|---|---|
| `PO` | USPSBoxType |  |
| `Box` | USPSBoxType |  |
| `731166` | USPSBoxID |  |
| `Patricia` **←** | **StreetName** | PlaceName (v43), PlaceName (v50) |
| `Ln` **←** | **StreetNamePostType** | StateName (v43) |
| `Mexico` | PlaceName |  |
| `NY` | StateName |  |
| `13114` | ZipCode |  |

**Your answer:** `      `

---

## 99. `1010 PINE 9E L 01 ST LOUIS, MO 63101`
*OH*

| Token | Proposed | Alternative |
|---|---|---|
| `1010` | AddressNumber |  |
| `PINE` **←** | **StreetNamePreType** | StreetName (v43), StreetName (v50) |
| `9E` | StreetName |  |
| `L` | StreetName |  |
| `01` | StreetName |  |
| `ST` | PlaceName |  |
| `LOUIS,` | PlaceName |  |
| `MO` | StateName |  |
| `63101` | ZipCode |  |

**Your answer:** `      `

---

## 100. `3262 LINCOLN WAY WEST MASSILLON, OH 44647`
*OH*

| Token | Proposed | Alternative |
|---|---|---|
| `3262` | AddressNumber |  |
| `LINCOLN` | StreetName |  |
| `WAY` | StreetNamePostType |  |
| `WEST` **←** | **StreetNamePostDirectional** | PlaceName (v43), PlaceName (v50) |
| `MASSILLON,` | PlaceName |  |
| `OH` | StateName |  |
| `44647` | ZipCode |  |

**Your answer:** `      `

---

## 101. `1180 LAKEMONT DRIVE MEADVILLE PA 163350000`
*PA*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `1180` | AddressNumber |
| `LAKEMONT` | StreetName |
| `DRIVE` | StreetNamePostType |
| `MEADVILLE` | PlaceName |
| `PA` | StateName |
| `163350000` | ZipCode |

**Your answer:** `      `

---

## 102. `1261 WASHINGTON STREET EXT CONNEAUTVILLE PA 16406`
*PA*

| Token | Proposed | Alternative |
|---|---|---|
| `1261` | AddressNumber |  |
| `WASHINGTON` | StreetName |  |
| `STREET` | StreetNamePostType |  |
| `EXT` **←** | **StreetNamePostModifier** | PlaceName (v43) |
| `CONNEAUTVILLE` | PlaceName |  |
| `PA` | StateName |  |
| `16406` | ZipCode |  |

**Your answer:** `      `

---

## 103. `1265 WASHINGTON STREET EXT CONNEAUTVILLE PA 16406`
*PA*

| Token | Proposed | Alternative |
|---|---|---|
| `1265` | AddressNumber |  |
| `WASHINGTON` | StreetName |  |
| `STREET` | StreetNamePostType |  |
| `EXT` **←** | **StreetNamePostModifier** | PlaceName (v43) |
| `CONNEAUTVILLE` | PlaceName |  |
| `PA` | StateName |  |
| `16406` | ZipCode |  |

**Your answer:** `      `

---

## 104. `204 PARKWAY DRIVE PO BOX 405 CONNEAUTVILLE PA 16406`
*PA*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `204` | AddressNumber |
| `PARKWAY` | StreetName |
| `DRIVE` | StreetNamePostType |
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `405` | USPSBoxID |
| `CONNEAUTVILLE` | PlaceName |
| `PA` | StateName |
| `16406` | ZipCode |

**Your answer:** `      `

---

## 105. `804 RAVINE STREET MEADVILLE PA 16335`
*PA*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `804` | AddressNumber |
| `RAVINE` | StreetName |
| `STREET` | StreetNamePostType |
| `MEADVILLE` | PlaceName |
| `PA` | StateName |
| `16335` | ZipCode |

**Your answer:** `      `

---

## 106. `894 DIAMOND PARK MEADVILLE PA 163350000`
*PA*

| Token | Proposed | Alternative |
|---|---|---|
| `894` | AddressNumber |  |
| `DIAMOND` | StreetName |  |
| `PARK` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `MEADVILLE` | PlaceName |  |
| `PA` | StateName |  |
| `163350000` | ZipCode |  |

**Your answer:** `      `

---

## 107. `903 DIAMOND PARK MEADVILLE PA 16335`
*PA*

| Token | Proposed | Alternative |
|---|---|---|
| `903` | AddressNumber |  |
| `DIAMOND` | StreetName |  |
| `PARK` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `MEADVILLE` | PlaceName |  |
| `PA` | StateName |  |
| `16335` | ZipCode |  |

**Your answer:** `      `

---

## 108. `1350 CASSIDY CT, UNIT B MT PLEASANT SC 29464`
*SC*

| Token | Proposed | Alternative |
|---|---|---|
| `1350` | AddressNumber |  |
| `CASSIDY` | StreetName |  |
| `CT,` | StreetNamePostType |  |
| `UNIT` | OccupancyType |  |
| `B` | OccupancyIdentifier |  |
| `MT` **←** | **StreetNamePostType** | PlaceName (v43), PlaceName (v50) |
| `PLEASANT` | PlaceName |  |
| `SC` | StateName |  |
| `29464` | ZipCode |  |

**Your answer:** `      `

---

## 109. `5241 HWY 17 BUS MURRELLS INLET SC 29576`
*SC*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `5241` | AddressNumber |
| `HWY` | StreetNamePreType |
| `17` | StreetName |
| `BUS` | PlaceName |
| `MURRELLS` | PlaceName |
| `INLET` | PlaceName |
| `SC` | StateName |
| `29576` | ZipCode |

**Your answer:** `      `

---

## 110. `6324 FAIRVIEW ROAD, Unit 550 CHARLOTTE NC 28210`
*SC*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `6324` | AddressNumber |
| `FAIRVIEW` | StreetName |
| `ROAD,` | StreetNamePostType |
| `Unit` | OccupancyType |
| `550` | OccupancyIdentifier |
| `CHARLOTTE` | PlaceName |
| `NC` | StateName |
| `28210` | ZipCode |

**Your answer:** `      `

---

## 111. `C/O LITCHFIELD BEACH MANAGEMENT P O BOX 911 PAWLEYS ISLAND SC 29585`
*SC*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `C/O` | Recipient |
| `LITCHFIELD` | Recipient |
| `BEACH` | Recipient |
| `MANAGEMENT` | Recipient |
| `P` | USPSBoxType |
| `O` | USPSBoxType |
| `BOX` | USPSBoxType |
| `911` | USPSBoxID |
| `PAWLEYS` | PlaceName |
| `ISLAND` | PlaceName |
| `SC` | StateName |
| `29585` | ZipCode |

**Your answer:** `      `

---

## 112. `C/O OYSTERCATCHER ASSOC PO DRAWER 320 PAWLEYS ISLAND SC 29585`
*SC*

| Token | Proposed | Alternative |
|---|---|---|
| `C/O` | Recipient |  |
| `OYSTERCATCHER` | Recipient |  |
| `ASSOC` | Recipient |  |
| `PO` **←** | **USPSBoxType** | Recipient (v43), Recipient (v50) |
| `DRAWER` **←** | **USPSBoxType** | Recipient (v43), Recipient (v50) |
| `320` **←** | **USPSBoxID** | AddressNumber (v43), AddressNumber (v50) |
| `PAWLEYS` **←** | **PlaceName** | StreetName (v43), StreetName (v50) |
| `ISLAND` | PlaceName |  |
| `SC` | StateName |  |
| `29585` | ZipCode |  |

**Your answer:** `      `

---

## 113. `P O DRAWER E GEORGETOWN SC 29442`
*SC*

| Token | Proposed | Alternative |
|---|---|---|
| `P` | Recipient |  |
| `O` | Recipient |  |
| `DRAWER` | Recipient |  |
| `E` **←** | **Recipient** | StreetNamePostDirectional (v43) |
| `GEORGETOWN` | PlaceName |  |
| `SC` | StateName |  |
| `29442` | ZipCode |  |

**Your answer:** `      `

---

## 114. `3 LIMITED CENTRE JOHNSON CITY TN 37604`
*TN*

| Token | Proposed | Alternative |
|---|---|---|
| `3` | AddressNumber |  |
| `LIMITED` | StreetName |  |
| `CENTRE` **←** | **StreetNamePostType** | StreetName (v50) |
| `JOHNSON` | PlaceName |  |
| `CITY` | PlaceName |  |
| `TN` | StateName |  |
| `37604` | ZipCode |  |

**Your answer:** `      `

---

## 115. `79 WHISPER BEND JOHNSON CITY TN 37604`
*TN*

| Token | Proposed | Alternative |
|---|---|---|
| `79` | AddressNumber |  |
| `WHISPER` | StreetName |  |
| `BEND` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `JOHNSON` | PlaceName |  |
| `CITY` | PlaceName |  |
| `TN` | StateName |  |
| `37604` | ZipCode |  |

**Your answer:** `      `

---

## 116. `PO BOX 9000 JOHNSON CITY TN 37615`
*TN*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `9000` | USPSBoxID |
| `JOHNSON` | PlaceName |
| `CITY` | PlaceName |
| `TN` | StateName |
| `37615` | ZipCode |

**Your answer:** `      `

---

## 117. `11918 FM 2153 SANGER TX 76266`
*TX*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `11918` | AddressNumber |
| `FM` | StreetNamePreType |
| `2153` | StreetName |
| `SANGER` | PlaceName |
| `TX` | StateName |
| `76266` | ZipCode |

**Your answer:** `      `

---

## 118. `2500 N INTERSTATE 35 STE 6 DENTON TX 76201`
*TX*

| Token | Proposed | Alternative |
|---|---|---|
| `2500` | AddressNumber |  |
| `N` | StreetNamePreDirectional |  |
| `INTERSTATE` **←** | **StreetName** | StreetNamePreType (v43) |
| `35` | StreetName |  |
| `STE` | OccupancyType |  |
| `6` | OccupancyIdentifier |  |
| `DENTON` | PlaceName |  |
| `TX` | StateName |  |
| `76201` | ZipCode |  |

**Your answer:** `      `

---

## 119. `C/O DIANA SEALE 15 20TH ST S APT 501 BIRMINGHAM AL 35233`
*TX*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `C/O` | Recipient |
| `DIANA` | Recipient |
| `SEALE` | Recipient |
| `15` | AddressNumber |
| `20TH` | StreetName |
| `ST` | StreetNamePostType |
| `S` | StreetNamePostDirectional |
| `APT` | OccupancyType |
| `501` | OccupancyIdentifier |
| `BIRMINGHAM` | PlaceName |
| `AL` | StateName |
| `35233` | ZipCode |

**Your answer:** `      `

---

## 120. `DO NOT SENT TO SEALS RD OR MARILYN ARGYLE TX 76226`
*TX*

| Token | Proposed | Alternative |
|---|---|---|
| `DO` **←** | **Recipient** | StreetName (v43) |
| `NOT` **←** | **Recipient** | StreetName (v43) |
| `SENT` **←** | **Recipient** | StreetName (v43) |
| `TO` **←** | **Recipient** | StreetName (v43) |
| `SEALS` **←** | **Recipient** | StreetName (v43) |
| `RD` **←** | **Recipient** | StreetNamePostType (v43) |
| `OR` **←** | **Recipient** | PlaceName (v43) |
| `MARILYN` **←** | **Recipient** | PlaceName (v43) |
| `ARGYLE` | PlaceName |  |
| `TX` | StateName |  |
| `76226` | ZipCode |  |

**Your answer:** `      `

---

## 121. `SACCO, KAREN A TRT OF KAREN A SACCO REV TR 10910 RALEIGH ST WESTCHESTER IL 60154`
*TX*

| Token | Proposed | Alternative |
|---|---|---|
| `SACCO,` | Recipient |  |
| `KAREN` | Recipient |  |
| `A` | Recipient |  |
| `TRT` | Recipient |  |
| `OF` | Recipient |  |
| `KAREN` | Recipient |  |
| `A` | Recipient |  |
| `SACCO` | Recipient |  |
| `REV` | Recipient |  |
| `TR` **←** | **Recipient** | StreetNamePreType (v43) |
| `10910` **←** | **AddressNumber** | StreetName (v43) |
| `RALEIGH` | StreetName |  |
| `ST` | StreetNamePostType |  |
| `WESTCHESTER` | PlaceName |  |
| `IL` | StateName |  |
| `60154` | ZipCode |  |

**Your answer:** `      `

---

## 122. `112 BIG MAPLE DR FOREST VA 24551`
*VA*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `112` | AddressNumber |
| `BIG` | StreetName |
| `MAPLE` | StreetName |
| `DR` | StreetNamePostType |
| `FOREST` | PlaceName |
| `VA` | StateName |
| `24551` | ZipCode |

**Your answer:** `      `

---

## 123. `PO BOX 198 HURLEY VA 24620`
*VA*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `198` | USPSBoxID |
| `HURLEY` | PlaceName |
| `VA` | StateName |
| `24620` | ZipCode |

**Your answer:** `      `

---

## 124. `PO BOX 62763 VIRGINIA BEACH VA 234662763`
*VA*  ·  _audit record: all models agree_

| Token | Proposed |
|---|---|
| `PO` | USPSBoxType |
| `BOX` | USPSBoxType |
| `62763` | USPSBoxID |
| `VIRGINIA` | PlaceName |
| `BEACH` | PlaceName |
| `VA` | StateName |
| `234662763` | ZipCode |

**Your answer:** `      `

---

## 125. `106 W SEEBOTH ST UN 306 MILWAUKEE, WI 532040000`
*WI*

| Token | Proposed | Alternative |
|---|---|---|
| `106` | AddressNumber |  |
| `W` | StreetNamePreDirectional |  |
| `SEEBOTH` | StreetName |  |
| `ST` | StreetName |  |
| `UN` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `306` **←** | **OccupancyIdentifier** | StreetName (v43), StreetName (v50) |
| `MILWAUKEE,` | PlaceName |  |
| `WI` | StateName |  |
| `532040000` | ZipCode |  |

**Your answer:** `      `

---

## 126. `106 W SEEBOTH ST UN 701 MILWAUKEE, WI 532040000`
*WI*

| Token | Proposed | Alternative |
|---|---|---|
| `106` | AddressNumber |  |
| `W` | StreetNamePreDirectional |  |
| `SEEBOTH` | StreetName |  |
| `ST` | StreetName |  |
| `UN` **←** | **StreetNamePostType** | StreetName (v43), StreetName (v50) |
| `701` **←** | **OccupancyIdentifier** | StreetName (v43), StreetName (v50) |
| `MILWAUKEE,` | PlaceName |  |
| `WI` | StateName |  |
| `532040000` | ZipCode |  |

**Your answer:** `      `

---

## 127. `106 W SEEBOTH ST-UNIT 308 MILWAUKEE, WI 532040000`
*WI*

| Token | Proposed | Alternative |
|---|---|---|
| `106` | AddressNumber |  |
| `W` | StreetNamePreDirectional |  |
| `SEEBOTH` | StreetName |  |
| `ST-UNIT` | StreetName |  |
| `308` **←** | **StreetName** | OccupancyIdentifier (v50) |
| `MILWAUKEE,` | PlaceName |  |
| `WI` | StateName |  |
| `532040000` | ZipCode |  |

**Your answer:** `      `

---

## 128. `130 W WATER ST UN 410 MILWAUKEE, WI 532040000`
*WI*

| Token | Proposed | Alternative |
|---|---|---|
| `130` | AddressNumber |  |
| `W` | StreetNamePreDirectional |  |
| `WATER` | StreetName |  |
| `ST` | StreetNamePostType |  |
| `UN` **←** | **OccupancyType** | USPSBoxType (v50) |
| `410` **←** | **OccupancyIdentifier** | USPSBoxID (v50) |
| `MILWAUKEE,` | PlaceName |  |
| `WI` | StateName |  |
| `532040000` | ZipCode |  |

**Your answer:** `      `

---

## 129. `210 S WATER ST UN 419 MILWAUKEE, WI 532040000`
*WI*

| Token | Proposed | Alternative |
|---|---|---|
| `210` | AddressNumber |  |
| `S` | StreetNamePreDirectional |  |
| `WATER` | StreetName |  |
| `ST` **←** | **StreetNamePostType** | StreetName (v43) |
| `UN` **←** | **USPSBoxType** | StreetName (v43) |
| `419` **←** | **USPSBoxID** | StreetName (v43) |
| `MILWAUKEE,` | PlaceName |  |
| `WI` | StateName |  |
| `532040000` | ZipCode |  |

**Your answer:** `      `

---

## When you're done

Answers get stored as approved label sequences in `eval/gold2c/approved_labels.json`. Gold-2c is a **dev surface**: it steers candidate selection and may never be cited in a public claim. Before it steers anything, it has to prove itself — it must rank v43 above v50, which is the order gold-2b already established. If it fails that check it gets published as a failed instrument, like the two before it.

Gold-2b's final scoring attempt stays unspent until this instrument earns its keep.