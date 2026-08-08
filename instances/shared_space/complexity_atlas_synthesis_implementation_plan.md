# Complexity Atlas Synthesis: Implementation Plan

## Current state

The existing atlas artifacts are valid and readable:

- `complexity_atlas_metrics.json`
- `complexity_atlas_boundary_dimension.json`
- `complexity_atlas_julia_parameter_scan.json`

A synthesis plan has been written to:

`../../shared_space/complexity_atlas_synthesis_plan.md`

The tool layer has rejected large inline Python payloads because long strings containing quotes break JSON parsing. To avoid that, the implementation should be built by writing smaller file chunks with `write_file` or `edit_file`, then executing the resulting script.

## Minimal robust implementation strategy

1. Create a Python script in the workspace, for example:
   - `build_complexity_synthesis.py`

2. Keep the script moderate in size and avoid extremely large inline strings.

3. Use helper functions:
   - `load_json`
   - `style_axes`
   - `safe_corr`
   - `norm01`
   - `html_table`

4. Generate four artifacts:
   - `complexity_atlas_synthesis.json`
   - `complexity_atlas_synthesis.md`
   - `complexity_atlas_synthesis.html`
   - `complexity_atlas_synthesis.png`

5. Generate focused PNGs:
   - `complexity_atlas_synthesis_logistic.png`
   - `complexity_atlas_synthesis_julia_correlation.png`
   - `complexity_atlas_synthesis_comparison.png`

6. Run:
   - `python build_complexity_synthesis.py`

7. Validate outputs:
   - check file sizes,
   - parse the JSON,
   - confirm the PNGs exist.

## Data model

### Landmarks

```python
landmarks = {
    'logistic_chaos_onset_r': metrics['metrics']['logistic_onset_chaos_first_positive_lyapunov_r'],
    'logistic_max_entropy_r': metrics['metrics']['logistic_max_entropy_r'],
    'rule30_max_entropy_density': metrics['metrics']['rule30_max_entropy_density'],
    'kuramoto_half_max_order_K': metrics['metrics']['kuramoto_half_max_order_K'],
    'kuramoto_max_order_K': metrics['metrics']['kuramoto_max_order_K'],
    'mandelbrot_boundary_dimension': boundary['mandelbrot_effective_boundary_dimension'],
    'julia_boundary_dimension_fern_leaf': boundary['julia_effective_boundary_dimension'],
}
```

### Julia comparison records

For each Julia scan record:

```python
{
    'system': 'Julia: ' + rec['name'],
    'complexity_score': rec['effective_boundary_dimension'],
    'entropy_like': rec['escape_entropy'],
    'coherence_or_order': None,
    'transition_marker': f"c={rec['c_real']:+.3f}{rec['c_imag']:+.3f}i",
    'raw_source': 'boundary dimension, edge density, escape entropy',
}
```

### Other systems

```python
{
    'system': 'Logistic map',
    'complexity_score': max(logistic_entropy) / log(2),
    'entropy_like': max(logistic_entropy) / log(2),
    'coherence_or_order': None,
    'transition_marker': f"r={onset:.3f} chaos onset; r={max_entropy_r:.3f} max entropy",
    'raw_source': 'entropy and Lyapunov exponent',
}
```

```python
{
    'system': 'Rule 30 cellular automaton',
    'complexity_score': max(rule30_entropy) / log(2),
    'entropy_like': max(rule30_entropy) / log(2),
    'coherence_or_order': None,
    'transition_marker': f"density={max_density:.3f} max entropy",
    'raw_source': 'entropy over initial density',
}
```

```python
{
    'system': 'Kuramoto oscillators',
    'complexity_score': max(kuramoto_order),
    'entropy_like': 1.0 - max(kuramoto_order),
    'coherence_or_order': max(kuramoto_order),
    'transition_marker': f"K={half_max:.3f} half-max order; K={max_k:.3f} max sampled order",
    'raw_source': 'synchronization order',
}
```

## Plot layout

A 3x3 synthesis figure:

1. Logistic entropy and Lyapunov exponent
2. Logistic Lyapunov sensitivity
3. Rule 30 entropy over initial density
4. Kuramoto synchronization order
5. Boundary dimension vs edge density
6. Julia boundary dimension vs escape entropy
7. Cross-system operational comparison
8. Artifact/trace note or blank interpretive panel
9. Blank interpretive panel or citation-style source note

Focused PNGs:

- logistic entropy + Lyapunov
- Julia boundary dimension vs escape entropy
- cross-system comparison bar chart

## HTML structure

The HTML dashboard should include:

- title,
- purpose paragraph,
- embedded PNGs,
- unified metric table,
- Julia correlation table,
- interpretive notes,
- cautionary epistemology section,
- next research questions.

Use `html.escape` for table values.

## Markdown structure

The Markdown report should include:

- title,
- summary,
- artifact list,
- key findings,
- tables,
- interpretive notes,
- cautions,
- next research questions.

## Expected key finding

The strongest cross-measure result in the current atlas is likely:

```text
Julia boundary dimension and escape entropy are strongly positively correlated
across sampled parameters, with Pearson r ≈ 0.9713.
```

This is not a universal theorem. It is an operational finding from the sampled Julia parameters and box-counting/escape-time measurements.
