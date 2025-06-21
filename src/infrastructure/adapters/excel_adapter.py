import pandas as pd

class ExcelAdapter:
    def carregar_planilha_excel(self, caminho: str) -> dict[str, list[dict]]:
        xlsx = pd.read_excel(caminho, sheet_name=None, engine='openpyxl')

        return {
            "PeriodoApuracao": xlsx.get("PeriodoApuracao", pd.DataFrame()).fillna("").to_dict(orient="records"),
            "DadosIniciais": xlsx.get("DadosIniciais", pd.DataFrame()).fillna("").to_dict(orient="records"),
            "Debitos": xlsx.get("Debitos", pd.DataFrame()).fillna("").to_dict(orient="records"),
            "ListaSuspensoes": xlsx.get("ListaSuspensoes", pd.DataFrame()).fillna("").to_dict(orient="records"),
        }