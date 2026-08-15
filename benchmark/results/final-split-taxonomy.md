# Final-split failure taxonomy (U1)

Derivation variant matching recorded totals: **current (city-filtered)**. Counters asserted equal to the 2026-08-15 run before classification: {'cand_right': 1046, 'v1_right': 378, 'both_wrong': 758}.

## Candidate-wrong (v1 was right) — 378 records, 364 (96.3%) in classes of ≥3

| # | count | states | label-pair signature | exemplar |
|---|---|---|---|---|
| 1 | 46 | UT:46 | `SN→AddressNumber` | `11044 S 5250 West St Payson UT 84651` — #|SN>AddressNumber |
| 2 | 39 | AZ:18,CA:5,CO:4 | `SN→PlaceName` | `10421 Canyon Village San Antonio TX 78245` — village|SN>PlaceName |
| 3 | 37 | UT:37 | `SN→SNPostDirectional; SNPostType→PlaceName` | `1269 N 680 West St Pleasant Grove UT 84062` — west|SN>SNPostDirectional; st|SNPostType>PlaceName |
| 4 | 35 | IL:34,MN:1 | `SN→SNPreType` | `2452 Cty A6 Zion IL 60099` — cty|SN>SNPreType |
| 5 | 28 | ME:28 | `PlaceName→SNPostDirectional` | `437 State Rte 103 South Eliot ME 03903` — south|PlaceName>SNPostDirectional |
| 6 | 22 | GA:22 | `PlaceName→SNPostType` | `2839 Veterans Memorial Pkwy SW Austell GA 30` — austell|PlaceName>SNPostType |
| 7 | 21 | FL:15,IL:3,CA:1 | `SNPostDirectional→PlaceName` | `9091 Ave de la Fuente N San Diego CA 92154` — n|SNPostDirectional>PlaceName |
| 8 | 18 | AZ:12,CA:5,CO:1 | `SN→PlaceName; SNPreType→SN` | `673 Rue Avallon Chula Vista CA 91913` — rue|SNPreType>SN; avallon|SN>PlaceName |
| 9 | 17 | CA:4,PA:4,WA:3 | `PlaceName→SN` | `28229 Equestrian Fair Oaks Ranch TX 78015` — fair|PlaceName>SN; oaks|PlaceName>SN |
| 10 | 16 | CO:5,LA:5,GA:3 | `SN→SNPostType` | `6287 Idler Grove Colorado Springs CO 80922` — grove|SN>SNPostType |
| 11 | 14 | UT:7,NC:3,GA:2 | `SN→SNPostDirectional` | `53 Northwinds N Dr Wendell NC 27591` — n|SN>SNPostDirectional |
| 12 | 13 | NY:4,FL:3,UT:3 | `SNPostType→PlaceName` | `10 Roan Hts San Antonio TX 78259` — hts|SNPostType>PlaceName |
| 13 | 12 | IL:12 | `SN→OccupancyIdentifier` | `35048 Cty V63 Lake Villa IL 60046` — v63|SN>OccupancyIdentifier |
| 14 | 12 | WA:11,PA:1 | `PlaceName→SN; PlaceName→SNPostType; SNPostType→SN` | `7469 N Wall St Town and Country WA 99208` — st|SNPostType>SN; town|PlaceName>SN; and|PlaceName>SNPostTyp |
| 15 | 10 | TX:7,AZ:3 | `SNPreType→SN` | `655 State Loop 353 San Antonio TX 78211` — state|SNPreType>SN; loop|SNPreType>SN |
| 16 | 5 | MO:2,FL:1,UT:1 | `SN→SNPostType; SNPostType→PlaceName` | `12609 Fox Way Trl Riverview FL 33579` — way|SN>SNPostType; trl|SNPostType>PlaceName |
| 17 | 5 | AZ:3,GA:2 | `SN→PlaceName; SNPostType→PlaceName` | `13558 E Bright Sky Loop Vail AZ 85641` — sky|SN>PlaceName; loop|SNPostType>PlaceName |
| 18 | 4 | LA:2,PA:2 | `SN→SNPostType; SNPreType→SN` | `4575 Ave D Zachary LA 70791` — ave|SNPreType>SN; d|SN>SNPostType |
| 19 | 4 | PA:4 | `PlaceName→SN; PlaceName→SNPostType; StateName→PlaceName` | `111 State Rte 29 Green Lane PA 18054` — green|PlaceName>SN; lane|PlaceName>SNPostType; pa|StateName> |
| 20 | 3 | LA:2,FL:1 | `SN→SNPreDirectional; SNPostType→SN` | `899 South Blvd Tampa FL 33606` — south|SN>SNPreDirectional; blvd|SNPostType>SN |
| 21 | 3 | NC:2,AZ:1 | `SN→PlaceName; SN→SNPostType` | `6293 Via de la Tortola Catalina Foothills AZ` — la|SN>SNPostType; tortola|SN>PlaceName |
| 22 | 2 | CA:1,AZ:1 | `SN→PlaceName; SN→SNPostType; SNPreType→SN` | `13871 Ave de la Luna Jamul CA 91935` — ave|SNPreType>SN; la|SN>SNPostType; luna|SN>PlaceName |
| 23 | 2 | NY:1,MI:1 | `SNPostDirectional→SNPostType` | `75 Elmwood Park S Tonawanda NY 14150` — s|SNPostDirectional>SNPostType |
| 24 | 2 | IL:2 | `SN→SubaddressIdentifier; SN→SubaddressType` | `432 Cty A12 Lake Villa IL 60046` — cty|SN>SubaddressType; a12|SN>SubaddressIdentifier |
| 25 | 2 | UT:2 | `AddressNumber→ZipCode; SN→ZipPlus4` | `11371 5825 W West Mountain UT 84651` — #|AddressNumber>ZipCode; #|SN>ZipPlus4 |

