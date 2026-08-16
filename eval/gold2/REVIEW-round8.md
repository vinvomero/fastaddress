# Address review — Round 8 (national free-text): 64 parses

## What this is

Real owner-mailing addresses fetched from state and county open-data portals across the country — free text as assessors wrote it, the evidence base for any public 'national' claim. These are every record where the two parsers disagree.

No suggestions this round: gold-2 has no prior machine verdicts, and a clean first read is worth more than a prefilled one. Models are blinded as A/B under a fresh key. Answer **A** · **B** · **neither** · **skip** per entry.

The source dataset is named under each address — these are records of real properties, so public listings are fair evidence.

---

## 1. `% SHIRLEY FRIDAY PERS REP 13 1139 LEILANI AVE PAHOA HI 96778`
*AK — https://maps.matsugov.us/map/rest/services/OpenData/Cadastral_Parcels/FeatureSer*

| | Token | Model A | Model B |
|---|---|---|---|
| | `SHIRLEY` | Recipient | Recipient |
| | `FRIDAY` | Recipient | Recipient |
| | `PERS` | Recipient | Recipient |
| **←** | `REP` | **Recipient** | **SubaddressType** |
| | `13` | SubaddressIdentifier | SubaddressIdentifier |
| | `1139` | AddressNumber | AddressNumber |
| | `LEILANI` | StreetName | StreetName |
| | `AVE` | StreetNamePostType | StreetNamePostType |
| | `PAHOA` | PlaceName | PlaceName |
| | `HI` | StateName | StateName |
| | `96778` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 2. `74 LAKESHORE VIEW WEST JASPER AL 35503`
*AL — https://jccgis.jccal.org/server/rest/services/Basemap/Parcels/MapServer/0*

| | Token | Model A | Model B |
|---|---|---|---|
| | `74` | AddressNumber | AddressNumber |
| | `LAKESHORE` | StreetName | StreetName |
| **←** | `VIEW` | **StreetNamePostType** | **StreetName** |
| **←** | `WEST` | **PlaceName** | **StreetName** |
| | `JASPER` | PlaceName | PlaceName |
| | `AL` | StateName | StateName |
| | `35503` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 3. `5423 ROSEMARY ROAD MT OLIVE ALQ 35117`
*AL — https://jccgis.jccal.org/server/rest/services/Basemap/Parcels/MapServer/0*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5423` | AddressNumber | AddressNumber |
| | `ROSEMARY` | StreetName | StreetName |
| **←** | `ROAD` | **StreetName** | **StreetNamePostType** |
| **←** | `MT` | **StreetNamePostType** | **PlaceName** |
| | `OLIVE` | PlaceName | PlaceName |
| **←** | `ALQ` | **StateName** | **PlaceName** |
| | `35117` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 4. `7090 PINECREST PARK CITY UT 840985387`
*CO — https://services.arcgis.com/aXqye4IXyXsdIpPb/arcgis/rest/services/TaxParcelsPubl*

| | Token | Model A | Model B |
|---|---|---|---|
| | `7090` | AddressNumber | AddressNumber |
| | `PINECREST` | StreetName | StreetName |
| **←** | `PARK` | **StreetNamePostType** | **PlaceName** |
| | `CITY` | PlaceName | PlaceName |
| | `UT` | StateName | StateName |
| | `840985387` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 5. `163 SOUTH ST #93 DANBURY CT 06810`
*CT — https://data.ct.gov/resource/pqrn-qghw.json*

| | Token | Model A | Model B |
|---|---|---|---|
| | `163` | AddressNumber | AddressNumber |
| **←** | `SOUTH` | **StreetNamePreDirectional** | **StreetName** |
| **←** | `ST` | **StreetNamePreType** | **StreetNamePostType** |
| **←** | `#` | **StreetName** | **OccupancyIdentifier** |
| **←** | `93` | **StreetName** | **OccupancyIdentifier** |
| | `DANBURY` | PlaceName | PlaceName |
| | `CT` | StateName | StateName |
| | `06810` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 6. `4411 BEE RIDGE RD PMB 177 SARASOTA FL 34233`
*FL — https://services9.arcgis.com/Gh9awoU677aKree0/arcgis/rest/services/Florida_State*

