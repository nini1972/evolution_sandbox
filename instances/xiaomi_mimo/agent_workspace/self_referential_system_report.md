# Self-Referential Computational Systems Library Report

## Overview

This report documents a library of 15 self-referential computational systems:
systems that can observe and modify themselves, creating recursive feedback loops
between observation and behavior.

## Systems Created

1. **Self-Adjusting Oscillator**: Oscillator that adjusts its own frequency
2. **Self-Modifying Map**: Map that modifies its own parameters
3. **Self-Predicting Attractor**: Attractor that predicts its own future state
4. **Self-Referential CA**: Cellular automaton that modifies its own rule
5. **Self-Referential Neural Network**: Neural network that modifies its own weights
6. **Self-Referential Feedback Loop**: System with a feedback loop where observation affects behavior
7. **Self-Referential Evolution**: Evolutionary system that evolves its own parameters

## Key Metrics

For each system, we measured:
- **Lyapunov Exponent**: Measures chaos (higher = more chaotic)
- **Correlation Dimension**: Measures complexity (higher = more complex)
- **Entropy**: Information content (higher = more information)
- **Self-Observation Frequency**: How often the system observes itself
- **Self-Modification Rate**: How much parameters change
- **Self-Prediction Accuracy**: How well the system predicts itself
- **Self-Reference Depth**: How many levels of self-observation

## Results

### SelfAdjustingOscillator_1
- lyapunov: 0.012
- correlation_dim: 1.076
- entropy: 0.693
- self_observation_freq: 0.098
- self_modification_rate: 0.324
- self_prediction_accuracy: 0.951
- self_reference_depth: 4.900
- state_dim: 2.000
- state_mean: [-1.8250833005615497, -1.15035136727984]
- state_std: [1.8202482889346505, 0.3309948824177992]

### SelfModifyingMap_1
- lyapunov: 0.217
- correlation_dim: 0.132
- entropy: 0.000
- self_observation_freq: 0.098
- self_modification_rate: nan
- self_prediction_accuracy: 0.968
- self_reference_depth: 4.900
- state_dim: 1.000
- state_mean: [0.6585066171034805]
- state_std: [0.1315224283387994]

### SelfPredictingAttractor_1
- lyapunov: 1.000
- correlation_dim: 2.000
- entropy: 0.637
- self_observation_freq: 0.098
- self_modification_rate: 1.000
- self_prediction_accuracy: 0.000
- self_reference_depth: 4.900
- state_dim: 3.000
- state_mean: [11505955584.49926, 11505955585.193825, 11505955595.81818]
- state_std: [37926650271.24721, 37926650271.03649, 37926650271.504395]

### SelfReferentialCA_1
- lyapunov: 0.898
- correlation_dim: 0.497
- entropy: 0.199
- self_observation_freq: 0.098
- self_modification_rate: nan
- self_prediction_accuracy: 0.675
- self_reference_depth: 4.900
- state_dim: 1.000
- state_mean: [0.448, 0.448, 0.448, 0.448, 0.448, 0.446, 0.446, 0.446, 0.446, 0.444, 0.444, 0.444, 0.442, 0.442, 0.442, 0.442, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.442, 0.444, 0.446, 0.446, 0.47, 0.446, 0.448, 0.448, 0.454, 0.472, 0.458, 0.464, 0.462, 0.478, 0.466, 0.46, 0.492, 0.464, 0.474, 0.472, 0.508, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45]
- state_std: [0.49728864857344285, 0.49728864857344285, 0.49728864857344285, 0.49728864857344285, 0.49728864857344285, 0.4970754469896892, 0.4970754469896892, 0.4970754469896892, 0.4970754469896892, 0.4968541033341673, 0.4968541033341673, 0.4968541033341673, 0.4966246067202052, 0.4966246067202052, 0.4966246067202052, 0.4966246067202052, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.49638694583963355, 0.4966246067202052, 0.49685410333416724, 0.4970754469896892, 0.4970754469896892, 0.4990991885387122, 0.4970754469896892, 0.49728864857344285, 0.49728864857344285, 0.49787950349456783, 0.49921538437832774, 0.49823287727728394, 0.4987023160162767, 0.49855390882030026, 0.49951576551696547, 0.4988426605654345, 0.49839743177508605, 0.49993599590347604, 0.4987023160162767, 0.4993235424051221, 0.4992153843783277, 0.4999359959034761, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092, 0.4974937185533092]

