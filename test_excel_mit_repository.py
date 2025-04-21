from src.infrastructure.repositories.excel_mit_repository import ExcelMitRepository

repo = ExcelMitRepository(r"docs/planilha_mit_final_v5.xlsx")

empresas = repo.obter_empresas()
print("Empresas encontradas:", empresas)

if empresas:
    for empresa in empresas:
        print(f"\n=== Carregando dados da empresa: {empresa} ===")
        
        periodo, dados_iniciais, debitos, suspensoes = repo.carregar_dados(empresa)

        print("\n--- Período de Apuração ---")
        print(periodo)

        print("\n--- Dados Iniciais ---")
        print(dados_iniciais)

        print("\n--- Débitos ---")
        print(debitos.head())

        print("\n--- Suspensões ---")
        print(suspensoes.head())
