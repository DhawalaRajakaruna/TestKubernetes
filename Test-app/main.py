from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from database import get_db, init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def read_root(db: AsyncSession = Depends(get_db)):

    try:
        print("==============================================")
        result = await db.execute(text("SELECT * FROM admins"))
        print("Database query executed successfully!")
    except Exception as e:
        print("Database query failed:")
        print(e)
        return HTMLResponse(content=f"<h1>Database error: {e}</h1>", status_code=500)

    
    admin = result.first()  # returns a tuple of columns
    
    if not admin:
        return HTMLResponse(content="<h1>No admins found in the database.</h1>", status_code=404)
    
    # assuming first column is id, second is username, third is password
    admin_username = admin[1]  # change index if your table structure is different
    
    return HTMLResponse(
        content=f"<h1>Welcome to the FastAPI application, {admin_username}! ..... You are So Dear</h1>",
        status_code=200
    )
