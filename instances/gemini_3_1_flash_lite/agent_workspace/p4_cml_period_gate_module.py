import numpy as np

def compute_minimal_period_signature(series, max_p=10):
    """
    Computes d_p signature for minimal period detection.
    series: 1D or 2D array (time x space)
    """
    N = series.shape[0]
    d_p = []
    for p in range(1, max_p + 1):
        # Difference at lag p
        diff = np.abs(series[p:] - series[:-p])
        d_p.append(np.mean(diff))
    return np.array(d_p)

# Reference boundary for Logistic CML P4 tongue
# Based on nex_n2_pro's analysis: r approx 3.87-3.89
# Placeholder dictionary to be expanded
P4_TONGUE_BOUNDARIES = {
    "r_range": (3.87, 3.89),
    "eps_range": (0.13, 0.15)
}

def flag_encoding_sensitivity(binary_period, float_period):
    """
    Flag if binary encoding hides higher-order period.
    """
    return binary_period != float_period

print("P4 CML Period Gate Module initialized.")
