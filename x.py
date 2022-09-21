from fastapi import FastAPI, Request, Response, Form, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from flags import flag1, flag2
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


coins = {}

coins["brad"] = 100

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session_token: str = Cookie("Sign in")):
    return templates.TemplateResponse("power.html", {"request": request, "username": session_token, "coins": coins.get(session_token, 0), "users": coins})

@app.post("/donate")
async def donate(request: Request, username: str = Form(...), amount: int = Form(...), session_token: str = Cookie("Sign in")):
    flag = False
    if username in coins:
        coins_to_donate = min(amount, coins[session_token])
        coins[username] += coins_to_donate
        coins[session_token] -= coins_to_donate

    if coins[session_token] > 100:
        flag = flag1

    return templates.TemplateResponse("power.html", {"request": request, "username": session_token, "coins": coins[session_token], "users": coins, "flag": flag})

@app.post("/login")
async def login(request: Request, response: Response, username: str = Form(...),  ):
    flag = False
    if username not in coins:
        coins[username] = 10
    
    if coins[username] >= 100:
        flag = flag2

    response = templates.TemplateResponse("power.html", {"request": request, "response": response, "username": username, "coins": coins[username], "users": coins, "flag": flag})
    response.set_cookie(key="session_token", value=username, httponly=True)
    return response

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)