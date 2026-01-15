from fastapi import FastAPI
from api import router
from fastapi.staticfiles import StaticFiles
from models import init_db
import random 
import string   

def generateshortcode(length=6):   
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

app = FastAPI()
#initialize the database
init_db()
#mount the static files
app.include_router(router)
#mount the static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def default():
    return "Welcome to URL Shortner Microservice"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
