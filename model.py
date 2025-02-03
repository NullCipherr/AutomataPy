# model.py

import numpy as np
from tkinter import filedialog
from PIL import Image
import imageio
from scipy.signal import convolve2d

from config import N, CELL_SIZE, automata_config
from patterns import patterns

class CellularAutomatonModel:
    def __init__(self, automaton_name="Conway's Game of Life"):
        self.current_automaton = automaton_name
        self.generation = 0
        self.speed = 100  # em milissegundos
        self.zoom = 1
        self.gif_frames = []
        self.setup_automaton()

    def setup_automaton(self):
        config = automata_config[self.current_automaton]
        self.states = config["states"]
        self.colors = config["colors"]
        self.grid = np.zeros((N, N), dtype=int)
        # O padrão default vem da configuração do autômato
        self.reset_grid(*config["default_pattern"])

    def step(self):
        """Executa uma iteração (geração) da simulação."""
        self.apply_rules()
        self.generation += 1

    def apply_rules(self):
        regra = automata_config[self.current_automaton]["rules"]
        if regra == "conway":
            self.apply_conway_rules()
        elif regra == "brians_brain":
            self.apply_brians_brain_rules()
        elif regra == "wireworld":
            self.apply_wireworld_rules()
        elif regra == "seeds":
            self.apply_seeds_rules()

    def apply_conway_rules(self):
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
        neighbors = convolve2d(self.grid, kernel, mode='same')
        new_grid = np.where((self.grid == 1) & ((neighbors == 2) | (neighbors == 3)), 1, 0)
        new_grid = np.where((self.grid == 0) & (neighbors == 3), 1, new_grid)
        self.grid = new_grid

    def apply_brians_brain_rules(self):
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
        new_grid = np.zeros_like(self.grid)
        new_grid[self.grid == 1] = 2  # células ativas passam para "em espera"
        new_grid[self.grid == 2] = 0  # células em espera morrem
        neighbors = convolve2d((self.grid == 1).astype(int), kernel, mode='same')
        new_grid[(self.grid == 0) & (neighbors == 2)] = 1
        self.grid = new_grid

    def apply_wireworld_rules(self):
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
        new_grid = np.zeros_like(self.grid)
        new_grid[self.grid == 1] = 2
        new_grid[self.grid == 2] = 3
        new_grid[self.grid == 3] = 0
        neighbors = convolve2d((self.grid == 1).astype(int), kernel, mode='same')
        new_grid[(self.grid == 0) & ((neighbors == 1) | (neighbors == 2))] = 1
        self.grid = new_grid

    def apply_seeds_rules(self):
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
        neighbors = convolve2d(self.grid, kernel, mode='same')
        new_grid = np.where((self.grid == 0) & (neighbors == 2), 1, 0)
        self.grid = new_grid

    def reset(self):
        """Reinicia o autômato com o padrão default."""
        self.setup_automaton()

    def reset_grid(self, category, pattern):
        """Reinicia o grid aplicando um padrão pré-definido ou aleatório.
           Se pattern for 'Random' ou se não houver padrão definido, o grid é populado aleatoriamente."""
        self.grid = np.zeros((N, N), dtype=int)
        pattern_coords = None
        if (self.current_automaton in patterns and
            category in patterns[self.current_automaton] and
            pattern in patterns[self.current_automaton][category]):
            pattern_coords = patterns[self.current_automaton][category][pattern]
        if pattern_coords is not None and pattern != "Random":
            for (i, j) in pattern_coords:
                if 0 <= i < N and 0 <= j < N:
                    self.grid[i, j] = 1
        else:
            self.grid = np.random.choice([0, 1], (N, N), p=[0.8, 0.2])

    def save_state(self):
        """Salva o estado atual do grid em um arquivo .npy."""
        file_path = filedialog.asksaveasfilename(defaultextension=".npy")
        if file_path:
            import numpy as np
            np.save(file_path, self.grid)

    def load_state(self):
        """Carrega um estado salvo do grid a partir de um arquivo .npy."""
        file_path = filedialog.askopenfilename(defaultextension=".npy")
        if file_path:
            import numpy as np
            self.grid = np.load(file_path)

    def export_gif(self):
        """Exporta os frames capturados durante a simulação para um GIF animado."""
        file_path = filedialog.asksaveasfilename(defaultextension=".gif")
        if file_path and self.gif_frames:
            imageio.mimsave(file_path, self.gif_frames, duration=self.speed / 1000)
            self.gif_frames = []

    def capture_frame(self):
        """Captura o frame atual do grid e o adiciona à lista de frames para o GIF."""
        img = Image.new("RGB", (N * CELL_SIZE, N * CELL_SIZE), "white")
        pixels = img.load()
        for i in range(N):
            for j in range(N):
                color = self.colors.get(self.grid[i, j], "white")
                if isinstance(color, str):
                    color = self._hex_to_rgb(color)
                for dx in range(CELL_SIZE):
                    for dy in range(CELL_SIZE):
                        pixels[j * CELL_SIZE + dx, i * CELL_SIZE + dy] = color
        self.gif_frames.append(np.array(img))

    def _hex_to_rgb(self, hex_color):
        """Converte uma cor hexadecimal para uma tupla RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
