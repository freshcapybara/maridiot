import os
import sys
import numpy as np
import argparse
import glob
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import regularizers

RAM_SIZE = 10240
CONTROLS_INPUT_SIZE = 9
#SLICE_SIZE = 40
#BORDER_SIZE = 5

def slice():
    pass

def parse_logfile(numpy_file):
    array = np.load(numpy_file)
    return array


def parse_all_logfiles(directory):
    numpy_files_inputs = glob.glob(os.path.join(directory, "input", "*.npy"))
    numpy_files_ram = glob.glob(os.path.join(directory, "ram", "*.npy"))
    print(f"{len(numpy_files_inputs)} log files found.")

    numpy_files_inputs.sort()
    labels = []
    training_data = []
    for input_file in numpy_files_inputs:
        basename = os.path.basename(input_file)
        ram_file = os.path.join(directory, "ram", basename) 
        if ram_file not in numpy_files_ram:
            print(f"Could not find corresponding ram file for input file {basename}")
            continue

        print(f"Parsing numpy file {input_file}")
        raw = parse_logfile(input_file)
        labels.extend(raw)

        raw = parse_logfile(ram_file)
        training_data.extend(raw)
    
    if not labels:
        print("No usable training data found.")
        sys.exit()

    labels = np.array(labels, dtype=np.uint8)
    training_data = np.array(training_data, dtype=np.uint8)

    assert labels.shape[0] == training_data.shape[0]
    print("labels", labels.shape, labels.dtype)
    print("training data", training_data.shape, training_data.dtype)
    
    return training_data, labels


def train_model_simple(training_data, labels):
    model = keras.models.Sequential()
    model.add(layers.Dense(4096, activation='relu', input_shape=(RAM_SIZE, ) ))
    model.add(layers.Dense(2048, activation='relu', input_shape=(RAM_SIZE, ) ))
    model.add(layers.Dense(2048, activation='relu', input_shape=(RAM_SIZE, ) ))
    model.add(layers.Dense(CONTROLS_INPUT_SIZE, activation='sigmoid'))

    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(training_data, labels, epochs=100, batch_size=512, shuffle=True, validation_split=0.2)

    model.save(os.path.join("models", 'simple_model'))


def train_model_lstm(training_data, labels):
    model = keras.models.Sequential()
    model.add(layers.Dense(64, activation='relu', input_shape=(RAM_SIZE, )))
    model.add(layers.LSTM(64, activation='relu'))
    model.add(layers.LSTM(128, activation='relu'))
    model.add(layers.LSTM(64, activation='relu'))
    model.add(layers.Dense(32, activation='relu'))
    model.add(layers.Dense(CONTROLS_INPUT_SIZE, activation='sigmoid'))

    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(training_data, labels, epochs=10)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help="What to save the model as")
    parser.add_argument('directory', help="Directory of the training data")
    args = parser.parse_args()

    train_data, labels = parse_all_logfiles(args.directory)
    train_model_simple(train_data, labels)


if __name__ == "__main__":
    main()