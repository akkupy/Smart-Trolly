import os
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
CONFIDENCE_THRESHOLD = 0.7

object_names = ['Background','Jam','Parachute']  # Names of the objects
model = None  # Placeholder for the trained model


# Step 1: Capture Images
def capture_images():
    """
    Capture images for each object and save them in labeled directories.
    """
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

    global object_names

    for obj_idx in range(NUM_OBJECTS):
        obj_name = input(f"Enter name for object {obj_idx + 1}: ")
        object_names.append(obj_name)

        obj_dir = os.path.join(DATASET_DIR, obj_name)
        if not os.path.exists(obj_dir):
            os.makedirs(obj_dir)

        print(f"Capturing images for {obj_name}. Press 's' to save and 'q' to quit.")
        cap = cv2.VideoCapture(0)
        count = 0

        while count < IMAGES_PER_OBJECT:
            ret, frame = cap.read()
            if not ret:
                print("Error accessing camera.")
                break

            cv2.imshow("Capture Images", frame)

            key = cv2.waitKey(1)
            if key & 0xFF == ord('s'):  # Save image
                img_path = os.path.join(obj_dir, f"{count}.jpg")
                cv2.imwrite(img_path, frame)
                count += 1
                print(f"Saved: {img_path}")
            elif key & 0xFF == ord('q'):  # Quit
                break

        cap.release()
        cv2.destroyAllWindows()


# Step 2: Train the Model
def train_model():
    """
    Train a MobileNetV2-based model using captured images.
    """
    global model

    # Data augmentation
    datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        validation_split=0.2,
    )

    train_data = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
    )
    val_data = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
    )

    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    base_model.trainable = False  # Freeze base layers

    # Add custom layers
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation="relu")(x)
    output = Dense(NUM_OBJECTS, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=output)
    model.compile(optimizer=Adam(learning_rate=0.001), loss="categorical_crossentropy", metrics=["accuracy"])

    # Train the model
    model.fit(train_data, validation_data=val_data, epochs=EPOCHS, batch_size=BATCH_SIZE)
    model.save("smart_trolley_model.h5")
    print("Model training complete and saved as 'smart_trolley_model.h5'.")

capture_images()
train_model()