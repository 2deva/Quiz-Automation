import os
import pyautogui
import requests
import openai
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import ImageGrab, Image, ImageEnhance
import pytesseract
import io
import threading
import keyboard
import asyncio
from tkinter import scrolledtext, ttk, Tk, Canvas
import logging
import uvicorn
import signal
import sys
import cv2
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the tesseract command path (adjust path based on your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize FastAPI app
api_app = FastAPI()

# OpenAI API key from environment variable
openai.api_key = "API"

# Function to extract text from an image using pytesseract with preprocessing
def extract_text_from_image(image):
    try:
        # Convert to grayscale and then to a NumPy array
        grayscale_image = image.convert("L")
        img_np = np.array(grayscale_image)

        # Apply Gaussian Blur and Adaptive Thresholding
        blurred = cv2.GaussianBlur(img_np, (5, 5), 0)
        enhanced_image = cv2.adaptiveThreshold(blurred, 255,
                                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                               cv2.THRESH_BINARY, 11, 2)

        # Use pytesseract to extract text
        custom_config = r'--oem 3 --psm 6'
        return pytesseract.image_to_string(enhanced_image, config=custom_config)
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return ""

# Function to send the extracted text to GPT-4 for analysis
async def get_gpt4_analysis(extracted_text):
    retries = 3
    while retries > 0:
        try:
            # General prompt for reasoning and analysis tasks
            task_prompt = (
                "You are an expert in solving quiz questions related to logical reasoning, "
                "arithmetic, aptitude, and verbal ability. Here is a question: " + extracted_text + ". "
                "Think step by step and provide a clear, detailed solution or answer to the problem presented."
            )

            # Use GPT-4 model for text analysis
            response = await asyncio.to_thread(openai.ChatCompletion.create,
                                               model="gpt-4o-mini",
                                               messages=[
                                                   {"role": "system", "content": "You are a helpful assistant specialized in solving quiz questions."},
                                                   {"role": "user", "content": task_prompt},
                                               ],
                                               max_tokens=1000)
            return response['choices'][0]['message']['content']
        except Exception as e:
            logging.error(f"Error getting GPT-4 analysis: {e}. Retrying...")
            retries -= 1
            await asyncio.sleep(2)
    return "Error getting analysis"

# FastAPI route to handle the image upload
@api_app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # Open the image using PIL.Image
        img = Image.open(io.BytesIO(contents))

        # Extract text from the image
        extracted_text = await asyncio.to_thread(extract_text_from_image, img)

        # Get the response from GPT-4
        answer_data = await get_gpt4_analysis(extracted_text)
        return JSONResponse(content={"answer": answer_data})
    except Exception as e:
        logging.error(f"Error in upload_file: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Global variable to keep track of the current answer window
current_answer_window = None

# Function to capture a user-dragged screenshot and upload it directly from memory
async def take_screenshot_and_upload():
    global current_answer_window
    try:
        # Close the current answer window if it exists
        if current_answer_window is not None:
            try:
                current_answer_window.destroy()
            except Exception as e:
                logging.error(f"Error destroying current answer window: {e}")
            current_answer_window = None

        # Create a tkinter window to allow the user to drag and select the screenshot area
        root = Tk()
        root.attributes('-fullscreen', True)  # Make the window fullscreen
        root.attributes('-topmost', True)  # Make sure the window is on top
        root.configure(bg='black')
        root.attributes('-alpha', 0.3)  # Make the window semi-transparent

        # Variables to store the coordinates
        selection_rectangle = None

        # Canvas to draw the selection box
        canvas = Canvas(root, cursor='cross', bg='black')
        canvas.pack(fill='both', expand=True)

        # Function to start selecting the area
        def on_mouse_down(event):
            nonlocal selection_rectangle
            start_x, start_y = event.x, event.y
            # Create the selection rectangle
            selection_rectangle = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='blue', width=8)
            canvas.start_x, canvas.start_y = start_x, start_y

        # Function to update the selection rectangle
        def on_mouse_drag(event):
            end_x, end_y = event.x, event.y
            canvas.coords(selection_rectangle, canvas.start_x, canvas.start_y, end_x, end_y)

        # Function to finalize the area selection
        def on_mouse_up(event):
            canvas.end_x, canvas.end_y = event.x, event.y
            root.quit()  # Close the tkinter mainloop

        # Bind the mouse events to the tkinter window
        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

        # Run the tkinter mainloop to allow area selection
        root.mainloop()
        root.destroy()  # Destroy the tkinter window to save resources

        # Capture the selected area screenshot
        screenshot = ImageGrab.grab(bbox=(canvas.start_x, canvas.start_y, canvas.end_x, canvas.end_y))
        
        # Convert the image to bytes and upload it to FastAPI
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        buffered.seek(0)

        # Upload the screenshot to FastAPI
        url = 'http://127.0.0.1:8000/upload/'
        files = {'file': ('screenshot.png', buffered, 'image/png')}
        response = requests.post(url, files=files)

        if response.status_code == 200:
            json_response = response.json()
            answer = json_response.get('answer', 'No answer found')
            logging.info(f"Answer: {answer}")

            # Create a modern dialog box to display the answer
            current_answer_window = display_answer(answer)
        else:
            logging.error(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        logging.error(f"Error during screenshot upload: {str(e)}")

# Function to display the answer in a dialog box
def display_answer(answer):
    answer_window = Tk()
    answer_window.title("Quiz Answer")
    answer_window.geometry("900x500")
    answer_window.configure(bg='white')

    # Position the window to the far right of the screen
    screen_width = answer_window.winfo_screenwidth()
    screen_height = answer_window.winfo_screenheight()
    window_width = 700
    window_height = 500
    x_position = screen_width - window_width
    y_position = (screen_height - window_height) // 2
    answer_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Use ttk for a modern look
    style = ttk.Style()
    style.theme_use('clam')

    # Scrollable text box for displaying the answer
    answer_text = scrolledtext.ScrolledText(answer_window, wrap='word', font=("Poppins", 14), width=100, height=15)
    answer_text.insert('end', f"Answer: {answer}")
    answer_text.config(state='disabled')  # Make the text box read-only
    answer_text.pack(pady=(20, 20))
    answer_text.see('end')  # Scroll to the end of the answer

    def type_answer():
        pyautogui.write(answer)
        answer_window.destroy()

    type_button = ttk.Button(answer_window, text="Type Answer", command=type_answer)
    type_button.pack(pady=10)

    close_button = ttk.Button(answer_window, text="Close", command=answer_window.destroy)
    close_button.pack(pady=10)

    answer_window.mainloop()
    return answer_window

# Set up keyboard listener for hotkey (Ctrl + Shift + S) to trigger screenshot
def setup_screenshot_hotkey():
    logging.info("Listening for Ctrl+Shift+S to take a screenshot...")
    keyboard.add_hotkey('ctrl+shift+s', lambda: asyncio.run(handle_screenshot_hotkey()))

async def handle_screenshot_hotkey():
    global current_answer_window
    if current_answer_window is not None:
        try:
            current_answer_window.destroy()
        except Exception as e:
            logging.error(f"Error destroying current answer window: {e}")
        current_answer_window = None
    await take_screenshot_and_upload()

# Start the FastAPI app in the background
def start_fastapi():
    uvicorn.run(api_app, host="127.0.0.1", port=8000)

# Signal handler to catch Ctrl+C and exit gracefully
def signal_handler(sig, frame):
    logging.info('Exiting...')
    sys.exit(0)

# Main execution
if __name__ == "__main__":
    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Start FastAPI in the background
    fastapi_thread = threading.Thread(target=start_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()

    # Set up the hotkey listener
    setup_screenshot_hotkey()

    # Keep the script running
    keyboard.wait('esc')  # Press ESC to stop the script
