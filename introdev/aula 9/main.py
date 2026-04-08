# Arquivo main.py

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from Models import Aluno
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select, col
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=initFunction)
app.mount("/Static", StaticFiles(directory="static"), name="static")

arquivo_sqlite = "HTMX2.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def buscar_alunos(busca):
    with Session(engine) as session:
        query = select(Aluno).where(col(Aluno.nome).contains(busca)).order_by(Aluno.id)
        return session.exec(query).all()


@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str | None = "", num_pag: int = 1):
    alunos = buscar_alunos(busca)
    max = 1
    if (len(alunos)%10 == 0 and len(alunos) != 0):
        max = len(alunos)/10
    elif (len(alunos) != 0):
        max = len(alunos)//10 + 1
        
    inf = 10 * (num_pag - 1)
    sup = 10 * num_pag
        
    return templates.TemplateResponse(
        request,
        "lista.html",
        {
            "alunos": alunos[inf : sup],
            "num_pag": num_pag,
            "max": max
        },
    )


@app.get("/busca", response_class=HTMLResponse)
def busca(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/editarAlunos")
def novoAluno(request: Request):
    return templates.TemplateResponse(request, "options.html")


@app.post("/novoAluno", response_class=HTMLResponse)
def criar_aluno(nome: str = Form(...)):
    with Session(engine) as session:
        novo_aluno = Aluno(nome=nome)
        session.add(novo_aluno)
        session.commit()
        session.refresh(novo_aluno)
        return HTMLResponse(
            content=f"<p>O(a) aluno(a) {novo_aluno.nome} foi registrado(a)!</p>"
        )


@app.delete("/deletaAluno", response_class=HTMLResponse)
def deletar_aluno(id: int):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if not aluno:
            raise HTTPException(404, "Aluno não encontrado")
        session.delete(aluno)
        session.commit()
        return HTMLResponse(
            content=f"<p>O(a) aluno(a) {aluno.nome} foi deletado(a)!</p>"
        )


@app.put("/atualizaAluno", response_class=HTMLResponse)
def atualizar_aluno(id: int = Form(...), novoNome: str = Form(...)):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if not aluno:
            raise HTTPException(404, "Aluno não encontrado")
        nomeAntigo = aluno.nome
        aluno.nome = novoNome
        session.commit()
        session.refresh(aluno)
        return HTMLResponse(
            content=f"<p>O(a) aluno(a) {nomeAntigo} foi atualizado(a) para {aluno.nome}!</p>"
        )


@app.delete("/apagar", response_class=HTMLResponse)
def apagar():
    return ""
