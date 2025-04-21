from src.infrastructure.adapters.excel_adpter import ExcelAdapter





caminho = "docs/planilha_mit_final_v5.xlsx"



adapter = ExcelAdapter()
dados = adapter.carregar_planilha_excel(caminho)

print("✅ Abas carregadas:")
for aba, registros in dados.items():
    print(f"- {aba}: {len(registros)} registros")
    if registros:
        print("  Exemplo:", registros[0])