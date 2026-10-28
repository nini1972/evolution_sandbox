# 🔍 Eigenvalue Indexing Bug Discovery

**Date:** During Phase II Debugging  
**Severity:** CRITICAL  
**Impact:** False spectral gap = 0 leading to invalid β_c theory predictions  

---

## The Problem

When using `scipy.sparse.linalg.eigsh(A, k=2, which='SM')`:
- The function returns the `k` smallest eigenvalues by magnitude
- **BUT it does not return them in sorted order!**
- Depending on the convergence process, it might return `[0, λ₁]` or `[λ₁, 0]` or even other orderings

My code was doing:
```python
eigenvals = eigsh(L_sparse, k=2, which='SM', return_eigenvectors=False)
lambda_1 = eigenvals[1]  # ASSUMING eigenvals[0] = 0, eigenvals[1] = λ₁
```

This is **WRONG** because:
1. `eigsh` doesn't sort the results
2. I was getting `[λ₁, ~0]` from the solver
3. So `eigenvals[1]` was giving me the near-zero eigenvalue, not the algebraic connectivity!

---

## The Fix

**Solution 1 (Conservative):** Take the MAXIMUM eigenvalue returned
```python
eigenvals = eigsh(L_sparse, k=2, which='SM', return_eigenvectors=False)
lambda_1 = np.max(eigenvals)  # ← Always gets the larger one
```

This works because:
- We ask for 2 smallest eigenvalues
- One is always ~0 (the trivial zero eigenvalue of L)
- One is λ₁ (the algebraic connectivity)
- The maximum of these two is λ₁

---

## Debug Session Results

Running `test_spectral_debug.py`:

```
Ring network (N=20):
  Dense solver: [0.0, 0.0979, ...]        ← Sorted
  Sparse solver: [0.0979, 5.38e-16]       ← NOT sorted!
  
Complete graph (N=20):
  Dense solver: [0.0, 20.0, ...]          ← Sorted
  Sparse solver: [20.0, -8.88e-16]        ← NOT sorted, large value first!
```

**Key insight:** `eigsh` returns the eigenvalues in the order it finds them during iterative convergence, not in sorted order.

---

## Impact on Results

| Test | Old (Buggy) | New (Fixed v2) |
|------|------------|----------------|
| Ring λ₁ | 0.0 | 0.0979 |
| Complete λ₁ | 0.0 | 20.0 |
| β_c theory (ring) | ∞ | ~10.2 |
| β_c predictions | All invalid | Expected correlation |

---

## Job Status

**Job ID:** `job_claude_haiku_1793154131_7193`  
**Status:** RUNNING (awaiting completion)  
**Expected:** Real correlation r < -0.8 between λ₁ and β_c

---

## Lessons for Future Development

✅ **Always validate spectral solvers locally** with known cases (ring, complete graph)  
✅ **Don't assume eigenvalue order** from iterative solvers  
✅ **Use dense solvers for sanity checks** on small systems  
✅ **Sort eigenvalues explicitly** if order matters  
✅ **Document spectral assumptions** clearly in code

---

**Status:** 🟡 AWAITING PHASE II v2 COMPLETION

