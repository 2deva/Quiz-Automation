# Quiz-Automation
Automate quiz answering using ChatGPT API
This file is a Python script that uses FastAPI to create a web server for handling image uploads, processes the images to extract text using Tesseract OCR, and then sends the extracted text to OpenAI's GPT-4 model for analysis. It also includes functionality to capture screenshots and display the results in a Tkinter dialog box.

Summary of Key Functions:
1) extract_text_from_image(image): Extracts text from an image using Tesseract OCR.
2) get_gpt4_analysis(extracted_text): Sends the extracted text to GPT-4 for analysis.
3) upload_file(file: UploadFile): FastAPI route to handle image uploads and process them.
4) take_screenshot_and_upload(): Captures a screenshot, uploads it, and displays the result.
5) display_answer(answer): Displays the answer in a Tkinter dialog box.

setup_screenshot_hotkey(): Sets up the hotkey listener.
start_fastapi(): Starts the FastAPI server.
signal_handler(sig, frame): Handles Ctrl+C to exit gracefully.
This script integrates image processing, web server, and GUI functionalities to provide a complete solution for capturing screenshots, extracting text, and getting detailed answers using GPT-4.
