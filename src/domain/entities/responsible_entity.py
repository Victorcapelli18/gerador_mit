from pydantic import BaseModel, Field



class TelefoneResponsavel(BaseModel):
    ddd: str = Field(..., min_length=2, max_length=2)
    num_telefone: str = Field(..., min_length=8, max_length=9)

class RegistroCrc(BaseModel):
    uf_registro: str = Field(..., min_length=2, max_length=2)
    num_registro: str = Field(...)

class ResponsavelApuracao(BaseModel):
    cpf: str
    tel_responsavel: TelefoneResponsavel | None = None
    email_responsavel: str | None = None
    registro_crc: RegistroCrc | None = None