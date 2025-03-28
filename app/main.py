from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get('/')
async def index():
    return {'message': 'Base API file'}

if __name__ == '__main__':
    uvicorn.run('main:app', debug=True)