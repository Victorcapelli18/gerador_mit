from typing import Dict, List
import pandas as pd
from src.domain.entities.responsible_entity import ResponsavelApuracao, TelefoneResponsavel, RegistroCrc
from src.domain.entities.mit_entity import DadosIniciais, Debito, Debitos, Imposto, DebtioSuspeno, Suspensao, Mit, PeriodoApuracao

class GeradorService:
    def montar_dados_iniciais(self, dados: Dict) -> DadosIniciais:
        telefone = TelefoneResponsavel(
            ddd=str(dados["ddd"]).zfill(2),
            num_telefone=str(dados["num_telefone"]).zfill(8)
        )

        registro = RegistroCrc(
            uf_registro=dados["uf_registro"],
            num_registro=dados["num_registro"]
        )

        responsavel = ResponsavelApuracao(
            cpf=str(dados["cpf_responsavel"]).zfill(11),
            tel_responsavel=telefone,
            email_responsavel=dados.get("email_responsavel"),
            registro_crc=registro
        )

        return DadosIniciais(
            sem_movimento=bool(dados["sem_movimento"]),
            qualificacao_pj=int(dados["qualificacao_pj"]),
            tributacao_lucro=int(dados["tributacao_lucro"]),
            variacoes_monterias=int(dados["variacoes_monetarias"]),
            regime_pis_cofins=int(dados["regime_pis_cofins"]),
            responsavel_apuracao=responsavel
        )

    def montar_debitos(self, df: pd.DataFrame) -> Debitos:
        impostos = {}
        for _, row in df.iterrows():
            imposto = row["imposto"].lower().replace(" ", "_")
            if imposto not in impostos:
                impostos[imposto] = []

            debito = Debito(
                id_debito=int(row["id_debito"]),
                codigo_debito=str(row["codigo_debito"]).zfill(6),
                valor_debito=float(row["valor_debito"]),
                id_evento_debito=row.get("id_evento_debito"),
                ano_postergado=row.get("ano_postergado"),
                trim_postergado=row.get("trim_postergado"),
                ano_debito=row.get("ano_debito"),
                cnpj_scp=row.get("cnpj_estabelecimento")
            )
            impostos[imposto].append(debito)

        return Debitos(
            balanco_lucro_real=True,
            **{imp: Imposto(lista_debitos=lst) for imp, lst in impostos.items()}
        )

    def montar_suspensoes(self, df: pd.DataFrame) -> List[Suspensao]:
        suspensoes_dict = {}
        for _, row in df.iterrows():
            num_proc = str(row["numero_processo"]).zfill(20)
            if num_proc not in suspensoes_dict:
                suspensoes_dict[num_proc] = Suspensao(
                    tipo_suspensao=int(row["tipo_suspensao"]),
                    motivo_suspensao=int(row["motivo_suspensao"]),
                    com_deposito=bool(row["com_deposito"]),
                    numero_processo=num_proc,
                    processo_terceiro=row.get("processo_terceiro"),
                    data_decisao=row.get("data_decisao"),
                    vara_jucidiaria=row.get("vara_judiciaria"),
                    codigo_municipio_sj=row.get("codigo_municipio_sj"),
                    lista_debitos_suspensos=[]
                )

            suspensoes_dict[num_proc].lista_debitos_suspensos.append(
                DebtioSuspeno(
                    id_debito_suspeno=int(row["id_debito_suspenso"]),
                    valor_suspenso=float(row["valor_suspenso"])
                )
            )

        return list(suspensoes_dict.values())