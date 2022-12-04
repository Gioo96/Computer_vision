# -*- coding: utf-8 -*-
"""Final_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10IRrVeqV_yO7EXblUVViTPYZB2fyy5IJ

**Import modules**
"""

# Import modules
import os
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, Activation
import matplotlib.pyplot as plt
import keras
from PIL import Image 
import numpy as np
import cv2
import glob
from tensorflow.keras.optimizers import RMSprop
from keras.utils.vis_utils import plot_model
from keras.models import load_model
from google.colab.patches import cv2_imshow
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2

"""**Connection to google drive**"""

from google.colab import drive
drive.mount('/content/drive')

"""#Dataset preparation

Connection to the images stored in google drive and creation of Kaggle and Venice dataset
"""

# Path of the definitive sets
KAGGLE_path = '/content/drive/MyDrive/Classification/FINAL_DATASET/KAGGLE_300_300/'
VENICE_path = '/content/drive/MyDrive/Classification/FINAL_DATASET/VENICE_300_300/'

KAGGLE_path_boat = os.path.join(KAGGLE_path, "Boat")
KAGGLE_path_noboat = os.path.join(KAGGLE_path, "No Boat")
KAGGLE_num = len(os.listdir(KAGGLE_path_boat)) + len(os.listdir(KAGGLE_path_noboat))

VENICE_path_boat = os.path.join(VENICE_path, "Boat")
VENICE_path_noboat = os.path.join(VENICE_path, "No Boat")
VENICE_num = len(os.listdir(VENICE_path_boat)) + len(os.listdir(VENICE_path_noboat)) 

# Kaggle dataset
filelist_KAGGLE_boat = glob.glob(KAGGLE_path + "/Boat/*.jpg")
filelist_KAGGLE_noboat = glob.glob(KAGGLE_path + "/No Boat/*.jpg")
X_KAGGLE_boat = np.array([np.array(Image.open(fname)) for fname in filelist_KAGGLE_boat])
X_KAGGLE_noboat = np.array([np.array(Image.open(fname)) for fname in filelist_KAGGLE_noboat])
X_KAGGLE = np.concatenate([X_KAGGLE_boat, X_KAGGLE_noboat])

# Venice dataset
filelist_VENICE_boat = glob.glob(VENICE_path + "/Boat/*.jpg")
filelist_VENICE_noboat = glob.glob(VENICE_path + "/No Boat/*.jpg")
X_VENICE_boat = np.array([np.array(Image.open(fname)) for fname in filelist_VENICE_boat])
X_VENICE_noboat = np.array([np.array(Image.open(fname)) for fname in filelist_VENICE_noboat])
X_VENICE = np.concatenate([X_VENICE_boat, X_VENICE_noboat])

"""Function to create the corresponding labels and
conversion to numeric codes:


*   $\textbf{Boat}$: 1
*   $\textbf{No Boat}$: 0
"""

def create_data(array_images, img_folder, num):
      
    class_name = np.zeros(num)
    i = 0
    for dir in os.listdir(img_folder):
      for file in os.listdir(os.path.join(img_folder, dir)):
        if (dir == "Boat"):
          class_name[i] = 1
        else:
          class_name[i] = 0
        i = i + 1
    class_name = class_name.astype('int')
   
    return array_images, class_name


# Corresponding labels
X_KAGGLE, Y_KAGGLE = create_data(X_KAGGLE, KAGGLE_path, KAGGLE_num)
X_VENICE, Y_VENICE = create_data(X_VENICE, VENICE_path, VENICE_num)

# Final datasets
X_tot = np.concatenate([X_KAGGLE, X_VENICE])
Y_tot = np.concatenate([Y_KAGGLE, Y_VENICE])
X_tot, Y_tot = shuffle(X_tot, Y_tot, random_state=0)

"""Split the dataset to create training set and test set"""

X_train, X_test, Y_train, Y_test = train_test_split(X_tot, Y_tot, test_size = 0.33, random_state = 42)

