# Arquivo main.py

from fastapi import FastAPI, Request, Form, HTTPException, Response, Cookie, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, create_engine, Session, select, col, desc
from Models import Usuario, Meme, MemeFavorito
from pathlib import Path
from typing import Annotated
import base64
from contextlib import asynccontextmanager


@asynccontextmanager
async def initFunction(app: FastAPI):
    arquivo = Path("./memes.db")
    if arquivo.exists():
        arquivo.unlink()

    create_db_and_tables()
    yield


app = FastAPI(lifespan=initFunction)
app.mount("/Static", StaticFiles(directory="static"), name="static")

arquivo_sqlite = "memes.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])

# usado como referencia manual de qual imagem se refere a qual meme para construir o banco de dados inicial
dados_manuais = {
    "meme1.jpeg": [
        231,
        "https://www.reddit.com/r/MemesBR/comments/1sd55ky/mandem_uma_foto_aleat%C3%B3ria_da_galeria_de_voc%C3%AAs/?tl=en",
    ],
    "meme2.jpeg": [
        1000,
        "https://www.reddit.com/r/MemesBR/comments/1sbnlt3/eu_quero_virar_chad/?tl=en",
    ],
    "meme3.jpeg": [
        595,
        "https://www.reddit.com/r/MemesBR/comments/1sbr60z/nintendo_n%C3%A3o_%C3%A9_para_os_fracos/?tl=en",
    ],
    "meme4.jpeg": [
        230,
        "https://www.reddit.com/r/MemesBR/comments/1sbvgoq/kkkkkkk_vem_com_o_pai/?tl=en",
    ],
    "meme5.jpeg": [
        638,
        "https://www.reddit.com/r/MemesBR/comments/1s8mk0f/evento_can%C3%B4nico_da_inf%C3%A2ncia/?tl=en",
    ],
    "meme6.jpeg": [
        836,
        "https://www.reddit.com/r/MemesBR/comments/1s72vmq/primeiro_meme_que_j%C3%A1_fiz_ficou_uma_bosta/?tl=en",
    ],
    "meme7.jpeg": [
        82,
        "https://www.reddit.com/r/MemesBR/comments/1s5xx7o/gostaram_da_minha_nova_ma%C3%A7aneta/?tl=en",
    ],
    "meme8.jpeg": [
        7,
        "https://www.reddit.com/r/MemesBR/comments/1s5a1au/eita_gatinho/?tl=en",
    ],
    "meme9.jpeg": [
        1200,
        "https://www.reddit.com/r/MemesBR/comments/1n48aqb/qual_%C3%A9_o_melhor/?tl=en",
    ],
    "meme10.jpeg": [0, "matheus"],
}


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    for k in dados_manuais.keys():
        with Session(engine) as session:
            # monta o banco de dados dos memes pegando as imagens localmente e usando dados_manuais como referencia para saber as curtidas/fonte
            with open(f"./memes/{k}", "rb") as arquivo:
                imagem = arquivo.read()
                novo_meme = Meme(
                    imagem=imagem,
                    curtidas=dados_manuais.get(k)[0],
                    fonte=dados_manuais.get(k)[1],
                )
                session.add(novo_meme)
                session.commit()
                session.refresh(novo_meme)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


######################
# DA PARTE DOS MEMES #
######################


# envia a pagina inicial com os dois primeiros memes
@app.get("/start_memes", response_class=HTMLResponse)
async def start_memes(request: Request):
    with Session(engine) as session:
        query = select(Meme).where(Meme.id.in_([1, 2]))
        memes = session.exec(query).all()
        meme_img1 = base64.b64encode(memes[0].imagem).decode("utf-8")
        meme_img2 = base64.b64encode(memes[1].imagem).decode("utf-8")

    return templates.TemplateResponse(
        request,
        "container_memes.html",
        {
            "id1": 1,
            "id2": 2,
            "meme_id1": memes[0].id,
            "meme_id2": memes[1].id,
            "meme_img1": meme_img1,
            "meme_img2": meme_img2,
            "curtidas1": memes[0].curtidas,
            "curtidas2": memes[1].curtidas,
            "fonte1": memes[0].fonte,
            "fonte2": memes[1].fonte,
            "meme1": memes[0],
            "meme2": memes[1],
            "acertos": 0,
        },
    )


@app.get("/check-acerto", response_class=HTMLResponse)
def check_acerto(
    request: Request, meme_id1: int, meme_id2: int, escolhido: int, acertos: int
):
    color = "red"
    with Session(engine) as session:
        query1 = select(Meme).where(Meme.id == meme_id1)
        query2 = select(Meme).where(Meme.id == meme_id2)
        meme1 = session.exec(query1).first()
        meme2 = session.exec(query2).first()
        memes = [meme1, meme2]
        meme_img1 = base64.b64encode(memes[0].imagem).decode("utf-8")
        meme_img2 = base64.b64encode(memes[1].imagem).decode("utf-8")

        # para saber qual dos memes foi o escolhido
        idx_escolhido = 0
        idx_nescolhido = 1
        if escolhido != memes[0].id:
            idx_escolhido = 1
            idx_nescolhido = 0

        if memes[idx_escolhido].curtidas > memes[idx_nescolhido].curtidas:
            color = "green"
            acertos += 1

        return templates.TemplateResponse(
            request,
            "container_resultados.html",
            {
                "id1": meme1.id,
                "id2": meme2.id,
                "meme_id1": memes[0].id,
                "meme_id2": memes[1].id,
                "meme_img1": meme_img1,
                "meme_img2": meme_img2,
                "curtidas1": memes[0].curtidas,
                "curtidas2": memes[1].curtidas,
                "fonte1": memes[0].fonte,
                "fonte2": memes[1].fonte,
                "meme1": memes[0],
                "meme2": memes[1],
                "color": color,
                "escolhido": escolhido,
                "acertos": acertos,
            },
        )


