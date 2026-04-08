# Arquivo main.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])
# Monta a pasta "static" na rota "/static"
app.mount("/static", StaticFiles(directory="static"), name="static")

curtidas = 0


@app.get("/home", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"pagina": "/home  /pagina1", "curtidas": curtidas}
    )


@app.get("/home/jupiterweb", response_class=HTMLResponse)
async def pag1(request: Request):
    if not "HX-Request" in request.headers:
        return templates.TemplateResponse(
            request, "index.html", {"pagina": "/home/jupiterweb"}
        )
    return templates.TemplateResponse(request, "jupiterweb.html")


@app.get("/home/alan", response_class=HTMLResponse)
async def pag2(request: Request):
    if not "HX-Request" in request.headers:
        return templates.TemplateResponse(
            request, "index.html", {"pagina": "/home/alan"}
        )
    return templates.TemplateResponse(request, "alan-melhor.html")


@app.get("/home/curtidas", response_class=HTMLResponse)
async def pag1(request: Request):
    if not "HX-Request" in request.headers:
        return templates.TemplateResponse(
            request, "index.html", {"pagina": "/home/curtidas", "curtidas": curtidas}
        )
    return templates.TemplateResponse(request, "curtidas.html", {"curtidas": curtidas})


@app.post("/curtir")
async def curtir(request: Request):
    global curtidas
    curtidas += 1
    return curtidas


@app.delete("/curtir")
async def descurtir(request: Request):
    global curtidas
    curtidas = 0
    return curtidas


ctr = 0

@app.get("/alternar")
async def alterna(request: Request):
    global ctr
    ctr = (ctr + 1) % 3
    lista = [
        templates.TemplateResponse(
            request, "index.html", {"pagina": "/home/jupiterweb"}
        ),
        templates.TemplateResponse(request, "index.html", {"pagina": "/home/alan"}),
        templates.TemplateResponse(
            request,
            "index.html",
            {"pagina": "/home/curtidas", "curtidas": curtidas},
        )
    ]
    return lista[ctr]
