from fastapi import FastAPI, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from jsonschema import ValidationError
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Create FastAPI instance
app = FastAPI()

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    mobile_number = Column(String, index=True)
    whatsapp_number = Column(String, index=True)
    email = Column(String, index=True)
    locality = Column(String, index=True)
    classification = Column(String, index=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for request body
class UserData(BaseModel):
    name: str
    mobile_number: str
    whatsapp_number: str
    email: str
    locality: str
    classification: str = None

# Endpoint to submit user data
@app.post("/submit_user_data/")
async def submit_user_data(
    name: str = Form(...),
    mobile_number: str = Form(...),
    whatsapp_number: str = Form(...),
    email: str = Form(...),
    locality: str = Form(...),
):
    db = SessionLocal()
    try:
        user_data = UserData(name=name, mobile_number=mobile_number, whatsapp_number=whatsapp_number, email=email, locality=locality)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = user_data.dict()
    sql_query = text(
        """
        INSERT INTO users (name, mobile_number, whatsapp_number, email, locality, classification) 
        VALUES (:name, :mobile_number, :whatsapp_number, :email, :locality, :classification)
    """
    )
    db.execute(sql_query, data)
    db.commit()

    # Get the newly inserted user
    user = db.query(User).filter_by(email=email).first()

    return {"message": "User data submitted successfully!", "user_id": user.id}

# Endpoint to classify users
@app.post("/classify_users/")
async def classify_users(user_id: int = Form(...), classification: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id).first()
    user.classification = classification.upper()
    db.commit()
    return {"message": "User classification updated successfully!"}

# Home page with GUI
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head>
        <title>User Data Submission</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f2f2f2;
            }
            .container {
                width: 600px;
                margin: 50px auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
            }
            form {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            input[type="text"], select {
                width: calc(100% - 22px);
                padding: 10px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            input[type="submit"] {
                width: 100%;
                padding: 10px 0;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>User Data Submission</h1>
            <form id="user-form" action="/submit_user_data/" method="post">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required><br>
                <label for="mobile_number">Mobile Number:</label>
                <input type="text" id="mobile_number" name="mobile_number" required><br>
                <label for="whatsapp_number">WhatsApp Number:</label>
                <input type="text" id="whatsapp_number" name="whatsapp_number" required><br>
                <label for="email">Email:</label>
                <input type="text" id="email" name="email" required><br>
                <label for="locality">Locality:</label>
                <input type="text" id="locality" name="locality" required><br>
                <input type="submit" value="Submit">
            </form>
            <div id="classification-container" style="display: none;">
                <form id="classification-form" action="/classify_users/" method="post">
                    <input type="hidden" id="user_id" name="user_id">
                    <label for="classification">Classify User (A, B, C):</label>
                    <input type="text" id="classification" name="classification" required><br>
                    <input type="submit" value="Classify">
                </form>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
