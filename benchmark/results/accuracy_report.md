# Accuracy Report

## clean (159 rows)

Original model exact match: **100.00%** (0 tokenization-mismatch rows counted as miss)

| Label (top by error volume) | Precision | Recall | Support |
|---|---|---|---|
| AddressNumber | 1.000 | 1.000 | 131 |
| StreetName | 1.000 | 1.000 | 165 |
| StreetNamePostType | 1.000 | 1.000 | 96 |
| StreetNamePostDirectional | 1.000 | 1.000 | 18 |
| OccupancyType | 1.000 | 1.000 | 27 |
| OccupancyIdentifier | 1.000 | 1.000 | 38 |
| StreetNamePreDirectional | 1.000 | 1.000 | 39 |
| StreetNamePreType | 1.000 | 1.000 | 42 |

Candidate exact match: **95.60%** (diff -4.40pp, 95% CI [-7.55, -1.26])

## gold-adjudicated: no scoreable records yet
(1500 candidates exist; none adjudicated — gates pending human adjudication per protocol)

## Pre-registered gates
- clean gate (>= -1.0pp): FAIL
