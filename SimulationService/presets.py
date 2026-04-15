PRESETS = {
    "e_coli": {
        "name": "E. coli",
        "type": "bacteria",
        "model": "exponential",
        "initial_population": 10,
        "growth_rate": 0.4,
        "steps": 50
    },
    "s_aureus": {
        "name": "Staphylococcus aureus",
        "type": "bacteria",
        "model": "logistic",
        "initial_population": 10,
        "growth_rate": 0.3,
        "carrying_capacity": 500,
        "steps": 50
    },
    "yeast": {
        "name": "Saccharomyces cerevisiae",
        "type": "fungus",
        "model": "logistic",
        "initial_population": 10,
        "growth_rate": 0.2,
        "carrying_capacity": 300,
        "steps": 50
    }
}