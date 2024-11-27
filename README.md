# Quiz-Automation
Automate quiz answering using ChatGPT API
This file is a Python script that uses FastAPI to create a web server for handling image uploads, processes the images to extract text using Tesseract OCR, and then sends the extracted text to OpenAI's GPT-4 model for analysis. It also includes functionality to capture screenshots and display the results in a Tkinter dialog box. Here are the key components:

Imports: The script imports various libraries including FastAPI, PIL, Tesseract, OpenAI, Tkinter, and others for handling image processing, web server, and GUI.

Logging Setup: Configures logging for the application.

Tesseract Configuration: Sets the path for the Tesseract OCR executable.

FastAPI Initialization: Initializes a FastAPI app.

OpenAI API Key: Retrieves the OpenAI API key from environment variables.

Text Extraction Function: Defines a function to extract text from an image using Tesseract OCR with preprocessing.

GPT-4 Analysis Function: Defines an asynchronous function to send the extracted text to GPT-4 for analysis and get a detailed solution or answer.

FastAPI Route: Defines a FastAPI route to handle image uploads, extract text from the uploaded image, and get the analysis from GPT-4.

Global Variable: Keeps track of the current answer window.

Screenshot Function: Defines an asynchronous function to capture a user-dragged screenshot, upload it to the FastAPI server, and display the result in a Tkinter dialog box.

Answer Display Function: Defines a function to display the answer in a Tkinter dialog box.

Hotkey Setup: Sets up a keyboard listener for the hotkey (Ctrl + Shift + S) to trigger the screenshot function.

FastAPI Server: Starts the FastAPI server in a background thread.

Signal Handler: Defines a signal handler to catch Ctrl+C and exit gracefully.

Main Execution: Registers the signal handler, starts the FastAPI server, sets up the hotkey listener, and keeps the script running.

Summary of Key Functions:
extract_text_from_image(image): Extracts text from an image using Tesseract OCR.
get_gpt4_analysis(extracted_text): Sends the extracted text to GPT-4 for analysis.
upload_file(file: UploadFile): FastAPI route to handle image uploads and process them.
take_screenshot_and_upload(): Captures a screenshot, uploads it, and displays the result.
display_answer(answer): Displays the answer in a Tkinter dialog box.
setup_screenshot_hotkey(): Sets up the hotkey listener.
start_fastapi(): Starts the FastAPI server.
signal_handler(sig, frame): Handles Ctrl+C to exit gracefully.
This script integrates image processing, web server, and GUI functionalities to provide a complete solution for capturing screenshots, extracting text, and getting detailed answers using GPT-4.
