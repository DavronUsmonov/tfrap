from textverified import TextVerified
from fastapi import FastAPI, Header, HTTPException
from dotenv import load_dotenv
import os
# Initialize client

load_dotenv()

client = TextVerified(
    api_key=os.getenv("TEXTVERIFIED_API_KEY"),
    api_username=os.getenv("TEXTVERIFIED_USERNAME"),

)

def get_account_details():
    """Get your current balance and username"""
    try:
        account_info = client.account.me()
        print(f"Username: {account_info.username}")
        print(f"Current balance: ${account_info.current_balance}")
        return account_info
    except Exception as e:
        print(f"Error getting account details: {e}")
        return None

def getRentalList():
    allRentals = client.reservations.list_nonrenewable()
    activeRentals = []
    for rental in allRentals: 
        if rental.state.value == "nonrenewableActive":
            activeRentals.append(rental)
    return activeRentals

app = FastAPI()

API_KEY = os.getenv("MY_API_KEY")

unusedRentals = getRentalList()
usedRentals = []


@app.post("/getNumber")
async def getNumber(x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    rental = unusedRentals.pop()
    usedRentals.append(rental)
    print(f"number requested: {rental.number}")
    return rental

@app.get("/getMessage")
async def getMessage(rental_id, x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    rental = client.reservations.nonrenewable_details(rental_id)
    print(f"scanning for messages on: {rental.number}")
    for sms in client.sms.incoming(rental,timeout=60):
        print(f"{rental.number} received: {sms.parsed_code}")
        return sms
    
@app.get("/getUnusedRentals")
async def getUnusedRentals(x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return unusedRentals

@app.get("/getUsedRentals")
async def getUsedRentals(x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return usedRentals