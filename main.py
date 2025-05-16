import tkinter as tk
from tkinter import ttk
import random
import os
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types  # Para criar conteúdos (Content e Part)
import textwrap  # Para formatar melhor a saída de texto
# from IPython.display import Markdown  # Para exibir texto formatado (pode ser útil para debug)

# Configura a API Key do Google Gemini
# Certifique-se de que a variável de ambiente GOOGLE_API_KEY esteja definida
os.environ["GOOGLE_API_KEY"] = "AIzaSyCrqjgYm-y7DTjncCDMR0TpYHUc7iVB8NE"  # Substitua pela sua chave real ou configure a variável de ambiente

# Configura o cliente da SDK do Gemini
client = genai.Client()

MODEL_ID = "gemini-2.0-flash"

# Função auxiliar que envia uma mensagem para um agente via Runner e retorna a resposta final
def call_agent(agent: Agent, message_text: str) -> str:
    # Cria um serviço de sessão em memória
    session_service = InMemorySessionService()
    # Cria uma nova sessão
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    # Cria um Runner para o agente
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    # Cria o conteúdo da mensagem de entrada
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    # Itera assincronamente pelos eventos retornados durante a execução do agente
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text
                    final_response += "\n"
    return final_response

# Função auxiliar para exibir texto formatado em Markdown (opcional, para debug)
def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Personagens")

        self.generator_frame = ttk.Frame(self)
        self.favorites_frame = ttk.Frame(self)

        self.generator_frame.grid(row=0, column=0, sticky="nsew")
        self.favorites_frame.grid(row=0, column=0, sticky="nsew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.navigation_bar = ttk.Frame(self)
        self.navigation_bar.grid(row=1, column=0, sticky="ew")

        ttk.Button(self.navigation_bar, text="Gerar Nome", command=self.show_generator).pack(side="left", padx=5, pady=5, expand=True)
        ttk.Button(self.navigation_bar, text="Favoritos", command=self.show_favorites).pack(side="left", padx=5, pady=5, expand=True)

        # --- Conteúdo do Frame de Geração de Nomes ---
        ttk.Label(self.generator_frame, text="Classe:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.class_entry = ttk.Entry(self.generator_frame)
        self.class_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.generator_frame, text="Raça:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.race_entry = ttk.Entry(self.generator_frame)
        self.race_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.generator_frame, text="Gênero:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        gender_frame = ttk.Frame(self.generator_frame)
        gender_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.selected_gender = tk.StringVar(value="neutral")
        ttk.Radiobutton(gender_frame, text="Feminino", variable=self.selected_gender, value="female").pack(side="left", padx=5, pady=5, expand=True)
        ttk.Radiobutton(gender_frame, text="Neutro", variable=self.selected_gender, value="neutral").pack(side="left", padx=5, pady=5, expand=True)
        ttk.Radiobutton(gender_frame, text="Masculino", variable=self.selected_gender, value="male").pack(side="left", padx=5, pady=5, expand=True)

        ttk.Button(self.generator_frame, text="Gerar", command=self.generate_name).grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        self.generated_name = tk.StringVar(value="Nome Gerado:")
        self.generated_name_label = ttk.Label(self.generator_frame, textvariable=self.generated_name)
        self.generated_name_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # --- Conteúdo do Frame de Favoritos (por enquanto vazio) ---
        ttk.Label(self.favorites_frame, text="Lista de Favoritos").pack(padx=10, pady=10)

        self.show_generator()

    def show_generator(self):
        self.favorites_frame.grid_forget()
        self.generator_frame.grid(row=0, column=0, sticky="nsew")

    def show_favorites(self):
        self.generator_frame.grid_forget()
        self.favorites_frame.grid(row=0, column=0, sticky="nsew")

    def generate_name(self):
        character_class = self.class_entry.get()
        race = self.race_entry.get()
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