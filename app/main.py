from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
from .models import Post as DBPost  
from .database import get_db, engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True

@app.get("/")
async def root():
    return {"message": "Hello World this is harsha"}

@app.get("/posts")
async def get_post(db: Session = Depends(get_db)):
    posts = db.query(DBPost).all()
    my_posts = []
    for post in posts:
        my_posts.append(post)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: PostCreate, db: Session = Depends(get_db)):
    new_post = DBPost(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}

@app.get("/posts/latest")
async def get_latest_post(db: Session = Depends(get_db)):
    latest_post = db.query(DBPost).order_by(DBPost.created_at.desc()).first()
    return {"latest_post": latest_post}

@app.get("/posts/{id}")
async def get_post(id: int, db: Session = Depends(get_db)):
    latestpost = db.query(DBPost).filter(DBPost.id == id).first()
    if not latestpost:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post_detail": latestpost}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    del_post = db.query(DBPost).filter(DBPost.id == id)
    if del_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    del_post.delete(synchronize_session=False)
    db.commit()
    return {"data": del_post.first()}

@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_post(id: int, post: PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(DBPost).filter(DBPost.id == id)
    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return {"data": post_query.first()}