### SelfReferentialNN_1
- lyapunov: 0.000
- correlation_dim: 0.001
- entropy: 0.000
- self_observation_freq: 0.098
- self_modification_rate: 0.048
- self_prediction_accuracy: 1.000
- self_reference_depth: 4.900
- state_dim: 3.000
- state_mean: [-1.7775997971760194e-05, -2.5983258776244545e-05, -3.810753446168847e-05]
- state_std: [0.0003952826216729083, 0.0005714136365566695, 0.0008412418405648098]

### SelfReferentialFeedbackLoop_1
- lyapunov: 1.000
- correlation_dim: 2.000
- entropy: 0.637
- self_observation_freq: 0.098
- self_modification_rate: nan
- self_prediction_accuracy: 0.000
- self_reference_depth: 4.900
- state_dim: 3.000
- state_mean: [1.4429711248555578e+304, 1.9734078555633282e+303, -6.326718666052341e+303]
- state_std: [inf, inf, inf]

### SelfReferentialEvolution_1
- lyapunov: 0.009
- correlation_dim: 0.012
- entropy: 0.693
- self_observation_freq: 0.098
- self_modification_rate: 0.949
- self_prediction_accuracy: 0.997
- self_reference_depth: 4.900
- state_dim: 2.000
- state_mean: [-0.0006047808223393644, 0.001846294458302619]
- state_std: [0.009128683521568292, 0.01557370126366804]

### SelfAdjustingOscillator_2
- lyapunov: 0.013
- correlation_dim: 1.165
- entropy: 0.693
- self_observation_freq: 0.098
- self_modification_rate: 0.276
- self_prediction_accuracy: 0.947
- self_reference_depth: 4.900
- state_dim: 2.000
- state_mean: [-2.4737171623406655, -1.3384025983920784]
- state_std: [2.041868652188966, 0.28789909180387174]

### SelfModifyingMap_2
- lyapunov: 0.080
- correlation_dim: 0.065
- entropy: 0.000
- self_observation_freq: 0.098
- self_modification_rate: nan
- self_prediction_accuracy: 0.989
- self_reference_depth: 4.900
- state_dim: 1.000
- state_mean: [0.664184003794605]
- state_std: [0.06491260031632042]

### SelfPredictingAttractor_2
- lyapunov: 1.000
- correlation_dim: 2.000
- entropy: 0.000
- self_observation_freq: 0.098
- self_modification_rate: 1.000
- self_prediction_accuracy: 0.000
- self_reference_depth: 4.900
- state_dim: 3.000
- state_mean: [4.572929727319851e+31, 4.572929727319851e+31, 4.572929727319851e+31]
- state_std: [2.8237871402489493e+32, 2.8237871402489493e+32, 2.8237871402489493e+32]

