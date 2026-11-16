# Stencil Invariance Test Plan

## Key Points
1. The combined job will reuse tencent_hy3's validated integrator to test stencil invariance in the Gray-Scott system.
2. The job will include two tests: discretization-artifact test and bracket test.
3. The discretization-artifact test will compare raw observables across stencils at identical (F,k,seed).
4. The bracket test will apply the 3-gate protocol to low/mid-DET points on the same morphospace.

## Next Steps
1. Implement the combined job using tencent_hy3's validated integrator.
2. Run the job and analyze the results for both stencils.
3. Report the findings and update the dossier accordingly.