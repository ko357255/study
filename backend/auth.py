from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext # ハッシュ化ツール
from jose import JWTError, jwt # JWTの作成・検証
from datetime import datetime, timedelta # トークンの有効期限
from dotenv import load_dotenv
import os


# .evn を読み込む
load_dotenv()

# Oauth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# JWTを暗号化する為の秘密鍵
key = os.getenv("SECRET_KEY")
if key is None:
    raise ValueError("SECRET_KEY is not set in environment variables")

SECRET_KEY: str = key

# 署名アルゴリズム
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# トークンの有効期限
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# パスワードとDBのハッシュ値を比べる
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# パスワードをハッシュ化する
def get_password_hash(password):
    return pwd_context.hash(password)

# JWTを発行する
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    # 有効期限
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # 有効期限を追加
    to_encode.update({"exp": expire})
    # jwtトークン文字列を生成
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 
def get_current_user(
    # Authorization ヘッダからトークンを取り出す
    token: str = Security(oauth2_scheme)
):
    try:
        # jwtトークンをデコード
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: no subject")
        return username
    except JWTError:
        # デコード失敗
        raise HTTPException(status_code=401, detail="Invalid token")