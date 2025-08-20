from src.domain.entities.mit_entity import MitEntity, PeriodoApuracaoEntity, DadosIniciaisEntity, DebitoEntity, ImpostoEntity, DebitosEntity, SuspensaoEntity, DebitoSuspensoEntity
from src.domain.entities.company_entity import Company
from src.domain.entities.responsible_entity import ResponsavelApuracao, TelefoneResponsavel, RegistroCrc
from src.usecases.generate_mit_json_dto import (
    GenerateMitJsonInputDTO, EmpresaDTO, PeriodoApuracaoDTO, DadosIniciaisDTO, 
    DebitoDTO, ImpostoDTO, DebitoSuspensoDTO, SuspensaoDTO, ResponsavelApuracaoDTO, TelefoneResponsavelDTO, RegistroCrcDTO
)

def map_dto_to_entity(input_dto: GenerateMitJsonInputDTO) -> MitEntity:
    empresa = Company(**input_dto.empresa.dict())
    periodo_apuracao = PeriodoApuracaoEntity(**input_dto.periodo_apuracao.dict())
    dados_iniciais = DadosIniciaisEntity(**input_dto.dados_iniciais.dict())
    responsavel = ResponsavelApuracao(
        nome=input_dto.responsavel.nome,
        cpf=input_dto.responsavel.cpf,
        email=input_dto.responsavel.email,
        telefone=TelefoneResponsavel(**input_dto.responsavel.telefone.dict()),
        crc=RegistroCrc(**input_dto.responsavel.crc.dict()) if input_dto.responsavel.crc else None
    )
    debitos = [DebitoEntity(**debito.dict()) for debito in input_dto.debitos] if input_dto.debitos else []
    impostos = [ImpostoEntity(**imposto.dict()) for imposto in input_dto.impostos] if input_dto.impostos else []
    debitos_suspensos = [
        DebitoSuspensoEntity(
            debito=DebitoEntity(**ds.debito.dict()),
            suspensoes=[SuspensaoEntity(**s.dict()) for s in ds.suspensoes]
        ) for ds in input_dto.debitos_suspensos
    ] if input_dto.debitos_suspensos else []

    return MitEntity(
        empresa=empresa,
        periodo_apuracao=periodo_apuracao,
        dados_iniciais=dados_iniciais,
        responsavel=responsavel,
        debitos=debitos,
        impostos=impostos,
        debitos_suspensos=debitos_suspensos
    )