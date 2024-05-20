from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import gspread
import pytz

app = FastAPI()

# Get current date and time
def get_current_datetime():
    current_datetime = datetime.now(pytz.timezone('Asia/Kolkata'))  # Convert server time to IST
    current_date = current_datetime.date()
    current_time = current_datetime.strftime("%I:%M %p")
    return current_date, current_time

# Update Google Sheet with user data
def update_google_sheet(user_data):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "/etc/secrets/service_accounts.json", scope
    )
    gc = gspread.authorize(credentials)
    sh = gc.open("Manohar")  # Replace with your Google Sheet name
    worksheet = sh.get_worksheet(0)
      # Clear existing data
    worksheet.append_rows(user_data.values.tolist())  # Append new data

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    current_date, current_time = get_current_datetime()
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shopkeeper Messaging Portal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                font-size: 18px;
            }
            h1 {
                font-size: 36px;
                color: #333;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            input[type="text"], select {
                width: 100%;
                padding: 10px;
                font-size: 18px;
                margin-bottom: 15px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            input[type="submit"] {
                width: 100%;
                padding: 10px;
                font-size: 20px;
                background-color: #007bff;
                color: #fff;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Shopkeeper Messaging Portal</h1>
            <p>Today's Date: """ + str(current_date) + """</p>
            <p>Current Time: """ + str(current_time) + """</p>

            <form action="/classify" method="post">
                <h2>User Information</h2>
                <input type="text" name="name" placeholder="Name"><br>
                <input type="text" name="mobile_number" placeholder="Mobile Number"><br>
                <input type="text" name="whatsapp_number" placeholder="WhatsApp Number"><br>
                <input type="text" name="email" placeholder="Email"><br>
                <input type="text" name="locality" placeholder="Locality"><br>
                <input type="submit" value="Submit">
            </form>
        </div>
    </body>
    </html>
    """

# Classification page
@app.post("/classify", response_class=HTMLResponse)
async def classify(request: Request, name: str = Form(...), mobile_number: str = Form(...), whatsapp_number: str = Form(...), email: str = Form(...), locality: str = Form(...)):
    current_date, current_time = get_current_datetime()
    user_data = pd.DataFrame({
        "Name": [name],
        "Mobile Number": [mobile_number],
        "WhatsApp Number": [whatsapp_number],
        "Email": [email],
        "Locality": [locality]
    })
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shopkeeper Messaging Portal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                font-size: 18px;
            }
            h1 {
                font-size: 36px;
                color: #333;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            input[type="text"], select {
                width: 100%;
                padding: 10px;
                font-size: 18px;
                margin-bottom: 15px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            input[type="submit"] {
                width: 100%;
                padding: 10px;
                font-size: 20px;
                background-color: #007bff;
                color: #fff;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Shopkeeper Messaging Portal</h1>
            <p>Today's Date: """ + str(current_date) + """</p>
            <p>Current Time: """ + str(current_time) + """</p>
            <h2>Classify User</h2>
            <p>Please classify the user:</p>
            <form action="/" method="post">
                <input type="hidden" name="name" value='""" + name + """'>
                <input type="hidden" name="mobile_number" value='""" + mobile_number + """'>
                <input type="hidden" name="whatsapp_number" value='""" + whatsapp_number + """'>
                <input type="hidden" name="email" value='""" + email + """'>
                <input type="hidden" name="locality" value='""" + locality + """'>
                <select name="classification">
                    <option value="A">A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                </select><br><br>
                <input type="submit" value="Submit">
            </form>
        </div>
    </body>
    </html>
    """

# Process final form submission
@app.post("/", response_class=HTMLResponse)
async def submit_form(request: Request, name: str = Form(...), mobile_number: str = Form(...), whatsapp_number: str = Form(...), email: str = Form(...), locality: str = Form(...), classification: str = Form(...)):
    current_date, current_time = get_current_datetime()
    user_data = pd.DataFrame({
        "Name": [name],
        "Mobile Number": [mobile_number],
        "WhatsApp Number": [whatsapp_number],
        "Email": [email],
        "Locality": [locality],
        "Classification": [classification]
    })
    update_google_sheet(user_data)
    return RedirectResponse(url="/", status_code=303)