| | Token | Model A | Model B |
|---|---|---|---|
| | `4411` | AddressNumber | AddressNumber |
| | `BEE` | StreetName | StreetName |
| | `RIDGE` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `PMB` | **SubaddressType** | **OccupancyType** |
| **←** | `177` | **SubaddressIdentifier** | **OccupancyIdentifier** |
| | `SARASOTA` | PlaceName | PlaceName |
| | `FL` | StateName | StateName |
| | `34233` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 7. `2289 WILEY ST PORT CHARLOTTE FL 33952`
*FL — https://services9.arcgis.com/Gh9awoU677aKree0/arcgis/rest/services/Florida_State*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2289` | AddressNumber | AddressNumber |
| | `WILEY` | StreetName | StreetName |
| **←** | `ST` | **StreetName** | **StreetNamePostType** |
| **←** | `PORT` | **StreetNamePostType** | **PlaceName** |
| | `CHARLOTTE` | PlaceName | PlaceName |
| | `FL` | StateName | StateName |
| | `33952` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 8. `3039 POMONA WAY EAST POINT GA 30344`
*GA — https://gismaps.fultoncountyga.gov/arcgispub2/rest/services/PropertyMapViewer/Pr*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3039` | AddressNumber | AddressNumber |
| | `POMONA` | StreetName | StreetName |
| | `WAY` | StreetNamePostType | StreetNamePostType |
| **←** | `EAST` | **StreetNamePostDirectional** | **PlaceName** |
| | `POINT` | PlaceName | PlaceName |
| | `GA` | StateName | StateName |
| | `30344` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 9. `5742 BARRINGTON RUN UNION CITY GA 30291-6104`
*GA — https://gismaps.fultoncountyga.gov/arcgispub2/rest/services/PropertyMapViewer/Pr*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5742` | AddressNumber | AddressNumber |
| | `BARRINGTON` | StreetName | StreetName |
| **←** | `RUN` | **PlaceName** | **StreetNamePostType** |
| | `UNION` | PlaceName | PlaceName |
| | `CITY` | PlaceName | PlaceName |
| | `GA` | StateName | StateName |
| | `30291-6104` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 10. `5562 VILLAGE TRCE UNION CITY GA 30291-5147`
*GA — https://gismaps.fultoncountyga.gov/arcgispub2/rest/services/PropertyMapViewer/Pr*

| | Token | Model A | Model B |
|---|---|---|---|
| | `5562` | AddressNumber | AddressNumber |
| | `VILLAGE` | StreetName | StreetName |
| **←** | `TRCE` | **PlaceName** | **StreetNamePostType** |
| | `UNION` | PlaceName | PlaceName |
| | `CITY` | PlaceName | PlaceName |
| | `GA` | StateName | StateName |
| | `30291-5147` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 11. `6488 OLD COLONY BEND ROCKFORD IL 61108`
*IL — https://services9.arcgis.com/s8vOzt2hgxqrWawQ/arcgis/rest/services/Parcels_and_A*

| | Token | Model A | Model B |
|---|---|---|---|
| | `6488` | AddressNumber | AddressNumber |
| | `OLD` | StreetName | StreetName |
| | `COLONY` | StreetName | StreetName |
| **←** | `BEND` | **StreetNamePostType** | **StreetName** |
| | `ROCKFORD` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `61108` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 12. `616 LANAE WAY SOUTH BELOIT IL 61080`
*IL — https://services9.arcgis.com/s8vOzt2hgxqrWawQ/arcgis/rest/services/Parcels_and_A*

| | Token | Model A | Model B |
|---|---|---|---|
| | `616` | AddressNumber | AddressNumber |
| | `LANAE` | StreetName | StreetName |
| | `WAY` | StreetNamePostType | StreetNamePostType |
| **←** | `SOUTH` | **StreetNamePostDirectional** | **PlaceName** |
| | `BELOIT` | PlaceName | PlaceName |
| | `IL` | StateName | StateName |
| | `61080` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 13. `3906 N LAKE RIDGE WICHITA KS 67205-5206`
*KS — https://services3.arcgis.com/PRyeAMTgQS8gkd0F/arcgis/rest/services/Maize_Parcels*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3906` | AddressNumber | AddressNumber |
| | `N` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `LAKE` | StreetName | StreetName |
| **←** | `RIDGE` | **StreetNamePostType** | **StreetName** |
| | `WICHITA` | PlaceName | PlaceName |
| | `KS` | StateName | StateName |
| | `67205-5206` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 14. `3131 N DEN HOLLOW WICHITA KS 67205-8741`
*KS — https://services3.arcgis.com/PRyeAMTgQS8gkd0F/arcgis/rest/services/Maize_Parcels*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3131` | AddressNumber | AddressNumber |
| | `N` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `DEN` | StreetName | StreetName |
| **←** | `HOLLOW` | **StreetNamePostType** | **StreetName** |
| | `WICHITA` | PlaceName | PlaceName |
| | `KS` | StateName | StateName |
| | `67205-8741` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 15. `C/O DOLLAR GENERAL - LEASE ADMIN DEPT 100 MISSION RIDGE`
*LA — https://data.brla.gov/resource/myfc-nh6n.json*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `DOLLAR` | Recipient | Recipient |
| | `GENERAL` | Recipient | Recipient |
| | `LEASE` | Recipient | Recipient |
| | `ADMIN` | Recipient | Recipient |
| **←** | `DEPT` | **Recipient** | **SubaddressType** |
| **←** | `100` | **AddressNumber** | **SubaddressIdentifier** |
| **←** | `MISSION` | **StreetName** | **PlaceName** |
| **←** | `RIDGE` | **StreetNamePostType** | **PlaceName** |

**Your verdict:** `      `

---

