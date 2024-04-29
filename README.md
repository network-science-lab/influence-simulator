# Influence Simulator

Package for simulating influence in networks


## Installation
```bash
pip install git+https://github.com/network-science-lab/influence-simulator
```


## Usage

### In code
```python 
from influence_simulator import InfluenceSimulator


simulator = InfluenceSimulator(
    "Facebook.gml",
    infection_probability=0.1,
    random_state=2042,
)
simulator.simulate()

simulator.save_result("out.csv")
```

### Command line interface
```bash
influence-simulator Facebook.gml 0.1 \
    --output ./simulation_results/ \
    --random-state 2042 \
    --n-jobs 6 \
    --chunksize 10 \
    --verbose
```

