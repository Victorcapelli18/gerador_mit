import unittest
from src.domain.entities.mit_entity import Mit, PeriodoApuracao, DadosIniciais, Debito, Imposto, Debitos
from src.domain.entities.responsible_entity import ResponsavelApuracao, TelefoneResponsavel
import datetime


class TestPeriodoApuracao(unittest.TestCase):
    def test_periodo_formatado(self):
        periodo = PeriodoApuracao(mes_apuracao=3, ano_apuracao=2025)
        self.assertEqual(periodo.periodo_formatado(), "202503")
        
    def test_eh_valido_periodo_passado(self):
        # Teste com período no passado (sempre válido se ano > ano atual)
        hoje = datetime.date.today()
        if hoje.year < 2025:
            periodo = PeriodoApuracao(mes_apuracao=1, ano_apuracao=2025)
            self.assertTrue(periodo.eh_valido())
        else:
            # Teste com período no passado no mesmo ano
            mes_passado = hoje.month - 1 if hoje.month > 1 else 12
            ano = hoje.year if hoje.month > 1 else hoje.year - 1
            periodo = PeriodoApuracao(mes_apuracao=mes_passado, ano_apuracao=ano)
            self.assertTrue(periodo.eh_valido())


class TestImposto(unittest.TestCase):
    def test_valor_total_vazio(self):
        imposto = Imposto()
        self.assertEqual(imposto.valor_total(), 0)
        
    def test_valor_total_com_debitos(self):
        imposto = Imposto()
        imposto.adicionar_debito(Debito(codigo_debito="0001", valor_debito=100.0))
        imposto.adicionar_debito(Debito(codigo_debito="0002", valor_debito=150.0))
        imposto.adicionar_debito(Debito(codigo_debito="0003", valor_debito=None))  # Não deve afetar o total
        
        self.assertEqual(imposto.valor_total(), 250.0)


class TestDebitos(unittest.TestCase):
    def test_valor_total(self):
        debitos = Debitos(balanco_lucro_real=True)
        
        # Adicionar alguns débitos ao IRPJ
        debitos.irpj.adicionar_debito(Debito(codigo_debito="0001", valor_debito=100.0))
        
        # Adicionar alguns débitos à CSLL
        debitos.csll.adicionar_debito(Debito(codigo_debito="0002", valor_debito=200.0))
        
        # O valor total deve ser a soma de todos os impostos
        self.assertEqual(debitos.valor_total(), 300.0)


class TestMit(unittest.TestCase):
    def setUp(self):
        # Configurar objetos para testes
        self.periodo = PeriodoApuracao(mes_apuracao=3, ano_apuracao=2025)
        
        responsavel = ResponsavelApuracao(
            cpf="12345678900",
            tel_responsavel=TelefoneResponsavel(ddd="11", num_telefone="987654321"),
            email_responsavel="teste@teste.com"
        )
        
        self.dados_iniciais = DadosIniciais(
            sem_movimento=False,
            qualificacao_pj=1,
            tributacao_lucro=1,
            variacoes_monetarias=1,
            regime_pis_cofins=1,
            responsavel_apuracao=responsavel
        )
        
        self.debitos = Debitos(balanco_lucro_real=True)
        self.debitos.irpj.adicionar_debito(Debito(codigo_debito="0001", valor_debito=100.0))
        
        # Criar objeto Mit
        self.mit = Mit(
            periodo_apuracao=self.periodo,
            dados_iniciais=self.dados_iniciais,
            debitos=self.debitos
        )
    
    def test_eh_sem_movimento(self):
        # O objeto criado não é sem movimento
        self.assertFalse(self.mit.eh_sem_movimento())
        
        # Modificar para sem movimento
        dados_com_movimento = DadosIniciais(
            sem_movimento=True,
            qualificacao_pj=1,
            tributacao_lucro=1,
            variacoes_monetarias=1,
            regime_pis_cofins=1,
            responsavel_apuracao=self.dados_iniciais.responsavel_apuracao
        )
        
        mit_sem_movimento = Mit(
            periodo_apuracao=self.periodo,
            dados_iniciais=dados_com_movimento,
            debitos=self.debitos
        )
        
        self.assertTrue(mit_sem_movimento.eh_sem_movimento())
    
    def test_tem_debitos(self):
        # O objeto criado tem débitos
        self.assertTrue(self.mit.tem_debitos())
        
        # Criar objeto sem débitos
        debitos_vazios = Debitos(balanco_lucro_real=True)
        mit_sem_debitos = Mit(
            periodo_apuracao=self.periodo,
            dados_iniciais=self.dados_iniciais,
            debitos=debitos_vazios
        )
        
        self.assertFalse(mit_sem_debitos.tem_debitos())
    
    def test_gerar_nome_arquivo(self):
        nome_arquivo = self.mit.gerar_nome_arquivo("EMPRESA_TESTE")
        self.assertEqual(nome_arquivo, "EMPRESA_TESTE--MIT--202503.json")


if __name__ == "__main__":
    unittest.main() 