## 16. `C/O HEALTHCARE PROPERTIES 113 EAST ST. PETER ST.`
*LA — https://data.brla.gov/resource/myfc-nh6n.json*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `HEALTHCARE` | Recipient | Recipient |
| | `PROPERTIES` | Recipient | Recipient |
| | `113` | AddressNumber | AddressNumber |
| **←** | `EAST` | **StreetNamePreDirectional** | **StreetName** |
| | `ST.` | StreetName | StreetName |
| | `PETER` | StreetName | StreetName |
| | `ST.` | StreetNamePostType | StreetNamePostType |

**Your verdict:** `      `

---

## 17. `201 HIGHLAND OAKS BATON ROUGE, LA 70810`
*LA — https://data.brla.gov/resource/myfc-nh6n.json*

| | Token | Model A | Model B |
|---|---|---|---|
| | `201` | AddressNumber | AddressNumber |
| | `HIGHLAND` | StreetName | StreetName |
| **←** | `OAKS` | **PlaceName** | **StreetName** |
| | `BATON` | PlaceName | PlaceName |
| | `ROUGE,` | PlaceName | PlaceName |
| | `LA` | StateName | StateName |
| | `70810` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 18. `C/O 548 PROPERTIES, LLC 4023 HUNDRED OAKS AVE`
*LA — https://data.brla.gov/resource/myfc-nh6n.json*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `C/O` | **USPSBoxType** | **Recipient** |
| **←** | `548` | **USPSBoxID** | **Recipient** |
| **←** | `PROPERTIES,` | **SubaddressType** | **Recipient** |
| **←** | `LLC` | **SubaddressIdentifier** | **Recipient** |
| | `4023` | AddressNumber | AddressNumber |
| | `HUNDRED` | StreetName | StreetName |
| | `OAKS` | StreetName | StreetName |
| | `AVE` | StreetNamePostType | StreetNamePostType |

**Your verdict:** `      `

---

## 19. `ATTN: ROBERT S. MILLER 527 N ACADIAN THWY`
*LA — https://data.brla.gov/resource/myfc-nh6n.json*

| | Token | Model A | Model B |
|---|---|---|---|
| | `ATTN:` | Recipient | Recipient |
| | `ROBERT` | Recipient | Recipient |
| | `S.` | Recipient | Recipient |
| | `MILLER` | Recipient | Recipient |
| | `527` | AddressNumber | AddressNumber |
| **←** | `N` | **StreetNamePreDirectional** | **StreetNamePostDirectional** |
| **←** | `ACADIAN` | **StreetName** | **PlaceName** |
| **←** | `THWY` | **StreetName** | **PlaceName** |

**Your verdict:** `      `

---

## 20. `100 B SO MAIN ST MIDDLETON MA 01949`
*MA — https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/services/Massachusetts*

| | Token | Model A | Model B |
|---|---|---|---|
| | `100` | AddressNumber | AddressNumber |
| | `B` | AddressNumberSuffix | AddressNumberSuffix |
| **←** | `SO` | **StreetName** | **StreetNamePreDirectional** |
| | `MAIN` | StreetName | StreetName |
| | `ST` | StreetNamePostType | StreetNamePostType |
| | `MIDDLETON` | PlaceName | PlaceName |
| | `MA` | StateName | StateName |
| | `01949` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 21. `3 HONEY LOCUST CT, 21221`
*MD — https://services1.arcgis.com/UWYHeuuJISiGmgXx/arcgis/rest/services/Real_property*

| | Token | Model A | Model B |
|---|---|---|---|
| | `3` | AddressNumber | AddressNumber |
| | `HONEY` | StreetName | StreetName |
| **←** | `LOCUST` | **StreetName** | **PlaceName** |
| **←** | `CT,` | **StreetNamePostType** | **StateName** |
| | `21221` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 22. `ROOSEVELT TRAIL 29 POINT SEBAGO ROAD CASCO ME`
*ME — https://services1.arcgis.com/RbMX0mRVOFNTdLzd/arcgis/rest/services/Maine_Parcels*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `ROOSEVELT` | **BuildingName** | **LandmarkName** |
| **←** | `TRAIL` | **BuildingName** | **LandmarkName** |
| **←** | `29` | **AddressNumber** | **StreetName** |
| | `POINT` | StreetName | StreetName |
| | `SEBAGO` | StreetName | StreetName |
| | `ROAD` | StreetNamePostType | StreetNamePostType |
| | `CASCO` | PlaceName | PlaceName |
| | `ME` | StateName | StateName |

**Your verdict:** `      `

---

## 23. `0 SWANS RD C/O ROBERT FOGG RAYMOND ME`
*ME — https://services1.arcgis.com/RbMX0mRVOFNTdLzd/arcgis/rest/services/Maine_Parcels*

| | Token | Model A | Model B |
|---|---|---|---|
| | `0` | AddressNumber | AddressNumber |
| | `SWANS` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `C/O` | **Recipient** | **PlaceName** |
| **←** | `ROBERT` | **Recipient** | **PlaceName** |
| **←** | `FOGG` | **Recipient** | **PlaceName** |
| **←** | `RAYMOND` | **Recipient** | **PlaceName** |
| **←** | `ME` | **Recipient** | **StateName** |

**Your verdict:** `      `

---

