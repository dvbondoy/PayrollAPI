from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def test_hash():
    password = "123"
    hashed_password = hash(password)
    assert verify(password, hashed_password) == True

def test_wrong_password():
    password = "123"
    wrong_password = "1234"
    hashed_password = hash(password)
    assert verify(wrong_password, hashed_password) == False