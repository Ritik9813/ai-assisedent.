import tkinter as tk
from tkinter import messagebox
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import random
import requests
from googleapiclient.discovery import build  # Import YouTube API
from PIL import Image, ImageTk

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# YouTube API setup
YOUTUBE_API_KEY = 'AIzaSyD3QhFwwASHsjK0MfsazB65pXo1DO_pzu4'  # Replace with your YouTube API key
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

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
    api_key = 'YOUR_API_KEY'  # Replace with your OpenWeatherMap API key
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
                speak(f" {song_name} on YouTube.")
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

    elif "bye" in query or "quit" in query:
        stop_assistant()

def stop_assistant():
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        speak("Goodbye!")
        root.quit()

# GUI setup
root = tk.Tk()
root.title("Voice Assistant")
root.geometry("500x400")
root.configure(bg="#C0C0C0")

# Load and display the image
mask_image = Image.open("a.jpg")  # Change the file name to your image
mask_image = mask_image.resize((500, 400), Image.LANCZOS)
mask_photo = ImageTk.PhotoImage(mask_image)

canvas = tk.Canvas(root, width=500, height=400)
canvas.create_image(0, 0, anchor=tk.NW, image=mask_photo)
canvas.pack()

# Command label for visual feedback
command_label = tk.Label(root, text="", bg="#C0C0C0", font=("Arial", 14))
command_label.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

def listen_command():
    command = take_command()
    if command:
        command_label.config(text=command)
        execute_query(command)
    root.after(1000, listen_command)

def animate_button(event):
    stop_button.config(relief="sunken", bg="#b0b0b0")

def reset_button(event):
    stop_button.config(relief="raised", bg="#d0d0d0")

stop_button = tk.Button(root, text="Stop Assistant", command=stop_assistant,
                         bg="#d0d0d0", relief="raised", padx=10, pady=5,
                         highlightbackground="#c0c0c0")
stop_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
stop_button.bind("<ButtonPress>", animate_button)
stop_button.bind("<ButtonRelease>", reset_button)

# Greet the user
speak("Hello, I am your voice assistant. How can I help you?")

# Start listening for commands
listen_command()

root.mainloop()