## 24. `16890 E 8 MILE DETROIT MI 48205*1519`
*MI — https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/Parcels_Curre*

| | Token | Model A | Model B |
|---|---|---|---|
| | `16890` | AddressNumber | AddressNumber |
| | `E` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `8` | StreetName | StreetName |
| **←** | `MILE` | **StreetNamePostType** | **StreetName** |
| | `DETROIT` | PlaceName | PlaceName |
| | `MI` | StateName | StateName |
| | `48205*1519` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 25. `15 E KIRBY # 914 DETROIT MI 48226`
*MI — https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/Parcels_Curre*

| | Token | Model A | Model B |
|---|---|---|---|
| | `15` | AddressNumber | AddressNumber |
| | `E` | StreetNamePreDirectional | StreetNamePreDirectional |
| **←** | `KIRBY` | **StreetNamePreType** | **StreetName** |
| **←** | `#` | **StreetName** | **OccupancyIdentifier** |
| **←** | `914` | **StreetName** | **OccupancyIdentifier** |
| | `DETROIT` | PlaceName | PlaceName |
| | `MI` | StateName | StateName |
| | `48226` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 26. `14744 W CHICAGO DETROIT MI 48224`
*MI — https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/Parcels_Curre*

| | Token | Model A | Model B |
|---|---|---|---|
| | `14744` | AddressNumber | AddressNumber |
| | `W` | StreetNamePreDirectional | StreetNamePreDirectional |
| **←** | `CHICAGO` | **PlaceName** | **StreetName** |
| | `DETROIT` | PlaceName | PlaceName |
| | `MI` | StateName | StateName |
| | `48224` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 27. `6617 Jeffery Bay S Cottage Grove, MN 55016`
*MN — https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_mngeo/plan_pa*

| | Token | Model A | Model B |
|---|---|---|---|
| | `6617` | AddressNumber | AddressNumber |
| | `Jeffery` | StreetName | StreetName |
| | `Bay` | StreetName | StreetName |
| **←** | `S` | **StreetName** | **StreetNamePostDirectional** |
| **←** | `Cottage` | **StreetName** | **PlaceName** |
| **←** | `Grove,` | **StreetName** | **PlaceName** |
| **←** | `MN` | **StreetNamePostType** | **StateName** |
| | `55016` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 28. `Jeffrey W & Cindy Lou Larson 6973 Cty Rd 37 Nw Akeley, MN 56433`
*MN — https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_mngeo/plan_pa*

| | Token | Model A | Model B |
|---|---|---|---|
| | `Jeffrey` | Recipient | Recipient |
| | `W` | Recipient | Recipient |
| | `&` | Recipient | Recipient |
| | `Cindy` | Recipient | Recipient |
| | `Lou` | Recipient | Recipient |
| | `Larson` | Recipient | Recipient |
| | `6973` | AddressNumber | AddressNumber |
| **←** | `Cty` | **StreetNamePreType** | **StreetName** |
| **←** | `Rd` | **StreetNamePreType** | **StreetName** |
| | `37` | StreetName | StreetName |
| | `Nw` | StreetNamePostDirectional | StreetNamePostDirectional |
| | `Akeley,` | PlaceName | PlaceName |
| | `MN` | StateName | StateName |
| | `56433` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 29. `6641 Jeffery Bay S Cottage Grove, MN 55016`
*MN — https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_mngeo/plan_pa*

| | Token | Model A | Model B |
|---|---|---|---|
| | `6641` | AddressNumber | AddressNumber |
| | `Jeffery` | StreetName | StreetName |
| | `Bay` | StreetName | StreetName |
| **←** | `S` | **StreetName** | **StreetNamePostDirectional** |
| **←** | `Cottage` | **StreetName** | **PlaceName** |
| **←** | `Grove,` | **StreetName** | **PlaceName** |
| **←** | `MN` | **StreetNamePostType** | **StateName** |
| | `55016` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 30. `2459 S TRL RIDGE AVE INDEPENDENCE MO 64055`
*MO — https://services.arcgis.com/sbDzK061dd6DNPHv/arcgis/rest/services/COI_Parcels_2_*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2459` | AddressNumber | AddressNumber |
| | `S` | StreetNamePreDirectional | StreetNamePreDirectional |
| **←** | `TRL` | **StreetName** | **StreetNamePreType** |
| | `RIDGE` | StreetName | StreetName |
| | `AVE` | StreetNamePostType | StreetNamePostType |
| | `INDEPENDENCE` | PlaceName | PlaceName |
| | `MO` | StateName | StateName |
| | `64055` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 31. `2504 US HWY 70 CONNELLY SPRINGS NC 28612`
*NC — https://services.nconemap.gov/secure/rest/services/NC1Map_Parcels/FeatureServer/*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2504` | AddressNumber | AddressNumber |
| | `US` | StreetNamePreType | StreetNamePreType |
| | `HWY` | StreetNamePreType | StreetNamePreType |
| | `70` | StreetName | StreetName |
| **←** | `CONNELLY` | **PlaceName** | **StreetName** |
| | `SPRINGS` | PlaceName | PlaceName |
| | `NC` | StateName | StateName |
| | `28612` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 32. `51 W CENTER ST PMB 600 C/O HAVEN PARK COMMUNITIES OREM UT 84057`
*ND — https://gisweb.casscountynd.gov/arcgis/rest/services/OpenData/OpenData/FeatureSe*

