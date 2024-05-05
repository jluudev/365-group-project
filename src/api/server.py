from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware

from src.api import dungeon, hero, monster, world, guild

description = """
Some description.
"""

app = FastAPI(
    title="Arthur's Last Crusade",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Jessica Luu, Jenna Chan, Jeffer Ng, Austin Tepe",
        "email": "jluu27@calpoly.edu",
    },
)

app.include_router(world.router)
app.include_router(dungeon.router)
app.include_router(hero.router)
app.include_router(monster.router)
app.include_router(guild.router)


@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "This is the web service of Arthur's Last Crusade"}