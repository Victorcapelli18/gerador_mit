import customtkinter as ctk

def criar_widgets(app):
    # Frame principal
    app.main_frame = ctk.CTkFrame(app.root)
    app.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Titulo
    app.title_label = ctk.CTkLabel(
        app.main_frame,
        text="Gerador MIT",
        font =("Helvetica", 24)
    )
    app.title_label.pack(pady=20)

    # Botao Excel
    app.excel_button = ctk.CTkButton(
        app.main_frame,
        text="Selecionar Arquivo Excel",
        command=app.selecionar_excel
    )
    app.excel_button.pack(pady=10)

    app.excel_label = ctk.CTkLabel(
        app.main_frame,
        text="Nenhum arquivo selecionado",
        wraplength=500
    )
    app.excel_label.pack(pady=5)

    # Botao pasta saida
    app.output_button = ctk.CTkButton(
        app.main_frame,
        text="Selecionar Pasta de Saída",
        command=app.selecionar_pasta_saida
    )
    app.output_button.pack(pady=10)

    app.output_label = ctk.CTkLabel(
        app.main_frame,
        text="Nenhuma pasta selecionada",
        wraplength=500
    )
    app.output_label.pack(pady=5)

    # Botao de geracao
    app.generate_button = ctk.CTkButton(
        app.main_frame,
        text="Gerar JSON",
        command=app.gerar_json,
        fg_color="green",
        hover_color="darkgreen"
    )
    app.generate_button.pack(pady=20)

    # Barra de progresso
    app.progressbar = ctk.CTkProgressBar(app.main_frame)
    app.progressbar.pack(pady=10)
    app.progressbar.set(0)
    app.progressbar.pack_forget()