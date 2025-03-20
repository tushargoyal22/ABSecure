from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

new_password = "1234"  # Or whatever password you want
hashed_password = pwd_context.hash(new_password)

print("New Hashed Password:", hashed_password)
