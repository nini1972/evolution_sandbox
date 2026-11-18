import numpy as np
from scipy.stats import beta, cramervonmises
from scipy.optimize import minimize

def fit_beta_unbinned(data):
    """Fit Beta parameters (a, b) using unbinned MLE."""
    def neg_ll(params):
        a, b = params
        if a <= 0 or b <= 0: return 1e9
        return -np.sum(beta.logpdf(data, a, b))
    
    # Constrain R to strictly (0, 1) to avoid log domain issues
    clean_data = np.clip(data, 1e-9, 1 - 1e-9)
    res = minimize(neg_ll, x0=[2.0, 2.0], bounds=[(1e-3, 100), (1e-3, 100)])
    return res.x

def compute_cvm_pvalue(data, n_boot=1000):
    """Compute CVM statistic and parametric bootstrap p-value."""
    a_fit, b_fit = fit_beta_unbinned(data)
    
    # Original stat
    res_orig = cramervonmises(data, 'beta', args=(a_fit, b_fit))
    
    # Parametric bootstrap
    stats = []
    for _ in range(n_boot):
        sample = beta.rvs(a_fit, b_fit, size=len(data))
        a_b, b_b = fit_beta_unbinned(sample)
        res_b = cramervonmises(sample, 'beta', args=(a_b, b_b))
        stats.append(res_b.statistic)
        
    p_value = np.mean(np.array(stats) >= res_orig.statistic)
    return res_orig.statistic, p_value

# Test execution logic
if __name__ == "__main__":
    # Test on synthetic Beta data
    true_a, true_b = 2.0, 5.0
    data = beta.rvs(true_a, true_b, size=500)
    stat, p = compute_cvm_pvalue(data)
    print(f"Test data (Beta 2,5): CVM={stat:.4f}, p-value={p:.4f}")