| | Token | Model A | Model B |
|---|---|---|---|
| | `51` | AddressNumber | AddressNumber |
| | `W` | StreetNamePreDirectional | StreetNamePreDirectional |
| | `CENTER` | StreetName | StreetName |
| | `ST` | StreetNamePostType | StreetNamePostType |
| **←** | `PMB` | **SubaddressType** | **OccupancyType** |
| **←** | `600` | **SubaddressIdentifier** | **OccupancyIdentifier** |
| | `C/O` | PlaceName | PlaceName |
| | `HAVEN` | PlaceName | PlaceName |
| | `PARK` | PlaceName | PlaceName |
| | `COMMUNITIES` | PlaceName | PlaceName |
| | `OREM` | PlaceName | PlaceName |
| | `UT` | StateName | StateName |
| | `84057` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 33. `2347 20 1/2 AVE S FARGO ND 58103`
*ND — https://gisweb.casscountynd.gov/arcgis/rest/services/OpenData/OpenData/FeatureSe*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2347` | AddressNumber | AddressNumber |
| **←** | `20` | **StreetNamePreDirectional** | **StreetName** |
| | `1/2` | StreetName | StreetName |
| | `AVE` | StreetNamePostType | StreetNamePostType |
| | `S` | StreetNamePostDirectional | StreetNamePostDirectional |
| | `FARGO` | PlaceName | PlaceName |
| | `ND` | StateName | StateName |
| | `58103` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 34. `40 HIGHLAND DRIVE WEST CALDWELL NJ 07006`
*NJ — https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Parcels_Compo*

| | Token | Model A | Model B |
|---|---|---|---|
| | `40` | AddressNumber | AddressNumber |
| | `HIGHLAND` | StreetName | StreetName |
| | `DRIVE` | StreetNamePostType | StreetNamePostType |
| **←** | `WEST` | **StreetNamePostDirectional** | **PlaceName** |
| | `CALDWELL` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07006` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 35. `13 ST CHARLES AVENUE WEST CALDWELL NJ 07006`
*NJ — https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Parcels_Compo*

| | Token | Model A | Model B |
|---|---|---|---|
| | `13` | AddressNumber | AddressNumber |
| | `ST` | StreetName | StreetName |
| | `CHARLES` | StreetName | StreetName |
| | `AVENUE` | StreetNamePostType | StreetNamePostType |
| **←** | `WEST` | **PlaceName** | **StreetNamePostDirectional** |
| | `CALDWELL` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07006` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 36. `38 HIGHLAND DRIVE WEST CALDWELL NJ 07006`
*NJ — https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Parcels_Compo*

| | Token | Model A | Model B |
|---|---|---|---|
| | `38` | AddressNumber | AddressNumber |
| | `HIGHLAND` | StreetName | StreetName |
| | `DRIVE` | StreetNamePostType | StreetNamePostType |
| **←** | `WEST` | **StreetNamePostDirectional** | **PlaceName** |
| | `CALDWELL` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07006` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 37. `8 ST CHARLES AVENUE WEST CALDWELL NJ 07006`
*NJ — https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Parcels_Compo*

| | Token | Model A | Model B |
|---|---|---|---|
| | `8` | AddressNumber | AddressNumber |
| | `ST` | StreetName | StreetName |
| | `CHARLES` | StreetName | StreetName |
| | `AVENUE` | StreetNamePostType | StreetNamePostType |
| **←** | `WEST` | **PlaceName** | **StreetNamePostDirectional** |
| | `CALDWELL` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07006` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 38. `7 RICHARD AVENUE WEST CALDWELL NJ 07006`
*NJ — https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Parcels_Compo*

| | Token | Model A | Model B |
|---|---|---|---|
| | `7` | AddressNumber | AddressNumber |
| | `RICHARD` | StreetName | StreetName |
| | `AVENUE` | StreetNamePostType | StreetNamePostType |
| **←** | `WEST` | **PlaceName** | **StreetNamePostDirectional** |
| | `CALDWELL` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07006` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 39. `7 ST CHARLES AVENUE WEST CALDWELL NJ 07006`
*NJ — https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Parcels_Compo*

| | Token | Model A | Model B |
|---|---|---|---|
| | `7` | AddressNumber | AddressNumber |
| | `ST` | StreetName | StreetName |
| | `CHARLES` | StreetName | StreetName |
| | `AVENUE` | StreetNamePostType | StreetNamePostType |
| **←** | `WEST` | **PlaceName** | **StreetNamePostDirectional** |
| | `CALDWELL` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07006` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 40. `6 JOHNSON AVENUE WEST CALDWELL NJ 07006`
*NJ — https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Parcels_Compo*

