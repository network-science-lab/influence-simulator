# Influence Simulator

Package for simulating influence in networks


## Installation
```bash
pip install "influence-simulator[internal] @ git+https://github.com/network-science-lab/influence-simulator"
```


## Usage

### In code
```python 
from influence_simulator import IndependentCascadeSimulator
from influence_simulator.utils import load_graph

graph = load_graph("Facebook.gml")
simulator = IndependentCascadeSimulator(
    graph,
    infection_probability=0.1,
    random_state=2042,
)
simulator.simulate()

simulator.save_result("out.csv")
```

### Command line interface
```bash
influence-simulator \
    Facebook.gml \
    model_config.json \
    --output ./simulation_results/ \
    --n-jobs 6 \
    --chunksize 10 \
    --verbose
```


#### Model config example:

```json
{
    "type": "IndependentCascadeSimulator",
    "infection_probability": 0.1,
    "random_state": 2042
}
```

