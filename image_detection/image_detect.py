import os,time
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam

# Constants
IMG_SIZE = 224
NUM_OBJECTS = 3
IMAGES_PER_OBJECT = 300
EPOCHS = 20
BATCH_SIZE = 32
DATASET_DIR = "captured_images"
CONFIDENCE_THRESHOLD = 0.9

object_names = ['Background','Jam','Parachute']  # Names of the objects
model = None  # Placeholder for the trained model

CONSECUTIVE_FRAMES = 5  # Number of frames to confirm detection
PAUSE_DURATION = 3  # Seconds to pause after detection
POST_URL = "http://your-server-url/endpoint"  # Replace with your POST endpoint

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