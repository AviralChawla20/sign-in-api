from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext

app = FastAPI()

# CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DATABASE_URL = "mysql+mysqlconnector://sql12647981:XM51KVKzDA@sql12.freemysqlhosting.net:3306/sql12647981"
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, index=True)
    password = Column(String)  # Assuming the column is named "password"


# SQLAlchemy database engine and session setup
DATABASE_URL = "mysql+mysqlconnector://sql12647981:XM51KVKzDA@sql12.freemysqlhosting.net:3306/sql12647981"

engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # Adjust as needed
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Pydantic model for request validation
class UserInDB(BaseModel):
    email: str
    password: str


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/signin")
async def signin(user: UserInDB, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user is None or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return {"message": "Signin successful"}


if __name__ == "__main__":
    import uvicorn

    # Run the application using Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
