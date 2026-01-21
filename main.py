# import os
# import threading
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field, EmailStr
# from sqlalchemy import text
# from database import db 
# from dotenv import load_dotenv
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # Load environment variables
# load_dotenv()

# # --- Email sending function ---
# def send_email_to_admin(name: str, email: str, subject: str, message: str):
#     """
#     Sends an email to the admin when a new message is received.
#     Uses Gmail SMTP with TLS and App Password.
#     """
#     try:
#         admin_email = os.getenv("admin_email")
#         admin_password = os.getenv("admin_email_password")  # App Password

#         msg = MIMEMultipart()
#         msg["From"] = admin_email
#         msg["To"] = admin_email
#         msg["Subject"] = f"New Portfolio Message: {subject}"

#         body = f"""
# A new message has been sent from your portfolio site:

# Name: {name}
# Email: {email}
# Subject: {subject}

# Message:
# {message}
# """
#         msg.attach(MIMEText(body, "plain"))

#         # Connect to Gmail SMTP
#         with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
#             server.starttls()
#             server.login(admin_email, admin_password)
#             server.send_message(msg)

#         print(f"Email sent successfully for message from {email}")

#     except smtplib.SMTPAuthenticationError:
#         print("SMTP Authentication Error: Check your App Password or email")
#     except smtplib.SMTPConnectError:
#         print("SMTP Connect Error: Could not connect to Gmail SMTP server")
#     except Exception as e:
#         print("Unexpected error while sending email:", e)


# # --- FastAPI app ---
# app = FastAPI(title="Portfolio Backend API", version="1.0.0")

# # --- CORS configuration ---
# origins = ["https://portfolio-8ce12.web.app",
#            "https://portfolio-dashboard-afc4a.web.app",
#            "http://localhost:5173"
#            ] 

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Pydantic models ---
# class Message(BaseModel):
#     name: str = Field(..., example="Adesoji Ajijolaoluwa")
#     email: EmailStr = Field(..., example="ajee@ai.com")
#     subject: str = Field(..., example="Inquiry about your app development services")
#     message: str = Field(..., example="Hello. I want to build a mobile app for my business existing website.")

# class Login(BaseModel):
#     username: str = Field(..., example="admin")
#     password: str = Field(..., example="admin1234")


# # --- Routes ---
# @app.get("/")
# def home():
#     return {"message": "Welcome to my Portfolio Backend API"}


# @app.post("/api/messages")
# def send_message(message: Message):
#     """
#     Save message to DB and notify admin via email (async).
#     Uses rollback on DB errors.
#     """
#     try:
        
#         send_message_query = text(
#             "INSERT INTO messages_table (name, email, subject, message) VALUES (:name, :email, :subject, :message)"
#         )
#         try:
#             db.execute(send_message_query, message.dict())
#             db.commit()
#         except Exception as db_error:
#             db.rollback()  
#             print("Database error:", db_error)
#             raise HTTPException(status_code=500, detail="Database error occurred")

#         # --- Send email asynchronously ---
#         threading.Thread(target=send_email_to_admin, args=(
#             message.name,
#             message.email,
#             message.subject,
#             message.message
#         )).start()

#         return {"message": "Message sent successfully"}

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         print("Unexpected error in send_message endpoint:", e)
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# @app.get("/api/messages")
# def get_messages():
#     """
#     Retrieve all messages from the database.
#     Handles rollback on errors.
#     """
#     try:
#         get_messages_query = text("SELECT * FROM messages_table")
#         try:
#             result = db.execute(get_messages_query)
#             messages = result.mappings().fetchall()
#         except Exception as db_error:
#             db.rollback()
#             print("Database error:", db_error)
#             raise HTTPException(status_code=500, detail="Database error occurred")

#         if not messages:
#             return {"message": "No messages yet!"}

