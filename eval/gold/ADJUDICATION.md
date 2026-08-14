# Adjudication round 2 — 0 addresses need your call

The parsers now disagree on 49 of 1,500 messy addresses (16 distinct shapes). **16 shapes carry your verdicts forward from last time and need no action** — they are listed at the bottom for reference only. That leaves **0 groups covering 0 addresses** to judge.

**Models are blinded as A and B on purpose.** Judge which parse is *correct*, not which model you expect to win. (The A/B mapping is recorded in the repo, so the result stays auditable.)

**Census evidence is attached where it exists.** The US Census geocoder (public domain, so it can be published with the eval set) says what the real address looks like — house number, street name, street type, city. Treat it as *evidence*, not as the answer: it reports a canonical address, not usaddress's token labels, and its component names do not carry every distinction in the schema. Where it says *no match*, it abstained — which is common on exactly the messy inputs that are hardest to judge.

## How to fill this out

For each group, replace the `Verdict:` value with **A**, **B**, **neither**, or **skip** (use skip when the address is genuinely ambiguous). If one address in a group deserves a different answer than the rest, add a line under it — group verdicts are defaults, not handcuffs.

Labels are usaddress component names: `AddressNumber`, `StreetName`, `StreetNamePostType` (St/Ave/Rd), `StreetNamePreDirectional` (N/S/E/W before the name), `PlaceName` (city), `StateName`, `ZipCode`, `OccupancyType`/`OccupancyIdentifier` (Apt 4B), `USPSBoxType`/`USPSBoxID` (PO Box 12), `Recipient`, `LandmarkName`, `BuildingName`.

---

## Already decided last round — no action needed

These shapes match verdicts you already gave; they are carried forward automatically and listed only so the record is complete.

- 31 address(es) differing on `51`, `ST`, `JAMES` — your prior verdict favors **Model A** here
- 3 address(es) differing on `Square,` — your prior verdict favors **Model B** here
- 2 address(es) differing on `140` — your prior verdict favors **Model B** here
- 1 address(es) differing on `Terra`, `Alta,` — your prior verdict favors **Model A** here
- 1 address(es) differing on `RD`, `MT` — your prior verdict favors **Model B** here
- 1 address(es) differing on `LK` — your prior verdict favors **Model A** here
- 1 address(es) differing on `US`, `6`, `Ind` — your prior verdict favors **Model B** here
- 1 address(es) differing on `Mile`, `K`, `Beach` — your prior verdict favors **Model B** here
- 1 address(es) differing on `Mi`, `K`, `Beach` — your prior verdict favors **Model B** here
- 1 address(es) differing on `E`, `NORTH`, `WATER` — your prior verdict favors **Model A** here
- 1 address(es) differing on `ORL`, `FL` — your prior verdict favors **Model A** here
- 1 address(es) differing on `Miami` — your prior verdict favors **Model B** here
- 1 address(es) differing on `Route`, `313`, `RR` — your prior verdict favors **Model B** here
- 1 address(es) differing on `WILSHIRE`, `1210` — your prior verdict favors **Model B** here
- 1 address(es) differing on `BROADWAY`, `NEW` — your prior verdict favors **Model B** here
- 1 address(es) differing on `ST`, `UNT`, `D` — your prior verdict favors **Model B** here

---

## When you're done

Tell the agent it's filled in. It will read the verdicts, un-blind them, and score the gold gate — which decides whether the retrained model ships or stays shelved.

Disclosed limitation: judging only contested cases measures *relative* accuracy on the cases where the parsers differ, not absolute accuracy across all 1,500. It informs the decision; it does not replace the full-set gate in the protocol.