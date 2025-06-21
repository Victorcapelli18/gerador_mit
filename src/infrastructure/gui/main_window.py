import os
import json
import customtkinter as ctk
from tkinter import filedialog
from tkinter.messagebox import showinfo
from src.infrastructure.gui.presenter import MitPresenter, ViewInterface
from .widgets import criar_widgets


class MainWindow(ViewInterface):
    def __init__(self):
        self.schema = self.carregar_schema()
        self.presenter = MitPresenter(self)
        self.presenter.definir_schema(self.schema)
        self.setup_ui()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Gerador MIT")
        self.root.geometry("600x400")

        criar_widgets(self)

    def carregar_schema(self):
        try:
            current_file_dir = os.path.dirname(__file__)
            infrastructure_dir = os.path.dirname(current_file_dir)
            src_dir = os.path.dirname(infrastructure_dir)
            path = os.path.join(src_dir, "schemas", "mit_json_schema.json")

            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            showinfo("Erro", f"Arquivo de schema JSON não encontrado em: {path}\nPor favor, verifique se o arquivo 'mit_json_schema.json' existe em 'src/schemas/'.")
            return {}
        except json.JSONDecodeError:
            showinfo("Erro", f"Erro ao decodificar o arquivo de schema JSON: {path}\nO arquivo pode estar corrompido ou não ser um JSON Válido.")
            return {}
        except Exception as e:
            showinfo("Erro", f"Ocorreu um erro desconhecido ao carregar o schema: {str(e)}\nCaminho tentado: {path}")
            return {}
        
    def selecionar_excel(self):
        caminho = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if caminho:
            self.presenter.definir_caminho_excel(caminho)
            self.excel_label.configure(text=caminho)

    def selecionar_pasta_saida(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.presenter.definir_pasta_saida(pasta)
            self.output_label.configure(text=pasta)

    def gerar_json(self):
        self.presenter.gerar_json()

    # Implementacao da interface ViewInterface
    def mostrar_erro(self, mensagem: str) -> None:
        showinfo("Erro", mensagem)

    def mostrar_sucesso(self, mensagem: str) -> None:
        showinfo("Sucesso", mensagem)

    def atualizar_progresso(self, valor: float) -> None:
        self.progressbar.set(valor)
        self.root.update_idletasks()

    def mostrar_progresso(self) -> None:
        self.progressbar.pack()

    def esconder_progresso(self) -> None:
        self.progressbar.pack_forget()
    
    def run(self):
        self.root.mainloop()