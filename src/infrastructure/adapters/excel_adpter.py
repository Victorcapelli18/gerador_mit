import pandas as pd

class ExcelAdapter:
    def carregar_planilha_excel(self, caminho: str) -> dict[str, list[dict]]:
        xlsx = pd.read_excel(caminho, sheet_name=None)

        return {
            "PeriodoApuracao": xlsx.get("PeriodoApuracao", pd.DataFrame()).fillna("").to_dict(orient="records"),
            "DadosIniciais": xlsx.get("DadosIniciais", pd.DataFrame()).fillna("").to_dict(orient="records"),
            "Debitos": xlsx.get("Debitos", pd.DataFrame()).fillna("").to_dict(orient="records"),
            "ListaSuspensoes": xlsx.get("ListaSuspensoes", pd.DataFrame()).fillna("").to_dict(orient="records"),
        }
    



if __name__ == "__main__":
    caminho = "docs/planilha_mit_final_v5.xlsx"  # ajuste se necessário

    adapter = ExcelAdapter()
    dados = adapter.carregar_planilha_excel(caminho)

    print("✅ Abas carregadas:")
    for aba, registros in dados.items():
        print(f"- {aba}: {len(registros)} registros")
        if registros:
            print("  Exemplo:", registros[0])