# envia o proximo round de memes
@app.get("/proximo_round", response_class=HTMLResponse)
async def proximo_round(request: Request, meme_id1: int, meme_id2: int, acertos: int):
    # caso tenha acabado
    if meme_id2 > 10:
        return templates.TemplateResponse(
            request, "criar_user.html", {"acertos": acertos}
        )
    with Session(engine) as session:
        query1 = select(Meme).where(Meme.id == meme_id1)
        query2 = select(Meme).where(Meme.id == meme_id2)
        meme1 = session.exec(query1).first()
        meme2 = session.exec(query2).first()
        memes = [meme1, meme2]
        meme_img1 = base64.b64encode(memes[0].imagem).decode("utf-8")
        meme_img2 = base64.b64encode(memes[1].imagem).decode("utf-8")

        return templates.TemplateResponse(
            request,
            "container_memes.html",
            {
                "id1": meme1.id,
                "id2": meme2.id,
                "meme_id1": memes[0].id,
                "meme_id2": memes[1].id,
                "meme_img1": meme_img1,
                "meme_img2": meme_img2,
                "curtidas1": memes[0].curtidas,
                "curtidas2": memes[1].curtidas,
                "fonte1": memes[0].fonte,
                "fonte2": memes[1].fonte,
                "meme1": memes[0],
                "meme2": memes[1],
                "acertos": acertos,
            },
        )


#######################
# DA PARTE DO RANKING #
#######################


@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str | None = ""):

    # tem que retornar com a sessão ativa por causa do lazy loading do sqlmodel
    with Session(engine) as session:
        query = (
            select(Usuario)
            .where(col(Usuario.nome).contains(busca))
            .order_by(Usuario.acertos)
        )
        leaderboard = session.exec(query).all()

        return templates.TemplateResponse(
            request,
            "ranking.html",
            {
                "usuarios": leaderboard,
            },
        )


@app.post("/novoUsuario", response_class=HTMLResponse)
def criar_usuario(
    request: Request,
    response: Response,
    acertos: int,
    nome: str = Form(...),
    link: str = Form(...),
    bio: str = Form(...),
):

    with Session(engine) as session:
        query = select(MemeFavorito).where(MemeFavorito.link == link)
        meme = session.exec(query).first()

        # se o link do meme ainda n existe
        if not meme:
            meme = MemeFavorito(link=link)
            session.add(meme)

        novo_usuario = Usuario(
            nome=nome,
            acertos=acertos,
            bio=bio,
            meme_id=meme.id,
            meme_favorito=meme,
        )

        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)

        # cria o cookie do usuario para deletar/atualizar bio
        response = templates.TemplateResponse(request, "edicao.html")
        response.set_cookie(key="session_user", value=nome)

        return response


# gera a pagina de ranking
@app.get("/ranking", response_class=HTMLResponse)
async def ranking(request: Request):
    with Session(engine) as session:
        query = select(Usuario).order_by(desc(Usuario.acertos))
        leaderboard = session.exec(query).all()

        return templates.TemplateResponse(
            request, "ranking.html", {"usuarios": leaderboard}
        )


# deleta o usuario e envia para o ranking
@app.delete("/deletaUsuario", response_class=HTMLResponse)
def deletar_usuario(
    request: Request, session_user: Annotated[str | None, Cookie()] = None
):
    # se n eh o usuario correto
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado.",
        )

    with Session(engine) as session:
        query = select(Usuario).where(Usuario.nome == session_user)
        usuario = session.exec(query).first()
        session.delete(usuario)
        session.commit()

        query = select(Usuario).order_by(desc(Usuario.acertos))
        leaderboard = session.exec(query).all()
        return templates.TemplateResponse(
            request, "ranking.html", {"usuarios": leaderboard}
        )


# atualiza a bio e envia para o ranking
@app.put("/atualizaBio", response_class=HTMLResponse)
def atualizar_bio(
    request: Request,
    session_user: Annotated[str | None, Cookie()] = None,
    nova_bio: str = Form(...),
):

    # se n eh o usuario correto
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado.",
        )

    with Session(engine) as session:
        query = select(Usuario).where(Usuario.nome == session_user)
        usuario = session.exec(query).first()
        usuario.bio = nova_bio
        session.commit()
        session.refresh(usuario)

        query = select(Usuario).order_by(desc(Usuario.acertos))
        leaderboard = session.exec(query).all()
        return templates.TemplateResponse(
            request, "ranking.html", {"usuarios": leaderboard}
        )
