
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    toilet_id = Column(String, index=True)
    rating = Column(Integer)
    cleanliness = Column(Integer)
    accessibility = Column(Integer)
    baby_changing = Column(Integer)
    comment = Column(String)


class CustomToilet(Base):
    __tablename__ = "custom_toilets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lat = Column(Float)
    lon = Column(Float)

Base.metadata.create_all(bind=engine)


class ReviewCreate(BaseModel):
    toilet_id: str
    rating: int
    cleanliness: int
    accessibility: int
    baby_changing: int
    comment: str = ""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/reviews")
def post_review(review: ReviewCreate, db: Session = Depends(get_db)):
    db_review = Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return {"message": "Review submitted successfully"}

@app.get("/reviews")
def get_reviews(toilet_id: str, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.toilet_id == toilet_id).all()

@app.get("/summary")
def get_summary(toilet_id: str, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.toilet_id == toilet_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found")
    summary = {
        "average_rating": sum(r.rating for r in reviews) / len(reviews),
        "cleanliness": sum(r.cleanliness for r in reviews) / len(reviews),
        "accessibility": sum(r.accessibility for r in reviews) / len(reviews),
        "baby_changing": sum(r.baby_changing for r in reviews) / len(reviews)
    }
    return summary


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

from fastapi import Body

class CustomToiletCreate(BaseModel):
    name: str
    lat: float
    lon: float

@app.post("/custom-toilets")
def create_custom_toilet(toilet: CustomToiletCreate, db: Session = Depends(get_db)):
    new_toilet = CustomToilet(**toilet.dict())
    db.add(new_toilet)
    db.commit()
    db.refresh(new_toilet)
    return new_toilet

@app.get("/custom-toilets")
def get_custom_toilets(db: Session = Depends(get_db)):
    return db.query(CustomToilet).all()
