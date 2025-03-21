import os,time
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
import requests
import RPi.GPIO as GPIO

# Constants
IMG_SIZE = 224
NUM_OBJECTS = 3
IMAGES_PER_OBJECT = 300
EPOCHS = 20
BATCH_SIZE = 32
DATASET_DIR = "captured_images"
CONFIDENCE_THRESHOLD = 0.9

object_names = ['Background','Colgate', 'Good Day', 'Jam', 'Maggi', 'Parachute']
product_prices = {
    'Background': 0.0,  # Assuming 'Background' is just a placeholder for background images, no price
    'Colgate': 10.0, 
    'Good Day': 25.0,
    'Jam': 20.0,
    'Maggi': 15.0,
    'Parachute': 20.0
}
model = None  # Placeholder for the trained model

CONSECUTIVE_FRAMES = 5  # Number of frames to confirm detection
PAUSE_DURATION = 7  # Seconds to pause after detection
POST_URL = "http://your-server-url/endpoint"  # Replace with your POST endpoint
sensor = 36
buzzer = 35
GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor,GPIO.IN)
GPIO.setup(buzzer,GPIO.OUT)
GPIO.output(buzzer,False)
print("IR Sensor Ready...")
# Step 3: Detect Objects
def detect_objects():
    """
    Real-time object detection using the trained model.
    """
    global model
    model = tf.keras.models.load_model("smart_trolley_model.h5")
    cap = cv2.VideoCapture(0)

    print("Starting object detection. Press 'q' to quit.")
    detected_object = None
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error accessing camera.")
                break
            if GPIO.input(sensor):
               GPIO.output(buzzer,False)
            else:
               GPIO.output(buzzer,True)
               print("Obstacle detected")
               continue
            # Preprocess the frame
            img = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
            img_array = np.expand_dims(img / 255.0, axis=0)

            # Predict the object
            predictions = model.predict(img_array, verbose=0)
            predicted_class = np.argmax(predictions)
            confidence = np.max(predictions)

            if confidence > CONFIDENCE_THRESHOLD:
                current_object = object_names[predicted_class]
                if current_object == detected_object:
                    consecutive_count += 1
                else:
                    detected_object = current_object
                    consecutive_count = 1
            else:
                detected_object = None
                consecutive_count = 0
            time.sleep(0.5)
            # Confirm detection after 5 consecutive frames
            if consecutive_count >= CONSECUTIVE_FRAMES and detected_object is not 'Background':
                print(f"Detected: {detected_object}")
                #send_post_request(detected_object)
                print('Sending Data..')

                GPIO.output(buzzer, True)
                time.sleep(0.3)
                GPIO.output(buzzer, False)
                time.sleep(0.3)
                GPIO.output(buzzer, True)
                time.sleep(0.3)
                GPIO.output(buzzer, False)
                # Define the URL for the add_to_cart endpoint
                url = 'http://127.0.0.1:8001/add_to_cart/'

                # Define the data to send in the POST request
                data = {
                    'product_name': detected_object,
                    'price': product_prices.get(detected_object, None),
                    'quantity': '1',
                }

                # Send a POST request to the server
                response = requests.post(url, data=data)

                # Check the response
                if response.status_code == 200:
                    print("Item added to cart:", response.json())
                else:
                    print("Error:", response.status_code, response.text)

                time.sleep(PAUSE_DURATION)  # Pause for 3 seconds
                
                print("Place the next item..")
                consecutive_count = 0
                detected_object = None
    except KeyboardInterrupt:
        print("Object detection stopped.")
    finally:
        cap.release()
        print("Camera released.")


detect_objects()
