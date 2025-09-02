from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, SessionLocal
from models import Item

# テーブル作成
Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS（フロントから呼べるようにする）---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.jsのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydanticスキーマ
class ItemCreate(BaseModel):
    name: str
    price: int

# DBセッション
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
# ヘルスチェック
@app.get('/')
def root():
    return {'message': 'Hello World'}

# アイテム追加
@app.post('/item')
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get('/items')
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
    