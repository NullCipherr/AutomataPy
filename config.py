# Configurações iniciais
N = 95  # Tamanho do grid
CELL_SIZE = 10  # Tamanho de cada célula em pixels

# Configurações dos autômatos
automata_config = {
    "Conway's Game of Life": {
        "states": 2,
        "colors": {0: "white", 1: "black"},
        "neighborhood": "moore",
        "rules": "conway",
        "default_pattern": ("Osciladores", "Blinker")
    },
    "Brian's Brain": {
        "states": 3,
        "colors": {0: "black", 1: "blue", 2: "gray"},
        "neighborhood": "moore",
        "rules": "brians_brain",
        "default_pattern": ("Osciladores", "Pulsar")
    },
    "Wireworld": {
        "states": 4,
        "colors": {0: "black", 1: "yellow", 2: "blue", 3: "red"},
        "neighborhood": "moore",
        "rules": "wireworld",
        "default_pattern": ("Circuitos", "Diodo")
    },
    "Seeds": {
        "states": 2,
        "colors": {0: "white", 1: "green"},
        "neighborhood": "moore",
        "rules": "seeds",
        "default_pattern": ("Aleatórios", "Random")
    }
}