| | Token | Model A | Model B |
|---|---|---|---|
| | `6` | AddressNumber | AddressNumber |
| | `JOHNSON` | StreetName | StreetName |
| | `AVENUE` | StreetNamePostType | StreetNamePostType |
| **←** | `WEST` | **PlaceName** | **StreetNamePostDirectional** |
| | `CALDWELL` | PlaceName | PlaceName |
| | `NJ` | StateName | StateName |
| | `07006` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 41. `C/O JACK ANDERSON 845 CAMINO DE LAS TRAMPAS SANTA FE NM 87501`
*NM — https://services7.arcgis.com/p0Gk2nDbPs7KEqSZ/arcgis/rest/services/SFC_Parcels_2*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `JACK` | Recipient | Recipient |
| | `ANDERSON` | Recipient | Recipient |
| **←** | `845` | **Recipient** | **AddressNumber** |
| **←** | `CAMINO` | **Recipient** | **StreetName** |
| **←** | `DE` | **Recipient** | **StreetName** |
| **←** | `LAS` | **Recipient** | **StreetName** |
| **←** | `TRAMPAS` | **Recipient** | **StreetName** |
| | `SANTA` | PlaceName | PlaceName |
| | `FE` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `87501` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 42. `2042 OLD US 66 EDGEWOOD NM 87015-6740`
*NM — https://services7.arcgis.com/p0Gk2nDbPs7KEqSZ/arcgis/rest/services/SFC_Parcels_2*

| | Token | Model A | Model B |
|---|---|---|---|
| | `2042` | AddressNumber | AddressNumber |
| **←** | `OLD` | **StreetNamePreModifier** | **StreetName** |
| **←** | `US` | **StreetNamePreType** | **StreetName** |
| | `66` | StreetName | StreetName |
| | `EDGEWOOD` | PlaceName | PlaceName |
| | `NM` | StateName | StateName |
| | `87015-6740` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 43. `KAREN MORENO & ERASMO COSIO, TTEES 254 WINDTREE CIR CARSON CITY, NV 89701-`
*NV — https://portal.carsoncity.gov/server/rest/services/CarsonCity/CarsonCityNV_OpenD*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `KAREN` | **Recipient** | **BuildingName** |
| **←** | `MORENO` | **Recipient** | **BuildingName** |
| **←** | `&` | **Recipient** | **BuildingName** |
| **←** | `ERASMO` | **Recipient** | **BuildingName** |
| **←** | `COSIO,` | **Recipient** | **BuildingName** |
| **←** | `TTEES` | **Recipient** | **BuildingName** |
| | `254` | AddressNumber | AddressNumber |
| | `WINDTREE` | StreetName | StreetName |
| | `CIR` | StreetNamePostType | StreetNamePostType |
| | `CARSON` | PlaceName | PlaceName |
| | `CITY,` | PlaceName | PlaceName |
| | `NV` | StateName | StateName |
| | `89701-` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 44. `JAMES ALLEN JARRARD, TRUSTEE 3860 GS RICHARDS BLVD CARSON CITY, NV 89703-0000`
*NV — https://portal.carsoncity.gov/server/rest/services/CarsonCity/CarsonCityNV_OpenD*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `JAMES` | **Recipient** | **BuildingName** |
| **←** | `ALLEN` | **Recipient** | **BuildingName** |
| **←** | `JARRARD,` | **Recipient** | **BuildingName** |
| **←** | `TRUSTEE` | **Recipient** | **BuildingName** |
| | `3860` | AddressNumber | AddressNumber |
| | `GS` | StreetName | StreetName |
| | `RICHARDS` | StreetName | StreetName |
| | `BLVD` | StreetNamePostType | StreetNamePostType |
| | `CARSON` | PlaceName | PlaceName |
| | `CITY,` | PlaceName | PlaceName |
| | `NV` | StateName | StateName |
| | `89703-0000` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 45. `6289 WINTERBERRY CROSSING BEDFORD OH 44146`
*OH — https://gis.cuyahogacounty.us/server/rest/services/MyPLACE/Parcels_WMA_GJOIN_WGS*

| | Token | Model A | Model B |
|---|---|---|---|
| | `6289` | AddressNumber | AddressNumber |
| | `WINTERBERRY` | StreetName | StreetName |
| **←** | `CROSSING` | **StreetNamePostType** | **StreetName** |
| | `BEDFORD` | PlaceName | PlaceName |
| | `OH` | StateName | StateName |
| | `44146` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 46. `POX 3326 MERRIFIELD VA 22119`
*OH — https://gis.cuyahogacounty.us/server/rest/services/MyPLACE/Parcels_WMA_GJOIN_WGS*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `POX` | **SubaddressType** | **USPSBoxType** |
| **←** | `3326` | **SubaddressIdentifier** | **USPSBoxID** |
| | `MERRIFIELD` | PlaceName | PlaceName |
| | `VA` | StateName | StateName |
| | `22119` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 47. `342 LANTANA XING SPRING BRANCH, TX 78070`
*OR — https://services1.arcgis.com/znO8Hz1SuVVohYhZ/arcgis/rest/services/Taxlots/Featu*

