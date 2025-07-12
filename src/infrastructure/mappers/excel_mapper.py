from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import itertools
import re
from src.domain.entities.mit_entity import (
    MitEntity,
    PeriodoApuracaoEntity,
    DadosIniciaisEntity,
    DebitoEntity,
    ImpostoEntity,
    DebitosEntity,
    SuspensaoEntity,
    DebitoSuspensoEntity
)
from src.domain.entities.responsible_entity import (
    ResponsavelApuracao,
    TelefoneResponsavel,
    RegistroCrc
)


class ExcelMapper:
    def __init__(self):
        # armazena o CNPJ encontrado na aba PeriodoApuracao
        self.cnpj_encontrado = None

    def _to_str_or_none(self, value: Any) -> Optional[str]:
        if value is None or str(value).strip() == "":
            return None
        return str(value).strip()
    
    def _to_int_or_none(self, value: Any) -> Optional[int]:
        if value is None or str(value).strip() == "":
            return None
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return None
        
    def _to_bool(self, value: Any) -> bool:
            val_str = self._to_str_or_none(value)
            if val_str is None:
                return False
            return val_str.lower() in ["1", "true", "sim", "s", "verdadeiro", "v"]

    def _to_bool_or_none(self, value: Any) -> Optional[bool]:
        val_str = self._to_str_or_none(value)
        if val_str is None:
            return None
        return val_str.lower() in ["1", "true", "sim", "s", "verdadeiro", "v"]                                                                                                                                                                                                                                                                       

    def _to_float(self, value: Any) -> Optional[float]:
        val_str = self._to_str_or_none(value)
        if val_str is None:
            return None
        try:
            return float(val_str.replace(",", "."))
        except (ValueError, TypeError):
            return None
        
    def _parse_excel_date_to_timestamp_int(self, value: Any) -> Optional[int]:
        if value is None or str(value).strip() == "":
            return None
        
        if isinstance(value, datetime):
            return int(value.timestamp())
        
        if isinstance(value, (int, float)):
            try:
                if value > 0 and value < 2958465:
                    return int((datetime(1899, 12, 30) + timedelta(days=value)).timestamp())
            except (TypeError, ValueError, OverflowError):
                pass

        val_str = str(value).strip()
        date_formats = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M")
        dt_obj = None
        for fmt in date_formats:
            try:
                dt_obj = datetime.strptime(val_str, fmt)
                break
            except ValueError:
                continue
        
        return int(dt_obj.timestamp()) if dt_obj else None
    
    def _get_single_row_data(self, data_list: list[Dict], sheet_name: str) -> Optional[Dict]:
        if not data_list:
            return None
        return data_list[0]
    
    def _map_responsavel_apuracao(self, row: dict) -> ResponsavelApuracao:
        tel_responsavel = None
        ddd = self._to_str_or_none(row.get("Ddd"))
        num_telefone = self._to_str_or_none(row.get("NumTelefone"))
        if ddd and num_telefone:
            tel_responsavel = TelefoneResponsavel(ddd=ddd, num_telefone=num_telefone)

        registro_crc = None
        uf_registro = self._to_str_or_none(row.get("UfRegistro"))
        num_registro = self._to_str_or_none(row.get("NumRegistro"))
        if uf_registro and num_registro:
            registro_crc = RegistroCrc(uf_registro=uf_registro, num_registro=num_registro)

        return ResponsavelApuracao(
            cpf=str(row.get("CpfResponsavel", "")),
            tel_responsavel=tel_responsavel,
            email_responsavel=self._to_str_or_none(row.get("EmailResponsavel")),
            registro_crc=registro_crc
        )
    
    def _map_periodo_apuracao(self, row: dict) -> PeriodoApuracaoEntity:
        # Imprime as colunas disponíveis para debug
        print(f"Colunas disponíveis em PeriodoApuracao: {list(row.keys())}")

        # O CNPJ estará na segunda coluna da aba PeriodoApuracao
        cnpj = None

        # Tenta encontrar a coluna que contém o CNPJ
        colunas = list(row.keys())
        if len(colunas) >= 2:
            # A segunda coluna deve contar o CNPJ
            possivel_coluna_cnpj = colunas[1]
            print(f"Coluna que pode conter CNPJ: {possivel_coluna_cnpj}")
            valor = self._to_str_or_none(row.get(possivel_coluna_cnpj))
            if valor:
                print(f"Valor encontrado na possível coluna CNPJ: {valor}")
                # Limpar para ter apensas números
                cnpj_limpo = "".join(filter(str.isdigit, valor))
                if len(cnpj_limpo) >= 8:
                    print(f"CNPJ extraído da segunda coluna: {cnpj_limpo}")
                    # Armazenamos o CNPJ para uso posterior
                    self.cnpj_encontrado = cnpj_limpo
        
        return PeriodoApuracaoEntity(
            mes_apuracao=self._to_int_or_none(row.get("MesApuracao")),
            ano_apuracao=self._to_int_or_none(row.get("AnoApuracao"))
        )
    
    def _map_dados_iniciais(self, row: dict) -> DadosIniciaisEntity:
        responsavel = self._map_responsavel_apuracao(row)

        # Usamos preferencialmente o CNPJ que já encontramos na aba PeridoApuracao
        cnpj = self.cnpj_encontrado

        # Se nãao encontramos antes, tentamos extrair de várias colunas possíveis

        if not cnpj:
            colunas_cnpj = [
                "CNPJ", "Cnpj", "cnpj", "CnpjEmpresa", "cnpj_empresa", 
                "CnpjEstabelecimento", "CnpjBase", "cnpj_base", "NrCnpj",
                "NumCnpj", "numeroCnpj", "cnpj_contribuinte", "CnpjContribuinte"
            ]
            
            # Imprimir todas as chaves disponíveis para debug
            print(f"Colunas disponíveis em dados_iniciais: {list(row.keys())}")

            for coluna_possivel in colunas_cnpj:
                if coluna_possivel in row and row[coluna_possivel]:
                    valor = self._to_str_or_none(row[coluna_possivel])
                    print(f"ncontrado na coluna {coluna_possivel}: {valor}")
                    if valor:
                        # Limpar o CNPJ para conter apensas números
                        cnpj_limpo = "".join(filter(str.isdigit, valor))
                        if len(cnpj_limpo) >= 8:
                            cnpj = cnpj_limpo
                            print(f"CNPJ extraído: {cnpj}")
                            break
            
            if not cnpj and "Empresa" in row:
                nome_empresa = self._to_str_or_none(row.get("Empresa", ""))
                if nome_empresa:
                    print(f"Tentando extrais CNPJ do nome da empresa: {nome_empresa}")
                    # Procura por padrões de CNPJ (xx.xxx.xxx/xxxx-xx)
                    padrao_cnpj = r'(\d{2}[\.\s]?\d{3}[\.\s]?\d{3}[\/\.\s]?\d{4}[-\.\s]?\d{2})'
                    match = re.search(padrao_cnpj, nome_empresa)
                    if match:
                        cnpj_encontrado = match.group(1)
                        cnpj_limpo = "".join(filter(str.isdigit, cnpj_encontrado))
                        if len(cnpj) >= 8:
                            cnpj = cnpj_limpo
                            print(f"CNPJ extraído do nome da empresa: {cnpj}")
                    else:
                        # Procura por qualquer sequencia de 14 digitos do nome da empresa
                        padrao_numrico = r'(\d{14})'
                        match = re.search(padrao_numrico, nome_empresa)
                        if match:
                            cnpj = match.group(1)
                            print(f"Sequencia numerica extraida do nome da empresa: {cnpj}")

        # Se encontramos o CNPJ, informamos que ele está sendo usado
        if cnpj:
            print(f"Usando CNPJ encontrado: {cnpj}")

        return DadosIniciaisEntity(
            sem_movimento=self._to_bool(row.get("SemMovimento")),
            qualificacao_pj=self._to_int_or_none(row.get("QualificacaoPj")),
            tributacao_lucro=self._to_int_or_none(row.get("TributacaoLucro")),
            variacoes_monetarias=self._to_int_or_none(row.get("VariacoesMonetarias")),
            regime_pis_cofins=self._to_int_or_none(row.get("RegimePisCofins")),
            responsavel_apuracao=responsavel,
            cnpj=cnpj
        )
    
    def _map_debitos_estrutura(self, debitos_data: list[dict]) -> DebitosEntity:
        impostos_map: Dict[str, list[DebitoEntity]] = {}

        known_tax_fields_excel_to_entity = {
            "IRPJ": "irpj", "CSLL": "csll", "IRRF": "irrf", "IPI": "ipi",
            "IOF": "iof", "PIS/PASEP": "pis_pasep", "PIS": "pis_pasep", "PASEP": "pis_pasep",
            "COFINS": "cofins",
            "CONTRIBUIÇÕES DIVERSAS": "contribuicoes_diversas", "CONTRIBUICOES DIVERSAS": "contribuicoes_diversas",
            "CPSS": "cpss"
        }

        for linha_debito in debitos_data:
            imposto_nome_excel = self._to_str_or_none(linha_debito.get("Imposto"))
            if not imposto_nome_excel:
                continue

            imposto_nome_excel_upper = imposto_nome_excel.upper().strip()
            entity_attr_name = known_tax_fields_excel_to_entity.get(imposto_nome_excel_upper)

            if not entity_attr_name:
                continue

            debito = DebitoEntity(
                id_debito=self._to_int_or_none(linha_debito.get("IdDebito")),
                codigo_debito=str(linha_debito.get("CodigoDebito", "")),
                valor_debito=self._to_float(linha_debito.get("ValorDebito")),
                ano_debito=self._to_int_or_none(linha_debito.get("PaDebito")),
                cnpj_scp=self._to_str_or_none(linha_debito.get("CnpjEstabelecimento"))
            )

            if entity_attr_name not in impostos_map:
                impostos_map[entity_attr_name] = []
            impostos_map[entity_attr_name].append(debito)

        debitos_entity_args = {"balanco_lucro_real": False}
        for entity_field, tax_list in impostos_map.items():
            debitos_entity_args[entity_field] = ImpostoEntity(lista_debitos=tax_list)

        all_entity_tax_fields = [
            "irpj", "csll", "irrf", "ipi", "iof", "pis_pasep",
            "cofins", "contribuicoes_diversas", "cpss"
        ]
        for field in all_entity_tax_fields:
            if field not in debitos_entity_args:
                debitos_entity_args[field] = ImpostoEntity()

        return DebitosEntity(**debitos_entity_args)
    
    def _map_lista_suspensoes(self, suspensoes_data: list[dict]) -> list[SuspensaoEntity]:
        lista_suspensoes_final = []

        keyfunc = lambda x: (
            self._to_str_or_none(x.get("NumeroProcesso")),
            self._to_int_or_none(x.get("TipoSuspensao")),
            self._to_int_or_none(x.get("MotivoSuspensao"))
        )
        suspensoes_data.sort(key=keyfunc)

        for key_group, group_itens_iter in itertools.groupby(suspensoes_data, key=keyfunc):
            group_items = list(group_itens_iter)
            if not group_items:
                continue

            primeira_linha_grupo = group_items[0]

            debitos_suspensos_list: list[DebitoSuspensoEntity] = []
            for item_suspensao in group_items:
                id_deb_susp = self._to_int_or_none(item_suspensao.get("IdDebitoSuspenso"))
                val_susp = self._to_float(item_suspensao.get("ValorSuspenso"))
                if id_deb_susp is not None and val_susp is not None:
                    debitos_suspensos_list.append(
                        DebitoSuspensoEntity(id_debito_suspenso=id_deb_susp, valor_suspenso=val_susp)
                    )
            
            if not debitos_suspensos_list and not self._to_str_or_none(primeira_linha_grupo.get("NumeroProcesso")):
                continue

            suspensao = SuspensaoEntity(
                tipo_suspensao=self._to_int_or_none(primeira_linha_grupo.get("TipoSuspensao")),
                motivo_suspensao=self._to_int_or_none(primeira_linha_grupo.get("MotivoSuspensao")),
                com_deposito=self._to_bool(primeira_linha_grupo.get("ComDeposito")),
                numero_processo=str(primeira_linha_grupo.get("NumeroProcesso", "")),
                processo_terceiro=self._to_bool_or_none(primeira_linha_grupo.get("ProcessoTerceiro")),
                data_decisao=self._parse_excel_date_to_timestamp_int(primeira_linha_grupo.get("DataDecisao")),
                vara_judiciaria=self._to_int_or_none(primeira_linha_grupo.get("VaraJudiciaria")),
                codigo_municipio_sj=self._to_str_or_none(primeira_linha_grupo.get("CodigoMunicipioSJ")),
                lista_debitos_suspensos=debitos_suspensos_list
            )
            lista_suspensoes_final.append(suspensao)

        return lista_suspensoes_final
    
    def map_to_mit(self, dados_empresa_por_aba: Dict[str, list[Dict]]) -> MitEntity:
        # Limpa o CNPJ encontrado entre diferentes chamadas
        self.cnpj_encontrado = None

        periodo_data_row = self._get_single_row_data(
            dados_empresa_por_aba.get("PeriodoApuracao", []), "PeriodoApuracao"
        )
        dados_iniciais_row = self._get_single_row_data(
            dados_empresa_por_aba.get("DadosIniciais", []), "DadosIniciais"
        )

        debitos_data_list = dados_empresa_por_aba.get("Debitos", [])
        suspensoes_data_list = dados_empresa_por_aba.get("ListaSuspensoes", [])

        if periodo_data_row is None:
            raise ValueError("Dadis de 'PeriodoApuracao' são obrigatórios e não foram encontrados para a empresa.")
        if dados_iniciais_row is None:
            raise ValueError("Dados de 'DadosIniciais' são obrigatórios e não foram encontrados para a empresa.")
        
        periodo_apuracao_obj = self._map_periodo_apuracao(periodo_data_row)
        dados_iniciais_obj = self._map_dados_iniciais(dados_iniciais_row)
        debitos_obj = self._map_debitos_estrutura(debitos_data_list)
        lista_suspensoes_obj = self._map_lista_suspensoes(suspensoes_data_list)

        # log para garantir que o CNPJ foi encontrado
        if dados_iniciais_obj.cnpj:
            print(f"CNPJ filial utilizado {dados_iniciais_obj.cnpj}")
        else:
            print("ATENÇÃO: nenhum CNPJ foi encontrado para esta empresa!")

        return MitEntity(
            periodo_apuracao=periodo_apuracao_obj,
            dados_iniciais=dados_iniciais_obj,
            debitos=debitos_obj,
            lista_suspensoes=lista_suspensoes_obj
        )