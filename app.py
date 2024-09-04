from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests


# Load responses from file
def load_responses():
    responses = {}
    file_path = os.path.join(os.path.dirname(__file__), 'responses.txt')
    with open(file_path, 'r') as file:
        current_category = None
        for line in file:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_category = line[1:-1]
                responses[current_category] = []
            elif current_category and line:
                responses[current_category].append(line)
    return responses


# Load the responses once
responses_data = load_responses()


# Serve the index.html when the root URL is accessed
@app.route('/')
def index():
    return render_template('index.html')


# Define the /chat route to handle POST requests
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the message from the request
        data = request.json
        message = data.get('message')

        # Log the received message for debugging
        print(f"Received message: {message}")

        # Check if the message is a command to take a note
        if 'take note' in message.lower():
            note = extract_note_content(message, 'take note')
            save_note_to_file(note)
            response = "I've saved the note for you."
        elif 'save this' in message.lower():
            note = extract_note_content(message, 'save this')
            save_note_to_file(note)
            response = "I've saved the note for you."
        elif 'show notes' in message.lower() or 'read notes' in message.lower():
            notes = read_notes_from_file()
            response = f"Here are your saved notes:\n {notes}"
        elif 'delete note' in message.lower():
            note_to_delete = extract_note_content(message, 'delete note')
            deleted = delete_note_from_file(note_to_delete)
            if deleted:
                response = f"I've deleted the note: {note_to_delete}"
            else:
                response = f"Could not find a note matching: {note_to_delete}"
        elif 'clear notes' in message.lower():
            delete_all_notes()
            response = "All notes have been cleared."
        else:
            # Generate a response based on the message
            response = generate_jarvis_response(message)

        # Log the response before sending it
        print(f"Generated response: {response}")

        # Return the response as JSON
        return jsonify({'response': response})

    except Exception as e:
        # Log the error for debugging
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Function to extract the note content by removing the keyword
def extract_note_content(message, keyword):
    keyword_position = message.lower().find(keyword)
    note_content = message[keyword_position + len(keyword):].strip()
    return note_content


# Save the note to a file with a timestamp
def save_note_to_file(note):
    file_path = os.path.join(os.path.dirname(__file__), 'notes.txt')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, 'a') as file:
        file.write(f"{note} (Saved on: {timestamp})\n")


# Read notes from the file
def read_notes_from_file():
    file_path = os.path.join(os.path.dirname(__file__), 'notes.txt')
    if not os.path.exists(file_path):
        return "You don't have any saved notes."

    with open(file_path, 'r') as file:
        return file.read()


# Delete a specific note from the file
def delete_note_from_file(note_to_delete):
    file_path = os.path.join(os.path.dirname(__file__), 'notes.txt')
    if not os.path.exists(file_path):
        return False

    deleted = False
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if note_to_delete.lower() not in line.lower():
                file.write(line)
            else:
                deleted = True

    return deleted


# Clear all notes
def delete_all_notes():
    file_path = os.path.join(os.path.dirname(__file__), 'notes.txt')
    if os.path.exists(file_path):
        os.remove(file_path)


# Function to generate Jarvis's response based on the message
def generate_jarvis_response(message):
    """
    Generate a response based on the user's message.
    For simplicity, match certain keywords in the message and provide
    a response from the relevant category in responses.txt.
    """
    message = message.lower()

    if 'hello' in message or 'hi' in message:
        return random.choice(responses_data.get('GREETING', ["I'm not sure how to greet you right now."]))
    elif 'bye' in message or 'goodbye' in message:
        return random.choice(responses_data.get('FAREWELL', ["Goodbye!"]))
    elif 'how are you' in message:
        return random.choice(responses_data.get('HOW_ARE_YOU', ["I'm doing well, thank you!"]))
    elif 'weather' in message:
        return random.choice(responses_data.get('WEATHER', ["I don't have weather data at the moment."]))
    elif 'time' in message:
        current_time = datetime.now().strftime("%H:%M")
        return random.choice(responses_data.get('TIME', ["I don't have the time right now."])).replace(
            "{{current_time}}", current_time)
    elif 'joke' in message:
        return random.choice(responses_data.get('JOKE', ["I don't have any jokes right now."]))
    elif 'compliment' in message:
        return random.choice(responses_data.get('COMPLIMENT', ["You're doing great!"]))
    elif 'fact' in message:
        return random.choice(responses_data.get('RANDOM_FACT', ["I don't have a fact for you at the moment."]))
    else:
        return random.choice(responses_data.get('UNKNOWN', ["I'm not sure how to respond to that."]))


if __name__ == '__main__':
    app.run(debug=True)