#         return messages

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         print("Unexpected error in get_messages endpoint:", e)
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# @app.post("/api/login")
# def login(login: Login):
#     """
#     Admin login endpoint using environment variables.
#     """
#     try:
#         admin_username = os.getenv("admin_username")
#         admin_password = os.getenv("admin_password")

#         if login.username == admin_username and login.password == admin_password:
#             return {"message": "Login successful"}
#         else:
#             raise HTTPException(status_code=401, detail="Invalid credentials")

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         print("Unexpected error in login endpoint:", e)
#         raise HTTPException(status_code=500, detail="Internal Server Error")


import os
# import threading  <-- Removed this
from fastapi import FastAPI, HTTPException, BackgroundTasks # <-- Added BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import text
from database import db 
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import resend

# Load environment variables
load_dotenv()

# --- Email sending function (Unchanged) ---
def send_email_to_admin(name: str, email: str, subject: str, message: str):
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        
        r = resend.Emails.send({
            # MUST be a verified domain or the testing domain
            "from": "onboarding@resend.dev", 
            
            # This is the magic: When you click reply, it goes to the user's email
            "reply_to": email, 
            
            "to": os.getenv("admin_email"),
            "subject": f"New Portfolio Message: {subject}",
            "html": f"""
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Message:</strong><br>{message}</p>
            """
        })
        print("Email sent via API!", r)
    except Exception as e:
        print("API Error:", e)

# --- FastAPI app ---
app = FastAPI(title="Portfolio Backend API", version="1.0.0")

# --- CORS configuration ---
origins = ["https://portfolio-8ce12.web.app",
           "https://portfolio-dashboard-afc4a.web.app",
           "http://localhost:5173"
           ] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic models ---
class Message(BaseModel):
    name: str = Field(..., example="Adesoji Ajijolaoluwa")
    email: EmailStr = Field(..., example="ajee@ai.com")
    subject: str = Field(..., example="Inquiry about your app development services")
    message: str = Field(..., example="Hello. I want to build a mobile app for my business existing website.")

class Login(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="admin1234")


# --- Routes ---
@app.get("/")
def home():
    return {"message": "Welcome to my Portfolio Backend API"}


@app.post("/api/messages")
def send_message(message: Message, background_tasks: BackgroundTasks): # <-- Added parameter
    """
    Save message to DB and notify admin via email (using BackgroundTasks).
    """
    try:
        
        send_message_query = text(
            "INSERT INTO messages_table (name, email, subject, message) VALUES (:name, :email, :subject, :message)"
        )
        try:
            db.execute(send_message_query, message.dict())
            db.commit()
        except Exception as db_error:
            db.rollback()  
            print("Database error:", db_error)
            raise HTTPException(status_code=500, detail="Database error occurred")

        # --- Send email via BackgroundTasks ---
        # This schedules the function to run immediately after the response is sent
        background_tasks.add_task(
            send_email_to_admin, 
            message.name, 
            message.email, 
            message.subject, 
            message.message
        )

        return {"message": "Message sent successfully"}

    except HTTPException as he:
        raise he
    except Exception as e:
        print("Unexpected error in send_message endpoint:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/messages")
def get_messages():
    """
    Retrieve all messages from the database.
    """
    try:
        get_messages_query = text("SELECT * FROM messages_table")
        try:
            result = db.execute(get_messages_query)
            messages = result.mappings().fetchall()
        except Exception as db_error:
            db.rollback()
            print("Database error:", db_error)
            raise HTTPException(status_code=500, detail="Database error occurred")

        if not messages:
            return {"message": "No messages yet!"}

        return messages

    except HTTPException as he:
        raise he
    except Exception as e:
        print("Unexpected error in get_messages endpoint:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/login")
def login(login: Login):
    """
    Admin login endpoint using environment variables.
    """
    try:
        admin_username = os.getenv("admin_username")
        admin_password = os.getenv("admin_password")

        if login.username == admin_username and login.password == admin_password:
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except HTTPException as he:
        raise he
    except Exception as e:
        print("Unexpected error in login endpoint:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")