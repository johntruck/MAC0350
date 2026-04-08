# Arquivo main.py
from fastapi import Depends, HTTPException, status, Cookie, Response, FastAPI, Request
from typing import Annotated
from fastapi.responses import HTMLResponse
from typing import Any
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Sintaxe recomendada: diretório como primeiro argumento posicional
templates = Jinja2Templates(directory="templates")


class Usuario(BaseModel):
    username: str
    bio: str
    senha: str


class Login(BaseModel):
    username: str
    senha: str


# Nossa base de dados em memória
users_db = [
    {"username": "joão", "bio": "Professor de Python", "senha": "1234"},
    {"username": "maria", "bio": "Desenvolvedora Web", "senha": "asenha"},
]


@app.get("/")
async def envia_html(request: Request):
    return templates.TemplateResponse(request=request, name="home.html", context={})


@app.post("/users")
async def add_user(user: Usuario):
    users_db.append(user.dict())
    return {"usuario": user.username}


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})


# 1. Rota para "Logar" (Define o Cookie)
@app.post("/login")
def login(login: Login, response: Response):
    # Buscamos o usuário usando um laço simples
    username = login.username
    senha = login.senha
    usuario_encontrado = None
    for u in users_db:
        if u["username"] == username:
            usuario_encontrado = u
            break
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if senha != usuario_encontrado["senha"]:
        raise HTTPException(status_code=404, detail="Senha incorreta")

    # O servidor diz ao navegador: "Guarde esse nome no cookie 'session_user'"
    response.set_cookie(key="session_user", value=username)
    return {"message": "Logado com sucesso"}


# 2. A Dependência: Lendo o Cookie
def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    # O FastAPI busca automaticamente um cookie chamado 'session_user'
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado.",
        )

    user = next((u for u in users_db if u["username"] == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    return user


# 3. Rota Protegida
@app.get("/profile")
def show_profile(request: Request, user: dict = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"username": user["username"], "bio": user["bio"]},
    )
