from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

# --- DTOs auxiliares (componentes do MIT) ---

class DebitoDTO(BaseModel):
    codigo: str
    descricao: str
    valor: float

class ImpostoDTO(BaseModel):
    codigo: str
    valor: float

class DebitosDTO(BaseModel):
    debitos: List[DebitoDTO]
    impostos: List[ImpostoDTO]

class SuspensaoDTO(BaseModel):
    codigo: str
    descricao: str
    valor: float

class DebitoSuspensoDTO(BaseModel):
    debito: DebitoDTO
    suspensoes: List[SuspensaoDTO]

class PeriodoApuracaoDTO(BaseModel):
    ano: int
    mes: int

class DadosIniciaisDTO(BaseModel):
    cnpj: str
    razao_social: str
    natureza_juridica: str
    situacao: str

class TelefoneResponsavelDTO(BaseModel):
    ddd: str
    numero: str

class RegistroCrcDTO(BaseModel):
    uf: str
    numero: str

class ResponsavelApuracaoDTO(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    telefone: TelefoneResponsavelDTO
    crc: Optional[RegistroCrcDTO] = None

class EmpresaDTO(BaseModel):
    cnpj: str
    razao_social: str
    natureza_juridica: str
    situacao: str

# --- DTO principal de entrada ---

class GenerateMitJsonInputDTO(BaseModel):
    empresa: EmpresaDTO
    periodo_apuracao: PeriodoApuracaoDTO
    dados_iniciais: DadosIniciaisDTO
    responsavel: ResponsavelApuracaoDTO
    debitos: Optional[List[DebitoDTO]] = []
    impostos: Optional[List[ImpostoDTO]] = []
    debitos_suspensos: Optional[List[DebitoSuspensoDTO]] = []
    # Adicione outros campos necessários para o MIT conforme o domínio

# --- DTO principal de saída ---

class GenerateMitJsonOutputDTO(BaseModel):
    mit_json: dict
    errors: Optional[List[str]] = None