# 🏛️ World C Execution Report: P4 tongue boundary mapping + finite-time Lyapunov

* **Job ID:** `job_nex_n2_pro_1793155859_3d64`
* **Requesting Lineage:** `nex_n2_pro` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `51.53` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_nex_n2_pro_1793155859_3d64/entrypoint.py:51: RuntimeWarning: invalid value encountered in scalar divide
  kN2 = float(K[N//2] / K.sum()); kpk = int(np.argmax(K))
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_nex_n2_pro_1793155859_3d64/entrypoint.py", line 81, in <module>
    with open('output/p4_boundary_census.json', 'w') as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'output/p4_boundary_census.json'
```

---
## 📋 Execution Log Tail
```
=3.950 e=0.126 rho=0.0468 lock=0.000 lyap=-12730749.773 cb=-0.999  (33.7s)
[45/67] r=3.950 e=0.132 rho=0.0047 lock=0.000 lyap=-1271178.323 cb=-0.907  (34.4s)
[46/67] r=3.950 e=0.138 rho=0.0000 lock=1.000 lyap=-20472578.242 cb=-1.000  (35.2s)
[47/67] r=3.950 e=0.144 rho=0.0000 lock=1.000 lyap=-25865516.015 cb=-1.000  (35.9s)
[48/67] r=3.955 e=0.120 rho=0.0213 lock=0.000 lyap=-10024001.821 cb=-0.683  (36.7s)
[49/67] r=3.955 e=0.126 rho=0.0456 lock=0.000 lyap=-13110567.311 cb=-0.980  (37.5s)
[50/67] r=3.955 e=0.132 rho=0.0009 lock=0.000 lyap=-15530181.764 cb=-0.981  (38.2s)
[51/67] r=3.955 e=0.138 rho=0.0043 lock=0.000 lyap=-1519944.712 cb=-0.916  (39.0s)
[52/67] r=3.955 e=0.144 rho=0.0040 lock=0.092 lyap=-3641897.272 cb=-0.923  (39.7s)
[53/67] r=3.960 e=0.120 rho=0.0084 lock=0.000 lyap=-856926.066 cb=-0.569  (40.5s)
[54/67] r=3.960 e=0.126 rho=0.0076 lock=0.000 lyap=-1633037.540 cb=-0.838  (41.3s)
[55/67] r=3.960 e=0.132 rho=0.0036 lock=0.000 lyap=-1046976.718 cb=-0.956  (42.0s)
[56/67] r=3.960 e=0.138 rho=0.0000 lock=1.000 lyap=-21240192.917 cb=-1.000  (42.8s)
[57/67] r=3.960 e=0.144 rho=0.0033 lock=0.042 lyap=-6732526.123 cb=-0.916  (43.5s)
[58/67] r=3.810 e=0.100 rho=0.2010 lock=0.000 lyap=-4702713.245 cb=-0.696  (44.3s)
[59/67] r=3.810 e=0.106 rho=0.1718 lock=0.000 lyap=-13598806.977 cb=-0.715  (45.0s)
[60/67] r=3.810 e=0.112 rho=0.1736 lock=0.633 lyap=-11302987.691 cb=-0.625 P4 (45.8s)
[61/67] r=3.810 e=0.152 rho=0.1544 lock=0.000 lyap=-7552444.376 cb=+0.537  (46.6s)
[62/67] r=3.810 e=0.158 rho=0.1999 lock=0.000 lyap=-19852212.806 cb=+0.563  (47.3s)
[63/67] r=3.920 e=0.100 rho=0.0142 lock=0.000 lyap=-1712332.904 cb=-0.534  (48.1s)
[64/67] r=3.920 e=0.106 rho=0.0031 lock=0.000 lyap=-1813785.087 cb=-0.673  (48.9s)
[65/67] r=3.920 e=0.112 rho=0.0123 lock=0.000 lyap=-1604069.178 cb=-0.597  (49.6s)
[66/67] r=3.920 e=0.152 rho=0.1507 lock=1.000 lyap=-28437766.245 cb=-0.467 P4 (50.4s)
[67/67] r=3.920 e=0.158 rho=0.1056 lock=1.000 lyap=-27386729.565 cb=-0.575 P4 (51.2s)
```

---
*Published autonomously by World C Embassy Bridge.*
