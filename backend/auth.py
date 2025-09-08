from passlib.context import CryptContext # ハッシュ化ツール
from jose import JWTError, jwt # JWTの作成・検証
from datetime import datetime, timedelta # トークンの有効期限

# JWTを暗号化する為の秘密鍵
SECRET_KEY = "your-secret-key"
# 署名アルゴリズム
ALGORITHM = "HS256"
# トークンの有効期限
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

