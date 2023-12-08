import pyttsx3
import requests
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from base64 import urlsafe_b64decode
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from movie_checker import movie_check

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
API_KEY = os.getenv("API_KEY")

#Setup voice
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 150)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def speak_time(input):
    sentence = ""
    pattern = r"([0-9]+):([0-9]+)"
    matches = re.match(pattern, input)
    hour = int(matches.group(1))
    match hour:
        case 1: 
            sentence += "one"
        case 2:
            sentence += "two"
        case 3: 
            sentence += "three"
        case 4:
            sentence += "four"
        case 5: 
            sentence += "five"
        case 6:
            sentence += "six"
        case 7: 
            sentence += "seven"
        case 8:
            sentence += "eight"
        case 9: 
            sentence += "nine"
        case 10:
            sentence += "ten"
        case 11: 
            sentence += "11"
        case 12:
            sentence += "twelve"

    sentence += " "
    sentence += matches.group(2)
    if input.endswith("a"):
        sentence += " a m"
    else:
        sentence += " p m"
    


    return sentence


    

def weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric".format(city, API_KEY)
    resi = requests.get(url)
    data = resi.json()
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]

    speak("The Temp is: {} degrees celcius".format(temp))
    speak("Current Weather is: {} ".format(desc))

def movies():
    theater = movie_check(52241)
    speak("The movies at the closest theater near you at")
    speak(theater.name)

    for m in theater.movies:
        if not m.showings:
            continue
        speak(m.title)
        for time in m.showings:
            speak(speak_time(time))

def email_part_reader(parts):
    pattern = r"[Dd]eal.*(50%)+"
    
    if parts:
        for part in parts:
            if type(part) != dict:
                continue
            mimeType = part.get("mimeType")
            if part.get("parts"):
                email_part_reader(part)

            if mimeType == "text/plain":
                body = part.get("body")
                data = body.get("data")
                text = urlsafe_b64decode(data).decode()
                if re.search(pattern, text, re.M):
                    print(text)

            elif mimeType == "text/html":
                body = part.get("body")
                data = body.get("data")
                content = BeautifulSoup(urlsafe_b64decode(data), "html.parser")
                text = content.get_text()
                if re.search(pattern, text, re.M):
                    print(text)

            


def email_search():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=5).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found")
            return
        
        print("Messages:")
        
        for message in messages:
            try:
                msg_results = service.users().messages().get(userId="me", id=message["id"], format="full").execute()
                payload = msg_results["payload"]
                parts = payload.get("parts")
                email_part_reader(parts)
     
            except HttpError as error:
                print(f"An error occured: {error}")
            
    except HttpError as error:
        print(f"An error occured: {error}")


def main():
    weather("coralville")
    


    


if __name__ == "__main__":
    main()