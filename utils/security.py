from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hash_password(password: str):
    return pwd_context.hash(password)

#密码验证，返回布尔值
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)