"""#Convolutional neural network

Dataset images are of size 300 x 300 and feed them as input to the network.

The network is characterized by three convolutional layers:

1.   The first layer has 32 - 3x3 filters
2.   The second layer has 32 - 3x3 filters
3.   The third layer has 64 - 3x3 filters.

In addition, there are three max-pooling layers each of size 2 x 2 and at the end we added a Dense layer in order to compute the classification.
"""

model_CNN = Sequential()
model_CNN.add(Conv2D(32, (3, 3), input_shape=(300, 300, 3)))
model_CNN.add(Activation('relu'))
model_CNN.add(MaxPooling2D(pool_size=(2, 2)))

model_CNN.add(Conv2D(32, (3, 3)))
model_CNN.add(Activation('relu'))
model_CNN.add(MaxPooling2D(pool_size=(2, 2)))

model_CNN.add(Conv2D(64, (3, 3)))
model_CNN.add(Activation('relu'))
model_CNN.add(MaxPooling2D(pool_size=(2, 2)))

model_CNN.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
model_CNN.add(Dense(64))
model_CNN.add(Activation('relu'))
model_CNN.add(Dropout(0.5))
model_CNN.add(Dense(1))
model_CNN.add(Activation('sigmoid'))

# Compile the model using the Adam optimizer
model_CNN.compile(loss = 'binary_crossentropy',
              optimizer=keras.optimizers.Adam(learning_rate=0.001),
              metrics=['accuracy'])

# Fit the model
history_CNN = model_CNN.fit(X_train, Y_train, epochs = 16, validation_data = (X_test, Y_test), verbose = 1)

# Model summary
model_CNN.summary()

# Visualization of the model
plot_model(model_CNN, to_file='model_plot.png', show_shapes=True, show_layer_names=True)

"""Show missclassified images on test dataset """

# Test Dataset: plot the misclassified images
predicted_classes = model_CNN.predict(X_test)
predicted_classes = np.round(predicted_classes)
predicted_classes = predicted_classes.astype('int')

t = 0
i = 0
for label in predicted_classes:
  if label != Y_test[i]:
    print("Predicted: ", label)
    cv2_imshow(X_test[i])
    cv2.waitKey(1)
    t = t+1
  i = i+1

print("Number of missclassified images: ", t)
print("Total number of Test images: ", i)
print(predicted_classes)

"""Evaluation of the CNN performance"""

# evaluate model
test_eval = model_CNN.evaluate(X_test, Y_test, verbose = 1)
print(test_eval)

# plot diagnostic learning curves
# plot loss
plt.title('Cross Entropy Loss')
plt.plot(history_CNN.history['loss'], color='blue', label='train')
plt.plot(history_CNN.history['val_loss'], color='orange', label='test')
plt.legend(['train', 'val'])
plt.grid('on')
plt.show()
plt.savefig('CrossEntropyLoss.png')
# plot accuracy
plt.title('Classification Accuracy')
plt.plot(history_CNN.history['accuracy'], color='blue', label='train')
plt.plot(history_CNN.history['val_accuracy'], color='orange', label='test')
plt.legend(['train', 'val'])
plt.grid('on')
plt.show()
plt.savefig('ClassificationAccuracy.png')

"""#Freeze and save the model"""

# Freeze and save the model
full_model = tf.function(lambda inputs: model_CNN(inputs))
full_model = full_model.get_concrete_function([tf.TensorSpec(model_input.shape, model_input.dtype) for model_input in model_CNN.inputs])

frozen_func = convert_variables_to_constants_v2(full_model)
frozen_func.graph.as_graph_def()

tf.io.write_graph(graph_or_graph_def=frozen_func.graph, logdir='/content/drive/MyDrive/Classification', name = "model_CNN_try.pb", as_text = False)
tf.io.write_graph(graph_or_graph_def=frozen_func.graph, logdir='/content/drive/MyDrive/Classification', name = "model_CNN_try.pbtxt", as_text = True)