import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import random
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import textwrap
from IPython.display import Markdown

os.environ["GOOGLE_API_KEY"] = "AIzaSyCrqjgYm-y7DTjncCDMR0TpYHUc7iVB8NE"  # Substitua pela sua chave real
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
        self.geometry("1200x1000")
        self.resizable(False, False)

        try:
            self.background_image = Image.open("background.png")
            self.background_photo = ImageTk.PhotoImage(self.background_image)
        except FileNotFoundError:
            print("Erro: A imagem 'background.png' não foi encontrada.")
            self.background_photo = None

        self.background_canvas = tk.Canvas(self, width=1200, height=1000, highlightthickness=0)
        self.background_canvas.pack(fill="both", expand=True)

        if self.background_photo:
            self.background_canvas.create_image(0, 0, image=self.background_photo, anchor="nw", tags="bg_img")
        else:
            self.background_canvas.config(bg="#333333")

        # --- Estilos ttk ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#000000")
        self.style.configure("TLabel", background="#000000", foreground='white')
        self.style.configure("TRadiobutton", background='#000000', foreground='white')
        self.style.configure("TButton", foreground='black', background='#cccccc', padding=(10, 5), relief='groove')

        # --- Frames das telas ---
        self.home_frame = ttk.Frame(self.background_canvas)
        self.generator_frame = ttk.Frame(self.background_canvas)
        self.item_help_frame = ttk.Frame(self.background_canvas)
        self.master_chat_frame = ttk.Frame(self.background_canvas)
        self.dice_roll_frame = ttk.Frame(self.background_canvas)

        # --- Posicionamento inicial ---
        self.home_frame.place(relx=0.5, rely=0.5, anchor="center")

        # --- Conteúdo da Home ---
        ttk.Label(self.home_frame, text="Bem-vindo(a)!", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Button(self.home_frame, text="Gerador de Nome", command=self.show_generator).pack(pady=5, padx=20, fill="x")
        ttk.Button(self.home_frame, text="Ajuda com Equipamentos", command=self.show_item_help).pack(pady=5, padx=20, fill="x")
        ttk.Button(self.home_frame, text="Converse com o Mestre", command=self.show_master_chat).pack(pady=5, padx=20, fill="x")
        ttk.Button(self.home_frame, text="Rodar Dados", command=self.show_dice_roll).pack(pady=5, padx=20, fill="x")

        # --- Conteúdo do Gerador de Nome ---
        self.generator_frame.columnconfigure(0, weight=1)
        self.generator_frame.columnconfigure(1, weight=1)
        self.generator_frame.rowconfigure(9, weight=1)
        ttk.Button(self.generator_frame, text="Voltar", command=self.show_home).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        ttk.Label(self.generator_frame, text="Gerador de Nome", font=("Arial", 14)).grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        self.class_list = ["Bárbaro", "Bardo", "Clérigo", "Druida", "Monge", "Paladino", 
                      "Patrulheiro", "Ladino", "Feiticeiro", "Bruxo", "Guerreiro", "Mago"]
        self.race_list = ["Dracônico", "Anão", "Elfo", "Gnomo", "Meio-elfo", 
                     "Meio-orc", "Pequenino", "Humano", "Tiefling"]
        


        self.race_images = {
            "Dracônico": "dragonborn.png",
            "Anão": "dwarf.png",
            "Elfo": "elf.png",
            "Gnomo": "gnome.png",
            "Meio-elfo": "halfElf.png",
            "Meio-orc": "halfOrc.png",
            "Pequenino": "halfling.png",
            "Humano": "human.png",
            "Tiefling": "tiefling.png"
}
        self.class_images = {
            "Bárbaro": "barbarian.png",
            "Bardo": "bard.png",
            "Clérigo": "cleric.png",
            "Druida": "druid.png",
            "Monge": "monk.png",
            "Paladino": "paladin.png",
            "Patrulheiro": "ranger.png",
            "Ladino": "rogue.png",
            "Feiticeiro": "sorcerer.png",
            "Bruxo": "warlock.png",
            "Guerreiro": "warrior.png",
            "Mago": "wizard.png"
}
        
        self.selected_class_index = 0
        self.selected_race_index = 0
        ttk.Label(self.generator_frame, text="Classe:").grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        class_selector_frame = ttk.Frame(self.generator_frame)
        class_selector_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        class_selector_frame.columnconfigure(0, weight=1)
        class_selector_frame.columnconfigure(1, weight=3)
        class_selector_frame.columnconfigure(2, weight=1)
        self.prev_class_button = ttk.Button(class_selector_frame, text="<", command=self.previous_class)
        self.prev_class_button.grid(row=0, column=0, padx=5, sticky="w")
        self.class_image_label = ttk.Label(class_selector_frame)
        self.class_image_label.grid(row=0, column=1, pady=5)
        self.next_class_button = ttk.Button(class_selector_frame, text=">", command=self.next_class)
        self.next_class_button.grid(row=0, column=2, padx=5, sticky="w")
        self.current_class_label = ttk.Label(class_selector_frame, text=self.class_list[self.selected_class_index])
        self.current_class_label.grid(row=1, column=0, columnspan=3, pady=5)
        self.update_class_image()
        ttk.Label(self.generator_frame, text="Raça:").grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        race_selector_frame = ttk.Frame(self.generator_frame)
        race_selector_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        race_selector_frame.columnconfigure(0, weight=1)
        race_selector_frame.columnconfigure(1, weight=3)
        race_selector_frame.columnconfigure(2, weight=1)
        self.prev_race_button = ttk.Button(race_selector_frame, text="<", command=self.previous_race)
        self.prev_race_button.grid(row=0, column=0, padx=5, sticky="w")
        self.race_image_label = ttk.Label(race_selector_frame)
        self.race_image_label.grid(row=0, column=1, pady=5)
        self.next_race_button = ttk.Button(race_selector_frame, text=">", command=self.next_race)
        self.next_race_button.grid(row=0, column=2, padx=5, sticky="w")
        self.current_race_label = ttk.Label(race_selector_frame, text=self.race_list[self.selected_race_index])
        self.current_race_label.grid(row=1, column=0, columnspan=3, pady=5)
        self.update_race_image()
        ttk.Label(self.generator_frame, text="Gênero:").grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        gender_frame = ttk.Frame(self.generator_frame)
        gender_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        gender_frame.columnconfigure(0, weight=1)
        self.selected_gender = tk.StringVar(value="neutral")
        ttk.Radiobutton(gender_frame, text="Feminino", variable=self.selected_gender, value="female", style="TRadiobutton").pack(side="left", padx=5, pady=5, expand=True)
        ttk.Radiobutton(gender_frame, text="Neutro", variable=self.selected_gender, value="neutral", style="TRadiobutton").pack(side="left", padx=5, pady=5, expand=True)
        ttk.Radiobutton(gender_frame, text="Masculino", variable=self.selected_gender, value="male", style="TRadiobutton").pack(side="left", padx=5, pady=5, expand=True)
        ttk.Button(self.generator_frame, text="Gerar", command=self.generate_name).grid(row=8, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        self.generated_name = tk.StringVar(value="✨ Seu nome de personagem aparecerá aqui ✨")
        self.generated_name_label = ttk.Label(
            self.generator_frame, 
            textvariable=self.generated_name,
            font=("Arial", 16, "bold")  # Fonte maior e em negrito
        )
        self.generated_name_label.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # --- Conteúdo da Ajuda com Itens ---
        # O conteúdo será adicionado na função show_item_help

        # --- Conteúdo do Converse com o Mestre ---
        # O conteúdo será adicionado na função show_master_chat

        # --- Conteúdo do Rodar Dados ---
        # O conteúdo será adicionado na função show_dice_roll

        self.show_home()

    def show_home(self):
        self.generator_frame.place_forget()
        self.item_help_frame.place_forget()
        self.master_chat_frame.place_forget()
        self.dice_roll_frame.place_forget()
        self.home_frame.place(relx=0.5, rely=0.5, anchor="center")

    def show_generator(self):
        self.home_frame.place_forget()
        self.item_help_frame.place_forget()
        self.master_chat_frame.place_forget()
        self.dice_roll_frame.place_forget()
        self.generator_frame.place(relx=0.5, rely=0.5, anchor="center")

    def show_item_help(self):
        self.home_frame.place_forget()
        self.generator_frame.place_forget()
        self.master_chat_frame.place_forget()
        self.dice_roll_frame.place_forget()
    
        # Configuração do frame principal
        self.item_help_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.item_help_frame.columnconfigure(0, weight=1)
        self.item_help_frame.rowconfigure(2, weight=1)  # Espaço para o chat

        # Título centralizado grande
        ttk.Label(
            self.item_help_frame, 
            text="Ajuda com Equipamentos", 
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="ew")

        # Botão Voltar alinhado à esquerda
        ttk.Button(
            self.item_help_frame, 
            text="Voltar", 
            command=self.show_home
        ).grid(row=1, column=0, sticky="nw", padx=10, pady=5)

        # Imagem de Itens alinhada à direita
        try:
            itens_image = Image.open("itens.png")
            itens_image = itens_image.resize((150, 150))
            itens_photo = ImageTk.PhotoImage(itens_image)
            itens_label = ttk.Label(self.item_help_frame, image=itens_photo)
            itens_label.image = itens_photo
            itens_label.grid(row=1, column=1, padx=10, pady=5, sticky="ne")
        except FileNotFoundError:
            ttk.Label(
                self.item_help_frame, 
                text="Ícone de Itens", 
                font=("Arial", 10)
            ).grid(row=1, column=1, padx=10, pady=5, sticky="ne")

        # Área de Chat (abaixo do título e botões)
        self.item_chat_area = tk.Text(
            self.item_help_frame, 
            state='disabled', 
            wrap='word',
            font=("Arial", 11),
            height=15,
            width=50
        )
        self.item_chat_area.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Entrada de Texto
        self.item_input_entry = ttk.Entry(
            self.item_help_frame,
            font=("Arial", 11)
        )
        self.item_input_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Botão Enviar
        send_button = ttk.Button(
            self.item_help_frame, 
            text="Enviar", 
            command=self.send_item_message
        )
        send_button.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    def send_item_message(self, event=None):
        user_message = self.item_input_entry.get()
        self.item_input_entry.delete(0, tk.END)
        if user_message:
            self.display_item_message("Você:", user_message)
            self.get_item_response(user_message) # Simulação da resposta sobre itens

    def display_item_message(self, sender, message):
        self.item_chat_area.config(state='normal')
        self.item_chat_area.insert(tk.END, f"{sender} {message}\n")
        self.item_chat_area.config(state='disabled')
        self.item_chat_area.see(tk.END) # Autoscroll para a última mensagem

    def get_item_response(self, user_message):
        # Agente 1 - Analista de Necessidades
        needs_analyzer = Agent(
            name="item_needs_analyzer",
            model=MODEL_ID,
            description="Analisa as necessidades do jogador em relação a itens",
            instruction="""Você é um especialista em análise de necessidades de RPG. Sua tarefa é:
            1. Identificar o tipo de personagem (classe, raça, nível)
            2. Determinar o cenário atual (combate, exploração, social)
            3. Extrair os objetivos do jogador
            4. Retornar um resumo formatado:
            [Classe]: <classe>
            [Nível]: <nível>
            [Situação]: <situação>
            [Objetivo]: <objetivo>"""
        )
    
        # Agente 2 - Especialista em Builds
        build_expert = Agent(
            name="item_build_expert",
            model=MODEL_ID,
            description="Recomenda builds de equipamentos para personagens",
            instruction="""Você é um especialista em builds de RPG. Com base na análise:
            1. Recomende os melhores itens para a situação
            2. Considere sinergias entre itens
            3. Sugira combinações para diferentes orçamentos
            4. Classifique como:
            - Essencial: Itens indispensáveis
            - Recomendado: Boas opções
            - Situacional: Casos específicos
            5. Limite a 3-5 itens por categoria"""
        )
    
        # Agente 3 - Negociador de Itens
        item_negotiator = Agent(
            name="item_negotiator",
            model=MODEL_ID,
            description="Ensina como obter os itens recomendados",
            instruction="""Você é um mestre negociador de itens. Para cada item recomendado:
            1. Indique onde encontrar (lojas, saque, crafting)
            2. Estime o valor aproximado
            3. Sugira trocas ou negociações
            4. Aponte alternativas mais acessíveis
            5. Inclua dicas para conseguir descontos"""
        )

        # Primeiro analisamos as necessidades
        analysis = call_agent(needs_analyzer, user_message)
    
        # Obter recomendações de build
        recommendations = call_agent(build_expert, f"Análise do personagem:\n{analysis}\nPergunta original: {user_message}")
    
        # Obter informações de obtenção
        acquisition_info = call_agent(item_negotiator, f"Itens recomendados:\n{recommendations}\nContexto:\n{analysis}")

        # Formatamos a resposta completa
        full_response = (
        f"🔍 Análise das suas necessidades:\n{analysis}\n\n"
        f"🛡️ Recomendações de Equipamentos:\n{recommendations}\n\n"
        f"💰 Como obter esses itens:\n{acquisition_info}"
        )

        self.after(1500, self.display_item_message, "Especialista em Itens:", full_response)

    def show_master_chat(self):
        self.home_frame.place_forget()
        self.generator_frame.place_forget()
        self.item_help_frame.place_forget()
        self.dice_roll_frame.place_forget()
    
        # Configuração do frame principal
        self.master_chat_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.master_chat_frame.columnconfigure(0, weight=1)
        self.master_chat_frame.rowconfigure(2, weight=1)  # Espaço para o chat

        # Título centralizado grande
        ttk.Label(
            self.master_chat_frame, 
            text="Converse com o Mestre", 
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="ew")

        # Botão Voltar alinhado à esquerda
        ttk.Button(
            self.master_chat_frame, 
            text="Voltar", 
            command=self.show_home
        ).grid(row=1, column=0, sticky="nw", padx=10, pady=5)

        # Imagem do Mestre alinhada à direita
        try:
            master_image = Image.open("mestre.png")
            master_image = master_image.resize((150, 150))
            master_photo = ImageTk.PhotoImage(master_image)
            master_label = ttk.Label(self.master_chat_frame, image=master_photo)
            master_label.image = master_photo
            master_label.grid(row=1, column=1, padx=10, pady=5, sticky="ne")
        except FileNotFoundError:
            ttk.Label(
                self.master_chat_frame, 
                text="Ícone do Mestre", 
                font=("Arial", 10)
            ).grid(row=1, column=1, padx=10, pady=5, sticky="ne")

        # Área de Chat (abaixo do título e botões)
        self.chat_area = tk.Text(
            self.master_chat_frame, 
            state='disabled', 
            wrap='word',
            font=("Arial", 11),
            height=15,
            width=50
        )
        self.chat_area.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Entrada de Texto
        self.input_entry = ttk.Entry(
            self.master_chat_frame,
            font=("Arial", 11)
        )      
        self.input_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Botão Enviar
        send_button = ttk.Button(
            self.master_chat_frame, 
            text="Enviar", 
            command=self.send_message
        )
        send_button.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    def send_message(self, event=None):
        user_message = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        if user_message:
            self.display_message("Você:", user_message)
            self.get_master_response(user_message) # Simulação da resposta do mestre

    def display_message(self, sender, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{sender} {message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END) # Autoscroll para a última mensagem

    def get_master_response(self, user_message):
        # Agente 1 - Analista de Contexto
        context_analyzer = Agent(
            name="context_analyzer",
            model=MODEL_ID,
            description="Analisa o contexto da pergunta sobre RPG",
            instruction="""Você é um analista especializado em RPG. Sua tarefa é:
            1. Identificar o tema principal da pergunta
            2. Determinar se é sobre regras, lore, construção de personagem ou outro
            3. Extrair informações relevantes como classe, raça, nível do personagem
            4. Retornar um resumo conciso do contexto"""
        )
    
        # Agente 2 - Especialista em Regras
        rules_expert = Agent(
            name="rules_expert",
            model=MODEL_ID,
            description="Responde dúvidas sobre regras oficiais de RPG",
            instruction="""Você é um mestre de RPG com 20 anos de experiência. Responda:
            1. Baseado apenas nas regras oficiais do sistema
            2. Seja preciso com páginas e referências quando possível
            3. Para situações ambíguas, sugira interpretações alternativas
            4. Mantenha a resposta curta e direta"""
        )
    
        # Agente 3 - Criador de Histórias
        storyteller = Agent(
            name="storyteller",
            model=MODEL_ID,
            description="Cria conteúdo narrativo para RPG",
            instruction="""Você é um contador de histórias. Sua tarefa é:
            1. Enriquecer a resposta com elementos narrativos
            2. Sugerir twists interessantes para a história
            3. Criar NPCs, locais ou eventos memoráveis
            4. Manter o tom adequado ao universo do jogo"""
        )

        # Primeiro analisamos o contexto
        context = call_agent(context_analyzer, user_message)
    
        # Decidimos qual agente usar baseado no contexto
        if "regra" in context.lower() or "mecânica" in context.lower():
            response = call_agent(rules_expert, f"Contexto: {context}\nPergunta: {user_message}")
        else:
            # Para dúvidas narrativas, usamos ambos os especialistas
            rules_part = call_agent(rules_expert, f"Contexto: {context}\nPergunta: {user_message}\nSe não for sobre regras, responda 'Não se aplica'")
            story_part = call_agent(storyteller, f"Contexto: {context}\nPergunta: {user_message}")
        
            if "não se aplica" not in rules_part.lower():
                response = f"📜 Regras:\n{rules_part}\n\n📖 Narrativa:\n{story_part}"
            else:
                response = story_part
    
        # Exibimos a resposta formatada
        self.after(1000, self.display_message, "Mestre:", response)

    def show_dice_roll(self):
        self.home_frame.place_forget()
        self.generator_frame.place_forget()
        self.item_help_frame.place_forget()
        self.master_chat_frame.place_forget()
        self.dice_roll_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.dice_roll_frame.columnconfigure(0, weight=1)
        self.dice_roll_frame.rowconfigure(1, weight=1)

        # Botão Voltar
        ttk.Button(self.dice_roll_frame, text="Voltar", command=self.show_home).grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        # Imagem de Dados
        try:
            dice_image = Image.open("dados.png")
            # --- Redimensionar a imagem ---
            new_width = 150  # Defina a nova largura desejada
            new_height = 150 # Defina a nova altura desejada
            resized_dice_image = dice_image.resize((new_width, new_height))
            dice_photo = ImageTk.PhotoImage(resized_dice_image)
            dice_label = ttk.Label(self.dice_roll_frame, image=dice_photo)
            dice_label.image = dice_photo # Manter referência
            dice_label.grid(row=0, column=1, padx=10, pady=10, sticky="ne")
        except FileNotFoundError:
            ttk.Label(self.dice_roll_frame, text="Imagem de Dados não encontrada.").grid(row=0, column=1, padx=10, pady=10, sticky="ne")

        # Frame para os Radiobuttons
        dice_select_frame = ttk.Frame(self.dice_roll_frame)
        dice_select_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.selected_dice = tk.StringVar(value="d4")
        dices = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]

        for i, dice in enumerate(dices):
            ttk.Radiobutton(dice_select_frame, text=dice, variable=self.selected_dice, value=dice).pack(side="left", padx=5)

        # Botão de Rolagem
        roll_button = ttk.Button(self.dice_roll_frame, text="Rolar Dado", command=self.roll_dice)
        roll_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Label para exibir o resultado
        self.roll_result = tk.StringVar(value="Resultado:")
        result_label = ttk.Label(self.dice_roll_frame, textvariable=self.roll_result, font=("Arial", 12))
        result_label.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    def roll_dice(self):
        dice_type = self.selected_dice.get()
        if dice_type == "d4":
            result = random.randint(1, 4)
        elif dice_type == "d6":
            result = random.randint(1, 6)
        elif dice_type == "d8":
            result = random.randint(1, 8)
        elif dice_type == "d10":
            result = random.randint(1, 10)
        elif dice_type == "d12":
            result = random.randint(1, 12)
        elif dice_type == "d20":
            result = random.randint(1, 20)
        elif dice_type == "d100":
            result = random.randint(1, 100)
        else:
            result = "Selecione um dado"
        self.roll_result.set(f"Resultado: {result}")

    def update_class_image(self):
        current_class = self.class_list[self.selected_class_index]
        img_file = self.class_images.get(current_class)
    
        if img_file and os.path.exists(img_file):
            try:
                img = Image.open(img_file)
                img = img.resize((100, 100))
                self.class_photo = ImageTk.PhotoImage(img)
                self.class_image_label.config(image=self.class_photo)
                self.class_image_label.image = self.class_photo  # Manter referência
            except Exception as e:
                print(f"Erro ao carregar {img_file}: {e}")
                self.create_placeholder_class()
        else:
            print(f"Arquivo não encontrado: {img_file}")
            self.create_placeholder_class()

    def create_placeholder_class(self):
        img = Image.new("RGB", (100, 100), color=self.get_placeholder_color(self.selected_class_index))
        self.class_photo = ImageTk.PhotoImage(img)
        self.class_image_label.config(image=self.class_photo)
        self.class_image_label.image = self.class_photo

    def update_race_image(self):
        current_race = self.race_list[self.selected_race_index]
        img_file = self.race_images.get(current_race)
    
        if img_file and os.path.exists(img_file):
            try:
                img = Image.open(img_file)
                img = img.resize((100, 100))
                self.race_photo = ImageTk.PhotoImage(img)
                self.race_image_label.config(image=self.race_photo)
                self.race_image_label.image = self.race_photo  # Manter referência
            except Exception as e:
                print(f"Erro ao carregar {img_file}: {e}")
                self.create_placeholder_race()
        else:
            print(f"Arquivo não encontrado: {img_file}")
            self.create_placeholder_race()

    def create_placeholder_race(self):
        img = Image.new("RGB", (100, 100), color=self.get_placeholder_color(self.selected_race_index + len(self.class_list)))
        self.race_photo = ImageTk.PhotoImage(img)
        self.race_image_label.config(image=self.race_photo)
        self.race_image_label.image = self.race_photo

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
            self.generated_name.set(f"Nome: {generated_name_from_ai}")
        else:
            self.generated_name.set("Por favor, preencha todos os campos.")

    def call_name_generation_agent(self, prompt: str) -> str:
        name_generator_agent = Agent(
            name="name_generator",
            model=MODEL_ID,
            description="Agente para gerar nomes de personagens de fantasia.",
            instruction="""Você é um especialista em gerar nomes criativos e adequados para personagens de RPG de fantasia. 
            Considere a classe, a raça e o gênero fornecidos para criar um nome interessante e adequado ao contexto.
            Voce sempre envia apenas um nome e sobre nome sem nenhma informação a mais, evite ao maximo repetir nomes, 
            cada vez que for pedido para criar um nome novo mude o nome e o sobrenome 
            """,
        )
        return call_agent(name_generator_agent, prompt)

if __name__ == "__main__":
    app = App()
    app.mainloop()