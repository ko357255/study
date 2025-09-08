from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, SessionLocal
from models import Item, User
from auth import get_password_hash, verify_password, create_access_token

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

class UserCreate(BaseModel):
    username: str
    password: str

class LoginForm(BaseModel):
    username: str
    password: str

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

# ユーザー登録
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 既に同じユーザーが存在するか確認
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # ハッシュ化して保存
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

# ログイン
@app.post("/login")
def login(form: LoginForm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    # ユーザーが存在しない or パスワードが一致しない
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # トークンを生成
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}