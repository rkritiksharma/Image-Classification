# -*- coding: utf-8 -*-
"""Cats-vs-Dogs.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1BdFgjrhi9Zim-yvTZs23c13gHyCK3PZb
"""

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/

!kaggle datasets download -d salader/dogs-vs-cats

import zipfile
zip_ref = zipfile.ZipFile('/content/dogs-vs-cats.zip', 'r')
zip_ref.extractall('/content')
zip_ref.close()

"""**Import lib **"""

import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# Set paths
train_data_dir = '/content/train'
test_data_dir = '/content/test'

# Data augmentation and normalization
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    vertical_flip=False
)

test_datagen = ImageDataGenerator(rescale=1./255)

# Load and preprocess the training and testing data
train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='binary'  # 'binary' since we have two classes (cats and dogs)
)

test_generator = test_datagen.flow_from_directory(
    test_data_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='binary'
)

"""**build model**"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D

model = Sequential([
    # Custom convolutional layers
    Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(256, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(512, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),

    Flatten(),  # Flatten for fully connected layers
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')  # Binary classification
])

# Display the model summary
model.summary()

"""**compile the model**"""

model.compile(
    loss='binary_crossentropy',
    optimizer=Adam(learning_rate=0.0001),
    metrics=['accuracy']
)

"""**train the model**"""

# Callbacks for saving the best model and stopping early
checkpoint = ModelCheckpoint('best_model.keras', monitor='val_loss', save_best_only=True, mode='min')
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train the model
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // train_generator.batch_size,
    validation_data=test_generator,
    validation_steps=test_generator.samples // test_generator.batch_size,
    epochs=20,
    callbacks=[checkpoint, early_stopping],

)

#model.save('final_model.keras')
model.save('final_model.h5')

from google.colab import files

# Download the .h5 model
files.download('final_model.h5')  # For HDF5 format

from tensorflow.keras.models import load_model

model = load_model('final_model.h5')

"""**evalueate the model**"""

# Evaluate on test data
test_loss, test_acc = model.evaluate(test_generator)
print(f"Test Accuracy: {test_acc * 100:.2f}%")

"""**visualize training history**"""

# Plot training accuracy and loss
plt.plot(history.history['accuracy'], label='train accuracy')
plt.plot(history.history['val_accuracy'], label='val accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

plt.plot(history.history['loss'], label='train loss')
plt.plot(history.history['val_loss'], label='val loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

"""**make pridictions**"""

from tensorflow.keras.preprocessing import image



# Load a new image for prediction
img_path = '/content/cat1.jpeg'
img = image.load_img(img_path, target_size=(150, 150))
img_tensor = image.img_to_array(img)
img_tensor = np.expand_dims(img_tensor, axis=0)
img_tensor /= 255.



import cv2
test_img=cv2.imread(img_path)
test_img=cv2.resize(test_img,(256,256))
test_input=test_img.reshape((1,256,256,3))
# Predict the class (0 = cat, 1 = dog)
prediction = model.predict(img_tensor)
if prediction[0] > 0.5:
    plt.title("It's a dog!  🐶")
else:
    plt.title("It's a cat!  🐱")
plt.imshow(test_img)

images_folder = '/content/dogs_vs_cats/test/cats'  # Replace with your folder path
import os
dog_counter=0
cat_counter=0
total_counter=0
# Iterate through all image files in the directory
for img_file in os.listdir(images_folder):
    # Construct full image path
    img_path = os.path.join(images_folder, img_file)
    total_counter+=1

    try:
        # Load and preprocess image for the model
        img = image.load_img(img_path, target_size=(150, 150))  # Resize as per your model input size
        img_tensor = image.img_to_array(img)
        img_tensor = np.expand_dims(img_tensor, axis=0)
        img_tensor /= 255.0  # Normalize to [0,1]

        # Alternative preprocessing with OpenCV
        test_img = cv2.imread(img_path)
        test_img = cv2.resize(test_img, (256, 256))  # Resize for visualization
        test_input = test_img.reshape((1, 256, 256, 3))

        # Predict using the model
        prediction = model.predict(img_tensor)

        # Display the result
        if prediction[0] > 0.5:
            plt.title(f"{img_file}: It's a dog! 🐶")
            dog_counter+=1

        else:
            plt.title(f"{img_file}: It's a cat! 🐱")
            cat_counter+=1

        plt.imshow(cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for proper display
        plt.axis('off')
        plt.show()

    except Exception as e:
        print(f"Error processing file {img_file}: {e}")
print(f"total counter: {total_counter}")
print(f"dog counter: {dog_counter}")
print(f"cat counter: {cat_counter}")