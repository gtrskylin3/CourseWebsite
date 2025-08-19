import bcrypt

def hash_pw(password: str, rounds: int = 12) -> str:
    byte_password = str.encode(password)
    hashed = bcrypt.hashpw(password=byte_password, salt=bcrypt.gensalt(rounds))
    return hashed.decode("utf-8")


def check_pw(password: str, hashed_pw: str) -> bool:
    byte_password = str.encode(password)
    return bcrypt.checkpw(password=byte_password, hashed_password=hashed_pw.encode("utf-8"))
