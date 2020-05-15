import os
import sys
import numpy as np
import argparse
import glob
from tensorflow import keras
from tensorflow.keras import layers

RAM_SIZE = 10240
CONTROLS_INPUT_SIZE = 9
SLICE_SIZE = 40
BORDER_SIZE = 5

def slice():
    pass

def parse_logfile(numpy_file):
    input_array = np.load(numpy_file, allow_pickle=True)

    if not input_array.shape[1] == 2:
        print(f"Weirdly formatted input shape {input.shape[1]}")
        sys.exit()
    
    num_frames = input_array.shape[0]
    print(f"{num_frames} frames loaded")

    # generate the slices with some overlap
    slices = []
    current_frame = 0
    while True:
        end_frame = current_frame + SLICE_SIZE

        if end_frame >= num_frames:
            break

        slices.append(input_array[current_frame:end_frame])
        current_frame += BORDER_SIZE

    print(f"Generated {len(slices)} slices")
    return slices


def parse_all_logfiles(directory):
    numpy_files = glob.glob(os.path.join(directory, "*.npy"))
    numpy_files.sort()
    print(f"{len(numpy_files)} log files found.")

    all_slices = []
    for numpy_file in numpy_files:
        print(f"Parsing numpy file {numpy_file}")
        slices = parse_logfile(numpy_file)
        all_slices.extend(slices)
    
    all_slices = np.asarray(all_slices)
    print(all_slices.shape)
    traning_data = all_slices[:, :, 0]
    #traning_data.flatten()
    labels = all_slices[:, :, 1]

    #print(traning_data)
    print(traning_data.shape)
    #print(labels)
    print(labels.shape)

    # TODO: might want to shuffle the slices, might not

    return traning_data, labels


def train_model_simple(training_data, labels):
    model = keras.models.Sequential()
    model.add(layers.Dense(64, activation='relu', input_shape=(training_data.shape[0], SLICE_SIZE, RAM_SIZE) ))
    model.add(layers.Dense(32, activation='relu'))
    model.add(layers.Dense(32, activation='relu'))
    model.add(layers.Dense(CONTROLS_INPUT_SIZE, activation='sigmoid'))

    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(training_data, labels, epochs=2)

def train_model_lstm(training_data, labels):
    model = keras.models.Sequential()
    model.add(layers.Dense(64, activation='relu', input_shape=(SLICE_SIZE, RAM_SIZE)))
    model.add(layers.LSTM(64, activation='relu'))
    model.add(layers.LSTM(128, activation='relu'))
    model.add(layers.LSTM(64, activation='relu'))
    model.add(layers.Dense(32, activation='relu'))
    model.add(layers.Dense(CONTROLS_INPUT_SIZE, activation='sigmoid'))

    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(training_data, labels, epochs=10)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()

    train_data, labels = parse_all_logfiles(args.directory)
    train_model_simple(train_data, labels)


if __name__ == "__main__":
    main()