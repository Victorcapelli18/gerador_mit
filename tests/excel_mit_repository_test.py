from infrastructure.repositories.excel_mit_repository import ExcelMitRepository



repo = ExcelMitRepository(r"docs\planilha_mit_final_v5.xlsx")

print(repo.obter_empresas())