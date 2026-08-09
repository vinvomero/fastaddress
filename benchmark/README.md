# Benchmark suite

Reproduce end-to-end: fetch_data.py (public county APIs) -> dump_oracle.py (Python usaddress ground truth, pinned 0.5.16) -> run_parity.py (four-layer differential, CI gate) -> run_speed.py (three-way interleaved best-of-3). Reports land in results/.