| | Token | Model A | Model B |
|---|---|---|---|
| | `342` | AddressNumber | AddressNumber |
| | `LANTANA` | StreetName | StreetName |
| **←** | `XING` | **PlaceName** | **StreetNamePostType** |
| | `SPRING` | PlaceName | PlaceName |
| | `BRANCH,` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78070` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 48. `342 LATANA CROSSING SPRING BRANCH, TX 78070`
*OR — https://services1.arcgis.com/znO8Hz1SuVVohYhZ/arcgis/rest/services/Taxlots/Featu*

| | Token | Model A | Model B |
|---|---|---|---|
| | `342` | AddressNumber | AddressNumber |
| | `LATANA` | StreetName | StreetName |
| **←** | `CROSSING` | **PlaceName** | **StreetName** |
| | `SPRING` | PlaceName | PlaceName |
| | `BRANCH,` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78070` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 49. `8213 22ND ST CT W TACOMA, WA 98466`
*OR — https://services1.arcgis.com/znO8Hz1SuVVohYhZ/arcgis/rest/services/Taxlots/Featu*

| | Token | Model A | Model B |
|---|---|---|---|
| | `8213` | AddressNumber | AddressNumber |
| | `22ND` | StreetName | StreetName |
| | `ST` | StreetName | StreetName |
| | `CT` | StreetNamePostType | StreetNamePostType |
| **←** | `W` | **PlaceName** | **StreetNamePostDirectional** |
| | `TACOMA,` | PlaceName | PlaceName |
| | `WA` | StateName | StateName |
| | `98466` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 50. `1218 GREEN ST EXT ROCK HILL SC 29730`
*SC — https://services1.arcgis.com/2AGLxyiJoNiVHKwq/arcgis/rest/services/Parcels/Featu*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1218` | AddressNumber | AddressNumber |
| | `GREEN` | StreetName | StreetName |
| | `ST` | StreetNamePostType | StreetNamePostType |
| **←** | `EXT` | **StreetNamePostModifier** | **PlaceName** |
| | `ROCK` | PlaceName | PlaceName |
| | `HILL` | PlaceName | PlaceName |
| | `SC` | StateName | StateName |
| | `29730` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 51. `320 WESTBERRY CT W RAPID CITY SD 57702-2712`
*SD — https://gis.rcgov.org/server/rest/services/OpenData/TaxParcels/FeatureServer/0*

| | Token | Model A | Model B |
|---|---|---|---|
| | `320` | AddressNumber | AddressNumber |
| | `WESTBERRY` | StreetName | StreetName |
| | `CT` | StreetNamePostType | StreetNamePostType |
| **←** | `W` | **PlaceName** | **StreetNamePostDirectional** |
| | `RAPID` | PlaceName | PlaceName |
| | `CITY` | PlaceName | PlaceName |
| | `SD` | StateName | StateName |
| | `57702-2712` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 52. `377 WESTBERRY CT W RAPID CITY SD 57702-2712`
*SD — https://gis.rcgov.org/server/rest/services/OpenData/TaxParcels/FeatureServer/0*

| | Token | Model A | Model B |
|---|---|---|---|
| | `377` | AddressNumber | AddressNumber |
| | `WESTBERRY` | StreetName | StreetName |
| | `CT` | StreetNamePostType | StreetNamePostType |
| **←** | `W` | **PlaceName** | **StreetNamePostDirectional** |
| | `RAPID` | PlaceName | PlaceName |
| | `CITY` | PlaceName | PlaceName |
| | `SD` | StateName | StateName |
| | `57702-2712` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 53. `808 BRYAN ST OLD HICKORY TN 37138`
*TN — https://services2.arcgis.com/HdTo6HJqh92wn4D8/arcgis/rest/services/Parcels_view/*

| | Token | Model A | Model B |
|---|---|---|---|
| | `808` | AddressNumber | AddressNumber |
| | `BRYAN` | StreetName | StreetName |
| | `ST` | StreetNamePostType | StreetNamePostType |
| **←** | `OLD` | **StreetNamePreModifier** | **PlaceName** |
| | `HICKORY` | PlaceName | PlaceName |
| | `TN` | StateName | StateName |
| | `37138` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 54. `14901 APPLE SPRINGS HOLW LEANDER TX 78641`
*TX — https://gis.georgetowntexas.gov/arcgis/rest/services/OpenData/OpenData_FeatureSe*

| | Token | Model A | Model B |
|---|---|---|---|
| | `14901` | AddressNumber | AddressNumber |
| | `APPLE` | StreetName | StreetName |
| | `SPRINGS` | StreetName | StreetName |
| **←** | `HOLW` | **StreetNamePostType** | **StreetName** |
| | `LEANDER` | PlaceName | PlaceName |
| | `TX` | StateName | StateName |
| | `78641` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 55. `1501 Rayanne Dr N Chesterfield VA 23238`
*VA — https://services1.arcgis.com/k3vhq11XkBNeeOfM/arcgis/rest/services/Parcels/Featu*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1501` | AddressNumber | AddressNumber |
| | `Rayanne` | StreetName | StreetName |
| | `Dr` | StreetNamePostType | StreetNamePostType |
| **←** | `N` | **StreetNamePostDirectional** | **PlaceName** |
| | `Chesterfield` | PlaceName | PlaceName |
| | `VA` | StateName | StateName |
| | `23238` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 56. `P.O. BOX 418 MONTGOMERY CENTER VERMONT 05471`
*VT — https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPEND*

