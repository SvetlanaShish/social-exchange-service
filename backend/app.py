from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from passlib.context import CryptContext
from database.model import TokenData, UserCreate, UserDB, UserUpdate, Product, Token 
from database.connection import initialize_ravendb


app = FastAPI()

# Configure security
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/")
def read_root():
    return {"resp": "Hello, world!"}

# Dependency to get the current user
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return TokenData(username=token)

# Create a new user
def create_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    new_user = UserDB(**user.dict(), hashed_password=hashed_password)
    with initialize_ravendb().open_session() as db_session:
        db_session.store(new_user)
        db_session.save_changes()
    return new_user

# Get user by username
def get_user(username: str):
    with initialize_ravendb().open_session() as db_session:
        return db_session.query(UserDB).where_equals("username", username).first()

# Get user by ID
def get_user_by_id(user_id: str):
    with initialize_ravendb().open_session() as db_session:
        return db_session.load(UserDB, user_id)

# Update user
def update_user(user_id: str, user: UserUpdate):
    with initialize_ravendb().open_session() as db_session:
        stored_user = db_session.load(UserDB, user_id)
        stored_user.username = user.username
        stored_user.hashed_password = pwd_context.hash(user.password)
        db_session.save_changes()
    return stored_user

# Get user products
def get_user_products(user_id: str):
    with initialize_ravendb().open_session()  as db_session:
        user = db_session.load(UserDB, user_id)
    return user.products

# Create user product
def create_user_product(user_id: str, product: Product):
    with initialize_ravendb().open_session()  as db_session:
        user = db_session.load(UserDB, user_id)
        user.products.append(product)
        db_session.save_changes()
    return user.products

# Token endpoint for user login
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user.username, "token_type": "bearer"}

# Create a new user
@app.post("/users/", response_model=UserDB)
def create_user_route(user: UserCreate):
    # db_user = get_user(user.username)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(user)

# Get current user
@app.get("/users/me", response_model=UserDB)
def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return current_user

# Update current user
@app.put("/users/me", response_model=UserDB)
def update_user_me(user: UserUpdate, current_user: UserDB = Depends(get_current_user)):
    return update_user(current_user.id, user)

# Get user's products
@app.get("/users/me/products", response_model=List[Product])
def read_user_products(current_user: UserDB = Depends(get_current_user)):
    return get_user_products(current_user.id)

# Create user product
@app.post("/users/me/products", response_model=List[Product])
def create_user_product_route(product: Product, current_user: UserDB = Depends(get_current_user)):
    return create_user_product(current_user.id, product)