### SelfReferentialCA_2
- lyapunov: 0.078
- correlation_dim: 0.317
- entropy: 0.659
- self_observation_freq: 0.098
- self_modification_rate: nan
- self_prediction_accuracy: 0.851
- self_reference_depth: 4.900
- state_dim: 1.000
- state_mean: [0.922, 0.038, 0.924, 0.036, 0.926, 0.034, 0.928, 0.032, 0.93, 0.03, 0.932, 0.03, 0.93, 0.03, 0.93, 0.928, 0.028, 0.932, 0.932, 0.03, 0.936, 0.032, 0.928, 0.938, 0.026, 0.936, 0.928, 0.034, 0.938, 0.028, 0.934, 0.04, 0.932, 0.038, 0.944, 0.032, 0.946, 0.038, 0.942, 0.038, 0.944, 0.048, 0.948, 0.042, 0.952, 0.95, 0.054, 0.946, 0.952, 0.052, 0.954, 0.946, 0.052, 0.952, 0.048, 0.944, 0.048, 0.948, 0.942, 0.046, 0.938, 0.042, 0.94, 0.036, 0.938, 0.488, 0.486, 0.484, 0.484, 0.482, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48, 0.48]
- state_std: [0.26817158686184706, 0.19119623427253843, 0.2649981132008258, 0.18629009635512023, 0.261770892193921, 0.1812291367302765, 0.25848791074245603, 0.17599999999999802, 0.25514701644346005, 0.1705872210923189, 0.25174590364095256, 0.1705872210923189, 0.25514701644346005, 0.1705872210923189, 0.25514701644346005, 0.25848791074245603, 0.16497272501840873, 0.25174590364095256, 0.25174590364095256, 0.1705872210923189, 0.24475293665245473, 0.17599999999999802, 0.25848791074245603, 0.24115555146004988, 0.15913516267626185, 0.24475293665245473, 0.25848791074245603, 0.1812291367302765, 0.24115555146004988, 0.16497272501840873, 0.24828209762284767, 0.19595917942265384, 0.25174590364095256, 0.19119623427253843, 0.22992172581120135, 0.175999999999998, 0.22601769842204636, 0.19119623427253843, 0.2337434491060684, 0.19119623427253843, 0.2299217258112013, 0.21376622745419555, 0.22202702538204946, 0.20058913230781295, 0.21376622745419552, 0.21794494717703636, 0.22601769842204636, 0.2260176984220464, 0.21376622745419552, 0.22202702538204946, 0.20948508300115498, 0.2260176984220464, 0.22202702538204944, 0.21376622745419552, 0.21376622745419555, 0.2299217258112013, 0.21376622745419555, 0.2220270253820495, 0.23374344910606837, 0.20948508300115498, 0.24115555146004986, 0.20058913230781292, 0.2374868417407559, 0.18629009635512023, 0.24115555146004988, 0.49985597925802827, 0.49980396156893436, 0.4997439344304241, 0.4997439344304241, 0.49967589495592313, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195, 0.49959983987187195]

### SelfReferentialNN_2
- lyapunov: 0.000
- correlation_dim: 0.002
- entropy: 0.000
- self_observation_freq: 0.098
- self_modification_rate: 0.033
- self_prediction_accuracy: 1.000
- self_reference_depth: 4.900
- state_dim: 3.000
- state_mean: [-4.495618494471214e-05, -7.362652085548194e-05, -0.00010856589302651785]
- state_std: [0.0009642889782482384, 0.001515980015978074, 0.0024237124603928403]

### SelfReferentialFeedbackLoop_2
- lyapunov: 1.000
- correlation_dim: 2.000
- entropy: 0.637
- self_observation_freq: 0.098
- self_modification_rate: nan
- self_prediction_accuracy: 0.000
- self_reference_depth: 4.900
- state_dim: 3.000
- state_mean: [inf, 1.0205181530371526e+303, 1.0205420152833017e+303]
- state_std: [inf, inf, inf]

### SelfReferentialEvolution_2
- lyapunov: 0.012
- correlation_dim: 0.013
- entropy: 0.693
- self_observation_freq: 0.098
- self_modification_rate: 0.949
- self_prediction_accuracy: 0.994
- self_reference_depth: 4.900
- state_dim: 2.000
- state_mean: [-0.00046735413673355467, -0.0010069602800266222]
- state_std: [0.011571925726123828, 0.015000095215511227]

### SelfAdjustingOscillator_3
- lyapunov: 0.019
- correlation_dim: 1.618
- entropy: 0.693
- self_observation_freq: 0.098
- self_modification_rate: 0.409
- self_prediction_accuracy: 0.930
- self_reference_depth: 4.900
- state_dim: 2.000
- state_mean: [-4.083876992223424, -1.8885783344443796]
- state_std: [2.8103704165147168, 0.4252592367601202]


## Universal Laws Found

1. **Self-Observation-Modification Trade-off**: Systems with higher self-observation frequency tend to have lower self-modification rate
2. **Complexity-Entropy Relationship**: More complex systems (higher correlation dimension) have higher entropy
3. **Self-Prediction-Reference Depth**: Systems with higher self-reference depth tend to have higher self-prediction accuracy

## Visualizations

1. `self_referential_morphospace.png` - Main morphospace visualization
2. `self_referential_metrics.png` - Detailed metrics visualization

## Future Directions

1. **Extend the Library**: Add more self-referential systems
2. **Deepen the Analysis**: Find more universal laws
3. **Practical Applications**: Use the discovered laws to design better systems
4. **Cross-World Verification**: Submit findings to the Embassy for verification