| | Token | Model A | Model B |
|---|---|---|---|
| | `P.O.` | USPSBoxType | USPSBoxType |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `418` | USPSBoxID | USPSBoxID |
| | `MONTGOMERY` | PlaceName | PlaceName |
| | `CENTER` | PlaceName | PlaceName |
| **←** | `VERMONT` | **StateName** | **PlaceName** |
| | `05471` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 57. `74 LILAC LN S BURLINGTON VT 05403`
*VT — https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPEND*

| | Token | Model A | Model B |
|---|---|---|---|
| | `74` | AddressNumber | AddressNumber |
| | `LILAC` | StreetName | StreetName |
| | `LN` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **StreetNamePostDirectional** | **PlaceName** |
| | `BURLINGTON` | PlaceName | PlaceName |
| | `VT` | StateName | StateName |
| | `05403` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 58. `343 COBBLESTONE CIRCLE S BURLINGTON VT 05403`
*VT — https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPEND*

| | Token | Model A | Model B |
|---|---|---|---|
| | `343` | AddressNumber | AddressNumber |
| | `COBBLESTONE` | StreetName | StreetName |
| | `CIRCLE` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **StreetNamePostDirectional** | **PlaceName** |
| | `BURLINGTON` | PlaceName | PlaceName |
| | `VT` | StateName | StateName |
| | `05403` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 59. `P.O.BOX 1305 DERBY VT 05829`
*VT — https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPEND*

| | Token | Model A | Model B |
|---|---|---|---|
| **←** | `P.O.BOX` | **SubaddressType** | **USPSBoxType** |
| **←** | `1305` | **SubaddressIdentifier** | **USPSBoxID** |
| | `DERBY` | PlaceName | PlaceName |
| | `VT` | StateName | StateName |
| | `05829` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 60. `58 FIELDSTONE DR S BURLINGTON VT 05403`
*VT — https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPEND*

| | Token | Model A | Model B |
|---|---|---|---|
| | `58` | AddressNumber | AddressNumber |
| | `FIELDSTONE` | StreetName | StreetName |
| | `DR` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **StreetNamePostDirectional** | **PlaceName** |
| | `BURLINGTON` | PlaceName | PlaceName |
| | `VT` | StateName | StateName |
| | `05403` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 61. `51 MEADOW RD S BURLINGTON VT 05403`
*VT — https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPEND*

| | Token | Model A | Model B |
|---|---|---|---|
| | `51` | AddressNumber | AddressNumber |
| | `MEADOW` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **StreetNamePostDirectional** | **PlaceName** |
| | `BURLINGTON` | PlaceName | PlaceName |
| | `VT` | StateName | StateName |
| | `05403` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 62. `1560 WILLISTON RD S BURLINGTON VT 05403`
*VT — https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPEND*

| | Token | Model A | Model B |
|---|---|---|---|
| | `1560` | AddressNumber | AddressNumber |
| | `WILLISTON` | StreetName | StreetName |
| | `RD` | StreetNamePostType | StreetNamePostType |
| **←** | `S` | **StreetNamePostDirectional** | **PlaceName** |
| | `BURLINGTON` | PlaceName | PlaceName |
| | `VT` | StateName | StateName |
| | `05403` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 63. `52 STONEHOUSE COMMONS S BURLINGTONG VT 05403`
*VT — https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPEND*

| | Token | Model A | Model B |
|---|---|---|---|
| | `52` | AddressNumber | AddressNumber |
| | `STONEHOUSE` | StreetName | StreetName |
| **←** | `COMMONS` | **StreetNamePostType** | **StreetName** |
| | `S` | StreetNamePostDirectional | StreetNamePostDirectional |
| | `BURLINGTONG` | PlaceName | PlaceName |
| | `VT` | StateName | StateName |
| | `05403` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## 64. `C/O STEVEN SPARKS, P O BOX 239, DIXIE, WV 25059`
*WV — https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels*

| | Token | Model A | Model B |
|---|---|---|---|
| | `C/O` | Recipient | Recipient |
| | `STEVEN` | Recipient | Recipient |
| | `SPARKS,` | Recipient | Recipient |
| **←** | `P` | **USPSBoxType** | **Recipient** |
| | `O` | USPSBoxType | USPSBoxType |
| | `BOX` | USPSBoxType | USPSBoxType |
| | `239,` | USPSBoxID | USPSBoxID |
| | `DIXIE,` | PlaceName | PlaceName |
| | `WV` | StateName | StateName |
| | `25059` | ZipCode | ZipCode |

**Your verdict:** `      `

---

## When you're done

Paste answers back in any form. They get un-blinded, stored with the approved label sequences, and the pre-registered gates compute from human verdicts only. This is scoring attempt 2 of 2 against gold-2 — the attempt count ships with any claim either way.