from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TelefoneResponsavel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ddd: str = Field(..., alias="Ddd", min_length=2, max_length=2)
    num_telefone: str = Field(..., alias="NumTelefone", min_length=8, max_length=9)


class RegistroCrc(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uf_registro: str = Field(..., alias="UfRegistro", min_length=2, max_length=2)
    num_registro: str = Field(..., alias="NumRegistro")


class ResponsavelApuracao(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cpf: str = Field(..., alias="CpfResponsavel", min_length=11, max_length=11)
    tel_responsavel: Optional[TelefoneResponsavel] = Field(
        None, alias="TelResponsavel"
    )
    email_responsavel: Optional[str] = Field(
        None, alias="EmailResponsavel"
    )
    registro_crc: Optional[RegistroCrc] = Field(
        None, alias="RegistroCrc"
    )