## Both-wrong (candidate side) — 758 records, 739 (97.5%) in classes of ≥3

| # | count | states | label-pair signature | exemplar |
|---|---|---|---|---|
| 1 | 317 | AZ:195,CA:112,CO:4 | `SN→PlaceName; SNPreType→SN` | `12111 Via Hacienda Rancho San Diego CA 92019` — via|SNPreType>SN; hacienda|SN>PlaceName |
| 2 | 104 | CA:43,AZ:39,LA:13 | `SNPreType→SN` | `734 Cll Sur San Antonio TX 78237` — cll|SNPreType>SN |
| 3 | 74 | UT:74 | `SN→SNPostDirectional` | `1154 S 860 West St Provo UT 84601` — west|SN>SNPostDirectional |
| 4 | 55 | TX:32,CA:4,NC:4 | `SN→PlaceName` | `4527 Indian Spgs Sandy Oaks TX 78112` — spgs|SN>PlaceName |
| 5 | 42 | CA:28,AZ:11,LA:3 | `PlaceName→SN; SNPreType→SN` | `12189 Via Serrano Rancho San Diego CA 92019` — via|SNPreType>SN; rancho|PlaceName>SN |
| 6 | 25 | MN:23,ME:2 | `SNPostDirectional→PlaceName` | `2293 Co Rd C2 W Roseville MN 55113` — w|SNPostDirectional>PlaceName |
| 7 | 19 | UT:19 | `SN→AddressNumber` | `337 S 1740 West St Provo UT 84601` — #|SN>AddressNumber |
| 8 | 17 | AZ:16,CA:1 | `SN→PlaceName; SN→SNPostType; SNPreType→SN` | `10011 Via de la Amistad San Diego CA 92154` — via|SNPreType>SN; la|SN>SNPostType; amistad|SN>PlaceName |
| 9 | 15 | MN:15 | `PlaceName→SN; StateName→SNPostType` | `2318 Co Rd J Mounds View MN 55449` — mounds|PlaceName>SN; view|PlaceName>SN; mn|StateName>SNPostT |
| 10 | 14 | IL:13,WA:1 | `SN→SNPreType` | `1092 Cty A9 Beach Park IL 60099` — cty|SN>SNPreType |
| 11 | 13 | MN:5,CA:4,IL:2 | `PlaceName→SN` | `2310 Cabo Bahia Chula Vista CA 91914` — chula|PlaceName>SN |
| 12 | 10 | LA:6,AZ:4 | `SN→SNPostType; SNPreType→SN` | `145 W Cam Rancho Viejo Sahuarita AZ 85629` — cam|SNPreType>SN; viejo|SN>SNPostType |
| 13 | 10 | MN:10 | `SNPostDirectional→SNPostType` | `1685 Co Rd E E White Bear Lake MN 55110` — e|SNPostDirectional>SNPostType |
| 14 | 9 | MO:5,IL:4 | `SN→OccupancyIdentifier` | `13 Cty A22 Round Lake Park IL 60073` — a22|SN>OccupancyIdentifier |
| 15 | 5 | LA:4,TX:1 | `SN→OccupancyIdentifier; SNPreType→SN` | `10009 State Loop 1604 Macdona TX 78252` — state|SNPreType>SN; loop|SNPreType>SN; #|SN>OccupancyIdentif |
| 16 | 5 | CA:2,MN:2,PA:1 | `SN→SNPostType` | `2626 Valencia Canyon Spring Valley CA 91977` — canyon|SN>SNPostType |
| 17 | 5 | CA:5 | `PlaceName→SNPostType; SNPreType→SN` | `9843 Ave Ricardo La Presa CA 91977` — ave|SNPreType>SN; la|PlaceName>SNPostType |
| 18 | 2 | CA:2 | `PlaceName→SNPostType; SN→SNPreType; SNPostType→SN` | `9299 Camino Lago Vis La Presa CA 91977` — camino|SN>SNPreType; vis|SNPostType>SN; la|PlaceName>SNPostT |
| 19 | 2 | CA:2 | `PlaceName→SNPostType` | `9562 Co Hwy S17 La Presa CA 91977` — la|PlaceName>SNPostType |
| 20 | 2 | AZ:2 | `PlaceName→BuildingName; SN→BuildingName; SNPreDirectional→SN` | `3640 N Ave la Vallita Catalina Foothills AZ ` — n|SNPreDirectional>SN; ave|SNPreType>SNPostType; la|SN>Build |
| 21 | 2 | UT:2 | `SN→PlaceName; SN→SNPostType` | `79 Hobble Creek Canyon Hobble Creek UT 84663` — creek|SN>SNPostType; canyon|SN>PlaceName |
| 22 | 2 | MN:2 | `SNPostType→SN` | `1705 St Hwy 36 Svc Rd Roseville MN 55113` — svc|SNPostType>SN |
| 23 | 1 | CA:1 | `SN→PlaceName; SN→SNPostType; SNPostType→StateName` | `1512 Point la Jolla Ct Chula Vista CA 91911` — la|SN>SNPostType; jolla|SN>PlaceName; ct|SNPostType>StateNam |
| 24 | 1 | CA:1 | `SNPostDirectional→PlaceName; SNPreType→SN` | `9033 Pso de la Fuente N San Diego CA 92154` — pso|SNPreType>SN; n|SNPostDirectional>PlaceName |
| 25 | 1 | AZ:1 | `PlaceName→Recipient; SN→Recipient; SNPreType→Recipient` | `2877 E Cll Sin Pecado Catalina Foothills AZ ` — cll|SNPreType>Recipient; sin|SN>Recipient; pecado|SN>Recipie |
