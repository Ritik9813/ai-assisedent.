import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import requests
from googleapiclient.discovery import build
from twilio.rest import Client
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# YouTube API setup
YOUTUBE_API_KEY = 'AIzaSyD3QhFwwASHsjK0MfsazB65pXo1DO_pzu4'
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Twilio configuration
TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        query = r.recognize_google(audio, language='en-in')
        return query.lower()
    except Exception:
        return None

def get_weather(city):
    api_key = '932344d60f9905531e0eeb39274e9bbe'
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(base_url)
    data = response.json()
    if data['cod'] == '404':
        return "City not found. Please try again."
    else:
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is {weather_description}. The temperature is {temperature}°C."

def search_youtube(query):
    request = youtube.search().list(
        part='id,snippet',
        q=query,
        maxResults=1,
        type='video'
    )
    response = request.execute()
    return response['items'][0]['id']['videoId'] if response['items'] else None

def send_whatsapp_message(message, recipient_number):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:+91{recipient_number}'
        )
        speak("Message sent successfully!")
    except Exception as e:
        speak("Failed to send the message.")
        print(e)

def execute_query(query):
    if 'wikipedia' in query:
        query = query.replace("wikipedia", "")
        results = wikipedia.summary(query, sentences=2)
        speak(results)

    elif 'open youtube' in query:
        webbrowser.open("youtube.com")
        speak("Opening YouTube...")

    elif 'open google' in query:
        webbrowser.open("google.com")
        speak("Opening Google...")

    elif 'search' in query:
        query = query.replace("search", "")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak(f"Searching Google for: {query}")

    elif 'play music' in query or 'play' in query:
        song_name = query.replace("play", "").strip()
        if song_name:
            video_id = search_youtube(song_name)
            if video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"
                webbrowser.open(url)
                speak(f"Playing {song_name} on YouTube.")
            else:
                speak("I couldn't find any song with that name.")
        else:
            speak("Please specify the song you want to play.")

    elif 'the time' in query:
        str_time = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {str_time}")

    elif 'temperature' in query:
        speak("Please specify the city name.")
        city = take_command()
        if city:
            weather_info = get_weather(city)
            speak(weather_info)

    elif 'send whatsapp message' in query:
        query = query.replace("send whatsapp message", "").strip()
        speak("Please tell me the recipient's number.")
        recipient_number = take_command()
        if recipient_number:
            speak("What message would you like to send?")
            message = take_command()
            if message:
                send_whatsapp_message(message, recipient_number)
            else:
                speak("I didn't catch that. Please repeat the message.")
                
    elif "bye" in query or "quit" in query:
        speak("Goodbye!")
        exit()

def start_assistant():
    speak("Hello, I am your voice assistant. How can I help you?")
    while True:
        command = take_command()
        if command:
            execute_query(command)

# Video Player GUI
class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("voice assistant")

        # Create a canvas to display the video
        self.canvas = tk.Canvas(root, width=640, height=480)
        self.canvas.pack()

        # Load the video file directly
        self.video_path = "C:/Users/ritik/Downloads/stable--4-2025-02-14T13_36_38Z (1).mp4"  # Replace with your video file path
        self.video = cv2.VideoCapture(self.video_path)

        # Start playing the video
        self.play_video()

    def play_video(self):
        ret, frame = self.video.read()
        if ret:
            # Convert the frame to RGB and resize it
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            self.video_frame = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.video_frame)
            self.root.after(30, self.play_video)  # Update every 30ms
        else:
            # Loop the video when it ends
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.play_video()

# Main Application
if __name__ == "__main__":
    root = tk.Tk()

    # Start the Video Player GUI
    video_player = VideoPlayer(root)

    # Start the voice assistant in a separate thread
    import threading
    assistant_thread = threading.Thread(target=start_assistant)
    assistant_thread.daemon = True  # Daemonize thread to exit when the main program exits
    assistant_thread.start()

    # Start the Tkinter main loop
    root.mainloop()