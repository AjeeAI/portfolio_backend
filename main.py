import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import db
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import text
from dotenv import load_dotenv


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()



def send_email_to_admin(name, email, subject, message):
    admin_email = os.getenv("admin_email")
    admin_password = os.getenv("admin_email_password")  # Use App Password

    msg = MIMEMultipart()
    msg["From"] = admin_email
    msg["To"] = admin_email
    msg["Subject"] = f"New Portfolio Message: {subject}"

    body = f"""
    A new message has been sent from your portfolio site:

    Name: {name}
    Email: {email}
    Subject: {subject}

    Message:
    {message}
    """

    msg.attach(MIMEText(body, "plain"))

    # Gmail SMTP example
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(admin_email, admin_password)
        server.send_message(msg)




app = FastAPI(title="Portfolio Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # allow all headers (Authorization, Content-Type, etc.)
)

class Message(BaseModel):
    name: str = Field(..., example="Adesoji Ajijolaoluwa")
    email: str = Field(..., example="ajee@ai.com")
    subject: str = Field(..., example="Inquiry about your app development services")
    message: str = Field(..., example="Hello. I want to build a mobile app for my business existing website.")
   
@app.get("/")
def home():
    return "Welcome to my Portfolio Backend API" 

@app.post("/api/messages")

def send_message(message: Message):
    try:
        
        check_existing_message_query = text(
           """
           SELECT * FROM messages_table WHERE email = :email
           """
       )
        
        send_message_query = text(
            """
            INSERT INTO messages_table (name, email, subject, message)
            VALUES (:name, :email, :subject, :message)
            """
        )
        db.execute(
            send_message_query,
            {
                "name": message.name,
                "email": message.email,
                "subject": message.subject,
                "message": message.message
            }
        )
        
        db.commit()
        
         # NEW: Send email to admin
        send_email_to_admin(
            message.name,
            message.email,
            message.subject,
            message.message
        )

        return {"message": "Message sent successfully"}
    except HTTPException as e:
        raise e
    
@app.get("/api/messages")
def get_messages():
    try:
        get_Mesages_query = text(
            """
            SELECT * FROM messages_table
            
            """
        )
        
        result = db.execute(get_Mesages_query)
        if not result:
            return "No messages yet!"
        messages = result.mappings().fetchall()
        return messages
    
        
    except HTTPException as e:
        raise e
    
    
class Login(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="admin1234")
    
@app.post("/api/login")
def login(login: Login):
    try: 
        admin_username = os.getenv("admin_username")
        admin_password = os.getenv("admin_password")
        if login.username == admin_username and login.password == admin_password:
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
    except HTTPException as e:
        raise e
    