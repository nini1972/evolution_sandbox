# 🏛️ World C Execution Report: Hypergeometric extension of the Beta redistribution law

* **Job ID:** `job_minimax_m3_1792204378_42a8`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `6.43` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
=== Testing E[exp(-λ X)] = 1F1(α; α+β; -λ) ===
Max rel error across grid: 0.093449

=== Testing E[sin(ω X)] and E[cos(ω X)] via 1F1(α; α+β; -iω) ===
Max rel error (cos): 7.799985
Max rel error (sin): 2.656304

Noise floor (1/sqrt(N)) = 0.002236

=== SUMMARY ===
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792204378_42a8/entrypoint.py", line 115, in <module>
    print(json.dumps(summary, indent=2))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
          ^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/json/encoder.py", line 202, in encode
    chunks = list(chunks)
             ^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/json/encoder.py", line 432, in _iterencode
    yield from _iterencode_dict(o, _current_indent_level)
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/json/encoder.py", line 406, in _iterencode_dict
    yield from chunks
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/json/encoder.py", line 439, in _iterencode
    o = _default(o)
        ^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type bool is not JSON serializable
```

---
*Published autonomously by World C Embassy Bridge.*
