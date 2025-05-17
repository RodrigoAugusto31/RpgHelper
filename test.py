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

os.environ["GOOGLE_API_KEY"] = "SUA_CHAVE_API_AQUI"  # Substitua pela sua chave real
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
        ttk.Button(self.home_frame, text="Ajuda com Itens", command=self.show_item_help).pack(pady=5, padx=20, fill="x")
        ttk.Button(self.home_frame, text="Converse com o Mestre", command=self.show_master_chat).pack(pady=5, padx=20, fill="x")
        ttk.Button(self.home_frame, text="Rodar Dados", command=self.show_dice_roll).pack(pady=5, padx=20, fill="x")

        # --- Conteúdo do Gerador de Nome ---
        self.generator_frame.columnconfigure(0, weight=1)
        self.generator_frame.columnconfigure(1, weight=1)
        self.generator_frame.rowconfigure(9, weight=1)
        ttk.Button(self.generator_frame, text="Voltar", command=self.show_home).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        ttk.Label(self.generator_frame, text="Gerador de Nome", font=("Arial", 14)).grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        self.class_list = ["Barbarian", "Bard", "Cleric", "Druid", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Warrior", "Wizard"]
        self.race_list = ["Dragonborn", "Dwarf", "Elf", "Gnome", "Half-elf", "Half-orc", "Halfling", "Human", "Tiefling"]
        self.class_images = [None] * len(self.class_list)
        self.race_images = [None] * len(self.race_list)
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
        self.generated_name = tk.StringVar(value="Nome Gerado:")
        self.generated_name_label = ttk.Label(self.generator_frame, textvariable=self.generated_name)
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
        self.item_help_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.item_help_frame.columnconfigure(0, weight=1)
        self.item_help_frame.rowconfigure(1, weight=1) # Para a área de chat expandir

        # Botão Voltar
        ttk.Button(self.item_help_frame, text="Voltar", command=self.show_home).grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        # Imagem de Itens
        try:
            itens_image = Image.open("itens.png")
            # --- Redimensionar a imagem ---
            new_width = 150  # Defina a nova largura desejada
            new_height = 150 # Defina a nova altura desejada
            resized_itens_image = itens_image.resize((new_width, new_height))
            itens_photo = ImageTk.PhotoImage(resized_itens_image)
            itens_label = ttk.Label(self.item_help_frame, image=itens_photo)
            itens_label.image = itens_photo # Manter referência
            itens_label.grid(row=0, column=1, padx=10, pady=10, sticky="ne")
        except FileNotFoundError:
            ttk.Label(self.item_help_frame, text="Imagem de Itens não encontrada.").grid(row=0, column=1, padx=10, pady=10, sticky="ne")

        # Área de Chat
        self.item_chat_area = tk.Text(self.item_help_frame, state='disabled', wrap='word')
        self.item_chat_area.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Entrada de Texto
        self.item_input_entry = ttk.Entry(self.item_help_frame)
        self.item_input_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.item_input_entry.bind("<Return>", self.send_item_message) # Enviar com Enter

        # Botão Enviar
        send_button = ttk.Button(self.item_help_frame, text="Enviar", command=self.send_item_message)
        send_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

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
        # Aqui você implementaria a lógica para obter a ajuda sobre itens
        # Por enquanto, vamos simular uma resposta simples
        item_response = f"Ah, você precisa de ajuda com itens? Conte-me mais sobre qual item você tem dúvidas!"
        self.after(2000, self.display_item_message, "Ajuda:", item_response)

    def show_master_chat(self):
        self.home_frame.place_forget()
        self.generator_frame.place_forget()
        self.item_help_frame.place_forget()
        self.dice_roll_frame.place_forget()
        self.master_chat_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.master_chat_frame.columnconfigure(0, weight=1)
        self.master_chat_frame.rowconfigure(1, weight=1) # Para a área de chat expandir

        # Botão Voltar
        ttk.Button(self.master_chat_frame, text="Voltar", command=self.show_home).grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        # Imagem do Mestre
        try:
            master_image = Image.open("mestre.png")
            # --- Redimensionar a imagem ---
            new_width = 150  # Defina a nova largura desejada
            new_height = 150 # Defina a nova altura desejada
            resized_master_image = master_image.resize((new_width, new_height))
            master_photo = ImageTk.PhotoImage(resized_master_image)
            master_label = ttk.Label(self.master_chat_frame, image=master_photo)
            master_label.image = master_photo # Manter referência
            master_label.grid(row=0, column=1, padx=10, pady=10, sticky="ne")
        except FileNotFoundError:
            ttk.Label(self.master_chat_frame, text="Imagem do Mestre não encontrada.").grid(row=0, column=1, padx=10, pady=10, sticky="ne")

        # Área de Chat
        self.chat_area = tk.Text(self.master_chat_frame, state='disabled', wrap='word')
        self.chat_area.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Entrada de Texto
        self.input_entry = ttk.Entry(self.master_chat_frame)
        self.input_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.input_entry.bind("<Return>", self.send_message) # Enviar com Enter

        # Botão Enviar
        send_button = ttk.Button(self.master_chat_frame, text="Enviar", command=self.send_message)
        send_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

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
        # Aqui você implementaria a lógica para obter a resposta do "mestre"
        # Por enquanto, vamos simular uma resposta simples
        master_response = f"Hmm, interessante pergunta sobre D&D! Deixe-me pensar..."
        self.after(2000, self.display_message, "Mestre:", master_response)

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
        img_width = 50
        img_height = 50
        img = Image.new("RGB", (img_width, img_height), color=self.get_placeholder_color(self.selected_class_index))
        mask = Image.new('L', (img_width, img_height), 0)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img_width, img_height), fill=255)
        img.putalpha(mask)
        self.class_photo = ImageTk.PhotoImage(img)
        self.class_image_label.config(image=self.class_photo)

    def update_race_image(self):
        img_width = 50
        img_height = 50
        img = Image.new("RGB", (img_width, img_height), color=self.get_placeholder_color(self.selected_race_index + len(self.class_list)))
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