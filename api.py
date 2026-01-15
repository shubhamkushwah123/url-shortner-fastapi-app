from fastapi import APIRouter
from fastapi import Query
from typing import Optional
import main
import models
router = APIRouter()

# Specific routes first (more specific paths)
@router.post("/shortenURL")
def shorten_url(url: str = Query(...)):
    short_code = main.generateshortcode()
    models.insert_url(url, short_code)
    return {"short_code": short_code}

# get all urls
@router.get("/getAllUrls")
def getAllUrls():
    return models.getAllUrls()

#delete url
@router.delete("/deleteUrl/{short_url}")
def deleteUrl(short_url: str):
    return models.deleteUrl(short_url)

# Short code redirect route (must be last)
@router.get("/s/{shortURL}")
def get_url(shortURL: str):
    return models.get_url(shortURL)
   