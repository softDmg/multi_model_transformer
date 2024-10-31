from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTextEdit
from PyQt5.QtGui import QPixmap
import os
import sys
import requests
from image_llama import Ui_MainWindow  # Import the UI class from image_llama

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect buttons to their respective methods
        self.ui.upload_image_button.clicked.connect(self.upload_image)
        self.ui.send_Button.clicked.connect(self.send_prompt_and_image)

        # Initialize image path as None
        self.image_file_path = None

        # Use the ngrok URL generated
        self.ngrok_url = "https://9fcf-34-126-130-61.ngrok-free.app"  # Replace with the actual ngrok URL

        # Style the response text area
        self.ui.response_textEdit.setStyleSheet("""
            QTextEdit {
                font-family: Arial, Helvetica, sans-serif;
                font-size: 14px;
                color: #333;
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 5px;
            }
        """)

        # Initialize the progress bar
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setVisible(False)

    def upload_image(self):
        # Open file dialog to select an image
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            None, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options
        )

        if file_name:
            # Ensure the file exists and is a valid image format
            if os.path.exists(file_name):
                pixmap = QPixmap(file_name)
                
                if not pixmap.isNull():  # Valid image file
                    # Resize the image to fit the label while maintaining the aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        self.ui.image_label.size(), aspectRatioMode=QtCore.Qt.KeepAspectRatio
                    )
                    self.ui.image_label.setPixmap(scaled_pixmap)
                    self.ui.image_label.setScaledContents(True)
                    self.image_file_path = file_name
                else:
                    self.ui.response_textEdit.setText("Invalid image file. Please select a valid image.")
            else:
                self.ui.response_textEdit.setText("File not found. Please try again.")
        else:
            self.ui.response_textEdit.setText("No file selected.")

    def send_prompt_and_image(self):
        self.ui.response_textEdit.clear()  # Clear the response text area
        # Retrieve the prompt text
        prompt = self.ui.prompt_lineEdit.text().strip()  # Trim whitespace
        image_path = self.image_file_path

        print(f"Prompt: '{prompt}'")
        print(f"Image Path: '{image_path}'")

        # Initialize response text
        response_text = None

        # Show loading indicator and progress bar
        self.ui.response_textEdit.setText("Loading...")
        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setValue(50)  # Set to 50% to indicate loading

        response = None
        try:
            if prompt and image_path:
                print("Prompt and image provided.")
                # Send both prompt and image
                api_url = f"{self.ngrok_url}/image"
                with open(image_path, "rb") as image_file:
                    files = {"image": image_file}
                    payload = {"user_input": prompt}
                    response = requests.post(api_url, files=files, data=payload)
            
            elif prompt:
                print("Only prompt provided.")
                # Send prompt to text-to-text API
                api_url = f"{self.ngrok_url}/chat"
                payload = {"user_input": prompt}
                response = requests.post(api_url, data=payload)
            
            elif image_path:
                print("Only image provided.")
                # Only image provided
                response_text = "Only image provided, please write a prompt."
            
            else:
                # No prompt or image provided
                response_text = "You did not provide any prompt or image."

            # Handle response from the API
            if response:
                if response.status_code == 200:
                    response_text = response.json().get("response", "No response from the model.")
                else:
                    response_text = f"Error {response.status_code}: {response.text}"

        except requests.exceptions.RequestException as e:
            response_text = f"An error occurred during the API request: {str(e)}"
        except Exception as e:
            response_text = f"An unexpected error occurred: {str(e)}"

        # Display the response in the response_textEdit
        if response_text:
            self.ui.response_textEdit.setText(response_text)
        else:
            self.ui.response_textEdit.setText("You did not provide any prompt or image.")

        # Hide progress bar
        self.ui.progressBar.setVisible(False)

def main():
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()