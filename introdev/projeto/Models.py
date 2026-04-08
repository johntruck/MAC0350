# Arquivo Models.py

from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class Meme(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    curtidas: int
    fonte: str
    imagem: bytes = Field(unique=True)


class MemeFavorito(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    link: str = Field(unique=True)
    usuarios: List["Usuario"] = Relationship(back_populates="meme_favorito")


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(unique=True)
    acertos: int
    bio: str
    meme_id: str = Field(foreign_key="memefavorito.id")
    meme_favorito: Optional["MemeFavorito"] = Relationship(back_populates="usuarios")
