import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import os
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import textwrap
from IPython.display import Markdown

os.environ["GOOGLE_API_KEY"] = "AIzaSyCrqjgYm-y7DTjncCDMR0TpYHUc7iVB8NE"
client = genai.Client()
MODEL_ID = "gemini-2.0-flash"

def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])
    final_response = ""
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text
                    final_response += "\n"
    return final_response

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Personagens")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.generator_frame = ttk.Frame(self)
        self.favorites_frame = ttk.Frame(self)

        self.generator_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.favorites_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.generator_frame.columnconfigure(0, weight=1)
        self.generator_frame.rowconfigure(0, weight=0)
        self.generator_frame.rowconfigure(1, weight=0)
        self.generator_frame.rowconfigure(2, weight=0)
        self.generator_frame.rowconfigure(3, weight=0)
        self.generator_frame.rowconfigure(4, weight=0)
        self.generator_frame.rowconfigure(5, weight=0)
        self.generator_frame.rowconfigure(6, weight=0)
        self.generator_frame.rowconfigure(7, weight=0)

        self.favorites_frame.columnconfigure(0, weight=1)
        self.favorites_frame.rowconfigure(0, weight=1)

        self.navigation_bar = ttk.Frame(self)
        self.navigation_bar.grid(row=1, column=0, sticky="ew")
        self.navigation_bar.columnconfigure(0, weight=1)

        ttk.Button(self.navigation_bar, text="Gerar Nome", command=self.show_generator).pack(side="left", padx=5, pady=5, expand=True)
        ttk.Button(self.navigation_bar, text="Favoritos", command=self.show_favorites).pack(side="left", padx=5, pady=5, expand=True)

        # --- Listas de Classes e Raças ---
        self.class_list = ["Barbarian", "Bard", "Cleric", "Druid", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Warrior", "Wizard"]
        self.race_list = ["Dragonborn", "Dwarf", "Elf", "Gnome", "Half-elf", "Half-orc", "Halfling", "Human", "Tiefling"]
        self.class_images = [None] * len(self.class_list) # Para armazenar as imagens (placeholders)
        self.race_images = [None] * len(self.race_list)   # Para armazenar as imagens (placeholders)

        self.selected_class_index = 0
        self.selected_race_index = 0

        # --- Seletor de Classe ---
        ttk.Label(self.generator_frame, text="Classe:").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        class_selector_frame = ttk.Frame(self.generator_frame)
        class_selector_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        class_selector_frame.columnconfigure(1, weight=1) # Centralizar a imagem

        self.prev_class_button = ttk.Button(class_selector_frame, text="<", command=self.previous_class)
        self.prev_class_button.grid(row=0, column=0, padx=5)

        self.class_image_label = ttk.Label(class_selector_frame)
        self.class_image_label.grid(row=0, column=1, pady=5)

        self.next_class_button = ttk.Button(class_selector_frame, text=">", command=self.next_class)
        self.next_class_button.grid(row=0, column=2, padx=5)

        self.current_class_label = ttk.Label(class_selector_frame, text=self.class_list[self.selected_class_index])
        self.current_class_label.grid(row=1, column=0, columnspan=3) # Centralizar o texto abaixo

        self.update_class_image() # Mostrar o placeholder inicial

        # --- Seletor de Raça ---
        ttk.Label(self.generator_frame, text="Raça:").grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        race_selector_frame = ttk.Frame(self.generator_frame)
        race_selector_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        race_selector_frame.columnconfigure(1, weight=1) # Centralizar a imagem

        self.prev_race_button = ttk.Button(race_selector_frame, text="<", command=self.previous_race)
        self.prev_race_button.grid(row=0, column=0, padx=5)

        self.race_image_label = ttk.Label(race_selector_frame)
        self.race_image_label.grid(row=0, column=1, pady=5)

        self.next_race_button = ttk.Button(race_selector_frame, text=">", command=self.next_race)
        self.next_race_button.grid(row=0, column=2, padx=5)

        self.current_race_label = ttk.Label(race_selector_frame, text=self.race_list[self.selected_race_index])
        self.current_race_label.grid(row=1, column=0, columnspan=3) # Centralizar o texto abaixo

        self.update_race_image() # Mostrar o placeholder inicial

        # --- Seletor de Gênero ---
        ttk.Label(self.generator_frame, text="Gênero:").grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        gender_frame = ttk.Frame(self.generator_frame)
        gender_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        gender_frame.columnconfigure(0, weight=1)

        self.selected_gender = tk.StringVar(value="neutral")
        ttk.Radiobutton(gender_frame, text="Feminino", variable=self.selected_gender, value="female").pack(side="left", padx=5, pady=5, expand=True)
        ttk.Radiobutton(gender_frame, text="Neutro", variable=self.selected_gender, value="neutral").pack(side="left", padx=5, pady=5, expand=True)
        ttk.Radiobutton(gender_frame, text="Masculino", variable=self.selected_gender, value="male").pack(side="left", padx=5, pady=5, expand=True)

        ttk.Button(self.generator_frame, text="Gerar", command=self.generate_name).grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        self.generated_name = tk.StringVar(value="Nome Gerado:")
        self.generated_name_label = ttk.Label(self.generator_frame, textvariable=self.generated_name)
        self.generated_name_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        # --- Conteúdo do Frame de Favoritos ---
        ttk.Label(self.favorites_frame, text="Lista de Favoritos").pack(expand=True, fill="both", padx=20, pady=20)

        self.show_generator()

    def show_generator(self):
        self.favorites_frame.grid_forget()
        self.generator_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    def show_favorites(self):
        self.generator_frame.grid_forget()
        self.favorites_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    def update_class_image(self):
        # Criar um placeholder colorido (retângulo)
        img_width = 50
        img_height = 50
        img = Image.new("RGB", (img_width, img_height), color=self.get_placeholder_color(self.selected_class_index))
        # Simular um círculo (opcional, mas um pouco mais complexo com Pillow)
        mask = Image.new('L', (img_width, img_height), 0)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img_width, img_height), fill=255)
        img.putalpha(mask)

        self.class_photo = ImageTk.PhotoImage(img)
        self.class_image_label.config(image=self.class_photo)

    def update_race_image(self):
        # Criar outro placeholder colorido
        img_width = 50
        img_height = 50
        img = Image.new("RGB", (img_width, img_height), color=self.get_placeholder_color(self.selected_race_index + len(self.class_list))) # Cores diferentes
        mask = Image.new('L', (img_width, img_height), 0)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img_width, img_height), fill=255)
        img.putalpha(mask)

        self.race_photo = ImageTk.PhotoImage(img)
        self.race_image_label.config(image=self.race_photo)

    def get_placeholder_color(self, index):
        colors = ["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta", "lime", "teal", "navy", "olive", "maroon", "silver"]
        return colors[index % len(colors)]

    def previous_class(self):
        if self.selected_class_index > 0:
            self.selected_class_index -= 1
            self.current_class_label.config(text=self.class_list[self.selected_class_index])
            self.update_class_image()

    def next_class(self):
        if self.selected_class_index < len(self.class_list) - 1:
            self.selected_class_index += 1
            self.current_class_label.config(text=self.class_list[self.selected_class_index])
            self.update_class_image()

    def previous_race(self):
        if self.selected_race_index > 0:
            self.selected_race_index -= 1
            self.current_race_label.config(text=self.race_list[self.selected_race_index])
            self.update_race_image()

    def next_race(self):
        if self.selected_race_index < len(self.race_list) - 1:
            self.selected_race_index += 1
            self.current_race_label.config(text=self.race_list[self.selected_race_index])
            self.update_race_image()

    def generate_name(self):
        character_class = self.class_list[self.selected_class_index]
        race = self.race_list[self.selected_race_index]
        gender = self.selected_gender.get()

        if character_class and race and gender:
            prompt = f"Gere um nome para um personagem da classe {character_class}, raça {race} e gênero {gender} em um cenário de fantasia."
            generated_name_from_ai = self.call_name_generation_agent(prompt)
            self.generated_name.set(f"Nome Gerado: {generated_name_from_ai}")
        else:
            self.generated_name.set("Por favor, preencha todos os campos.")

    def call_name_generation_agent(self, prompt: str) -> str:
        name_generator_agent = Agent(
            name="name_generator",
            model=MODEL_ID,
            description="Agente para gerar nomes de personagens de fantasia.",
            instruction="Você é um especialista em gerar nomes criativos e adequados para personagens de RPG de fantasia. Considere a classe, a raça e o gênero fornecidos para criar um nome interessante e adequado ao contexto.",
        )
        return call_agent(name_generator_agent, prompt)

if __name__ == "__main__":
    app = App()
    app.mainloop()