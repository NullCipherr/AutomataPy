# view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from config import N, CELL_SIZE, automata_config
from patterns import patterns

class CellularAutomatonUI:
    def __init__(self, master, model):
        self.master = master
        self.model = model
        self.running = False

        self.master.title("Autômatos Celulares")
        self.master.geometry("800x600")
        
        # Carregar ícones
        self.icon_zoom = tk.PhotoImage(file="icons/zoom.png")
        self.icon_start = tk.PhotoImage(file="icons/start.png")
        self.icon_step = tk.PhotoImage(file="icons/step.png")
        self.icon_pause = tk.PhotoImage(file="icons/pause.png")
        self.icon_reset = tk.PhotoImage(file="icons/restart.png")
        
        # Configura as linhas da janela principal:
        # Linha 0 (canvas) expande; linha 1 (controles) tem altura fixa.
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=0)
        self.master.columnconfigure(0, weight=1)

        self.setup_styles()
        self.init_ui()
        self.redraw()

    def setup_styles(self):
        """Configura os estilos do ttk para botões e demais widgets."""
        style = ttk.Style()
        style.theme_use('clam')

        # Estilo para botões modernos:
        style.configure(
            'Modern.TButton',
            font=('Helvetica', 10, 'bold'),
            foreground='#ffffff',
            background='#3498db',
            borderwidth=0,
            focusthickness=3,
            focuscolor='none',
            padding=6
        )
        style.map(
            'Modern.TButton',
            background=[('active', '#2980b9'), ('disabled', '#bdc3c7')]
        )

        # Estilo para OptionMenu (utilizando o ttk.Menubutton)
        style.configure(
            'Modern.TMenubutton',
            font=('Helvetica', 10),
            foreground='#333333',
            background='#ecf0f1',
            padding=4
        )

    def init_ui(self):
        self.create_menu()
        self.create_canvas()
        self.create_controls()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salvar", command=self.wrap_command(self.model.save_state))
        file_menu.add_command(label="Carregar", command=self.wrap_command(self.load_and_redraw))
        file_menu.add_separator()
        file_menu.add_command(label="Exportar GIF", command=self.wrap_command(self.model.export_gif))
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.master.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        # Menu Autômatos (a seleção ocorre somente aqui)
        automata_menu = tk.Menu(menubar, tearoff=0)
        for automaton in automata_config.keys():
            automata_menu.add_command(
                label=automaton,
                command=self.wrap_command(lambda a=automaton: self.change_automaton(a))
            )
        menubar.add_cascade(label="Autômatos", menu=automata_menu)

        # Menu Exibir com controles de zoom e velocidade
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom", image=self.icon_zoom, compound="left", command=self.wrap_command(self.adjust_zoom))
        view_menu.add_command(label="Velocidade", command=self.wrap_command(self.adjust_speed))
        menubar.add_cascade(label="Exibir", menu=view_menu)

        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Como Usar", command=self.show_help)
        help_menu.add_command(label="Créditos", command=self.show_credits)
        menubar.add_cascade(label="Ajuda", menu=help_menu)

    def create_canvas(self):
        # Cria um frame para o canvas e configura seu grid para que ele expanda
        self.canvas_frame = ttk.Frame(self.master)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.canvas_frame.rowconfigure(0, weight=1)
        self.canvas_frame.columnconfigure(0, weight=1)

        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="white",
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)

        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.toggle_cell)

    def create_controls(self):
        self.control_frame = ttk.Frame(self.master)
        self.control_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        self.category_var = tk.StringVar()
        self.category_menu = ttk.OptionMenu(self.control_frame, self.category_var, "")
        self.category_menu.pack(side=tk.LEFT, padx=5)
        self.update_category_menu()

        self.pattern_var = tk.StringVar()
        self.pattern_menu = ttk.OptionMenu(self.control_frame, self.pattern_var, "")
        self.pattern_menu.pack(side=tk.LEFT, padx=5)
        self.update_pattern_menu()

        self.btn_start_pause = ttk.Button(
            self.control_frame, image=self.icon_start, command=self.toggle_simulation, style='Icon.TButton')
        self.btn_start_pause.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.control_frame, image=self.icon_step, command=self.step_and_redraw, style='Icon.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.control_frame, image=self.icon_reset, command=self.reset_and_redraw, style='Icon.TButton'
        ).pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(self.control_frame, text="Geração: 0")
        self.status_label.pack(side=tk.RIGHT, padx=5)

    def wrap_command(self, cmd):
        """
        Executa o comando e transfere o foco para o canvas, evitando que o botão fique visualmente pressionado.
        """
        def wrapped(*args, **kwargs):
            cmd(*args, **kwargs)
            self.canvas.focus_set()
        return wrapped

    def update_category_menu(self):
        if self.model.current_automaton in patterns:
            self.category_options = list(patterns[self.model.current_automaton].keys())
        else:
            self.category_options = []
        if self.category_options:
            self.category_var.set(self.category_options[0])
        else:
            self.category_var.set("")
        menu = self.category_menu["menu"]
        menu.delete(0, "end")
        for option in self.category_options:
            menu.add_command(
                label=option,
                command=self.wrap_command(lambda value=option: self.change_category(value))
            )

    def update_pattern_menu(self):
        current_category = self.category_var.get()
        if (self.model.current_automaton in patterns and 
            current_category in patterns[self.model.current_automaton]):
            self.pattern_options = list(patterns[self.model.current_automaton][current_category].keys())
        else:
            self.pattern_options = []
        if self.pattern_options:
            self.pattern_var.set(self.pattern_options[0])
        else:
            self.pattern_var.set("")
        menu = self.pattern_menu["menu"]
        menu.delete(0, "end")
        for option in self.pattern_options:
            menu.add_command(
                label=option,
                command=self.wrap_command(lambda value=option: self.change_pattern(value))
            )

    def change_category(self, value):
        self.category_var.set(value)
        self.update_pattern_menu()
        self.model.reset_grid(self.category_var.get(), self.pattern_var.get())
        self.redraw()

    def change_pattern(self, value):
        self.pattern_var.set(value)
        self.model.reset_grid(self.category_var.get(), self.pattern_var.get())
        self.redraw()

    def change_automaton(self, selected):
        # Método chamado somente a partir do menu superior.
        self.model.current_automaton = selected
        self.model.setup_automaton()
        self.update_category_menu()
        self.update_pattern_menu()
        self.redraw()

    def adjust_zoom(self):
        """Abre uma caixa de diálogo para o usuário ajustar o zoom."""
        novo_zoom = simpledialog.askfloat("Ajustar Zoom",
                                          "Informe o valor do zoom (ex.: 1 para 100%):",
                                          initialvalue=self.model.zoom,
                                          minvalue=0.1,
                                          maxvalue=10)
        if novo_zoom is not None:
            self.model.zoom = novo_zoom
            self.redraw()

    def adjust_speed(self):
        """Abre uma caixa de diálogo para o usuário ajustar a velocidade (em milissegundos)."""
        nova_velocidade = simpledialog.askinteger("Ajustar Velocidade",
                                                  "Informe a velocidade em milissegundos:",
                                                  initialvalue=self.model.speed,
                                                  minvalue=10,
                                                  maxvalue=2000)
        if nova_velocidade is not None:
            self.model.speed = nova_velocidade

    def show_help(self):
        """Exibe uma janela com instruções de uso."""
        help_text = (
            "Como Usar:\n\n"
            "- Utilize o menu 'Autômatos' para escolher o autômato desejado.\n"
            "- Selecione a categoria e o padrão na área inferior.\n"
            "- Use os botões Iniciar/Pausar, Avançar e Reiniciar para controlar a simulação.\n"
            "- Ajuste o zoom e a velocidade pelo menu 'Exibir'.\n"
            "- Clique no grid para alternar o estado das células manualmente."
        )
        messagebox.showinfo("Como Usar", help_text)

    def show_credits(self):
        """Exibe uma janela com informações sobre os créditos do projeto."""
        credits_text = (
            "Projeto Autômatos Celulares\n"
            "Desenvolvido por: Andrei Costa\n"
            "Versão: 0.1a\n\n"
            "Obrigado por utilizar o sistema!"
        )
        messagebox.showinfo("Créditos", credits_text)

    def toggle_simulation(self):
        self.running = not self.running
        if self.running:
            self.run_simulation()

    def run_simulation(self):
        if self.running:
            self.model.step()
            self.redraw()
            self.master.after(self.model.speed, self.run_simulation)

    def step_and_redraw(self):
        self.model.step()
        self.redraw()

    def reset_and_redraw(self):
        # Reinicia o grid utilizando o padrão atualmente selecionado
        self.model.reset_grid(self.category_var.get(), self.pattern_var.get())
        # Reseta a contagem de gerações para zero
        self.model.generation = 0
        self.redraw()

    def load_and_redraw(self):
        self.model.load_state()
        self.redraw()

    def toggle_cell(self, event):
        cell_size = CELL_SIZE * self.model.zoom
        x = event.x // cell_size
        y = event.y // cell_size
        if 0 <= x < N and 0 <= y < N:
            self.model.grid[y, x] = (self.model.grid[y, x] + 1) % self.model.states
            self.redraw()

    def on_resize(self, event):
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        cell_size = CELL_SIZE * self.model.zoom
        for i in range(N):
            for j in range(N):
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                color = self.model.colors.get(self.model.grid[i, j], "white")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
        # Atualiza o status (exibe a geração atual)
        self.status_label.config(text=f"Geração: {self.model.generation}")