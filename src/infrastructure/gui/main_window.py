import os
import json
import customtkinter as ctk
from tkinter import filedialog
from tkinter.messagebox import showinfo
from src.usecases.generate_mit_json import GeradorMitUseCase
from src.infrastructure.repositories.excel_mit_repository import ExcelMitRepository
from .widgets import criar_widgets


class MainWindow:
    def __init__(self):
        self.schema = self.carregar_schema()
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
            # O arquivo atual (main_window.py) está em src/infrastructure/gui/
            # O schema (mit_json_schema.json) está em src/schemas/
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
            showinfo("Erro", f"Erro ao decodificar o arquivo de schema JSON: {path}\nO arquivo pode estar corrompido ou não ser um JSON válido.")
            return {}
        except Exception as e:
            showinfo("Erro", f"Ocorreu um erro desconhecido ao carregar o schema: {str(e)}\nCaminho tentado: {path}")
            return {}

    def selecionar_excel(self):
        caminho = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if caminho:
            self.excel_path = caminho
            self.excel_label.configure(text=caminho)

    def selecionar_pasta_saida(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.output_path = pasta
            self.output_label.configure(text=pasta)

    def gerar_json(self):
        if not hasattr(self, 'excel_path') or not hasattr(self, 'output_path'):
            showinfo("Erro", "Selecione o arquivo e a pasta de saída!")
            return

        try:
            self.progressbar.pack()
            self.progressbar.set(0)

            repository = ExcelMitRepository(self.excel_path)
            usecase = GeradorMitUseCase(repository, self.output_path, self.schema)
            usecase.executar()

            self.progressbar.set(1)
            showinfo("Sucesso", "Arquivos gerados com sucesso!")

        except Exception as e:
            showinfo("Erro", f"Falha na geração: {str(e)}")

        finally:
            self.progressbar.pack_forget()

    def run(self):
        self.root.mainloop()
