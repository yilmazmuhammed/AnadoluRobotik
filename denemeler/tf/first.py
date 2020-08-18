import cv2
import numpy as np
import tensorflow as tf


# Please write your code only where you are indicated.
# please do not remove model fitting inline comments.

# YOUR CODE STARTS HERE
class myCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if logs.get('acc') > 0.95:
            print("\nReached 95% accuracy so cancelling training!")
            self.model.stop_training = True


callback = myCallback()
# YOUR CODE ENDS HERE
from tensorflow.python.keras.optimizers import RMSprop

training_images = []
training_labels = []
test_images = []
test_labels = []
labels = "0000000111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111110000000000000111111111111111111111111111111111111111111111111111111111111111111111110001111111111111111111111111111111111111111111111111111111111111111100000000011111111111111111111111111111111111111111111111111111111111111111111111111011111111111111111111100111111111111111111111111111000000000000000000111111111111111100001111111111111111101111111111111111100111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111100000000001111111111111111111111111111111111111111111110000000001111111111111111111111111000000000000000000000111111111110110111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111100011111001110000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
for i in range(982):
    img = cv2.imread("frames/"+str(i) + ".png", cv2.IMREAD_COLOR)
    if i % 10 == 0:
        test_images.append(img)
        test_labels.append(float(labels[i]))
    else:
        training_images.append(img)
        training_labels.append(float(labels[i]))

test_images = np.array(test_images)
test_labels = np.array(test_labels)
training_images = np.array(training_images)
training_labels = np.array(training_labels)
#print(test_images, test_labels, training_images, training_labels)

# mnist = tf.keras.datasets.mnist
# (training_images, training_labels), (test_images, test_labels) = mnist.load_data(path=path)
# # YOUR CODE STARTS HERE
print(np.shape(training_images))
#training_images = training_images.reshape((883, 480, 720, 3))
#test_images = test_images.reshape((99, 480, 720, 3))
training_images = training_images / 255.0
test_images = test_images / 255.0
# # YOUR CODE ENDS HERE
print("modelin üstü")
model = tf.keras.models.Sequential([
    # YOUR CODE STARTS HERE
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu', input_shape=(480, 720, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
    # YOUR CODE ENDS HERE
])
print("Model oluştu")

model.compile(optimizer=RMSprop(lr=0.001), loss='binary_crossentropy', metrics=['accuracy'])
print("Compile oluştu")
# model fitting
history = model.fit(
    # YOUR CODE STARTS HERE
    training_images, training_labels, epochs=500, batch_size=64, callbacks=[callback]
    # YOUR CODE ENDS HERE
)
print("Train edildi")
# model fitting
test_loss, test_acc = model.evaluate(test_images, test_labels)
print(test_acc)

if __name__ == '__main__':
    pass
