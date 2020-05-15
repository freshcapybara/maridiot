import sys
import numpy as np
import argparse
import glob
from tf.keras import keras
import os

RAM_SIZE = 10240
CONTROLS_INPUT_SIZE = 9
SLICE_SIZE = 40
BORDER_SIZE = 5

def slice():
    pass

def parse_logfile(numpy_file):
    input_array = np.load(numpy_file)

    if not input.shape[1] == 2:
        print(f"Weirdly formatted input shape {input.shape[1]}")
        sys.exit()
    
    num_frames = input.shape[0]
    print(f"{num_frames} loaded from {numpy_file}")

    # generate the slices with some overlap
    slices = []
    current_frame = 0
    while True:
        end_frame = current_fram + SLICE_SIZE

        if end_frame >= num_frames:
            break

        slices.append(input[current_frame:end_frame])
        current_frame += BORDER_SIZE

    print(f"Generated {len(slices)} from {numpy_file}.")
    return slices


def parse_all_logfiles(directory):
    numpy_files = glob.glob(os.path.join(directory, "*.npy"))
    numpy_files.sort()
    print(f"{len(numpy_file)} log files found.")

    all_slices = []
    for numpy_file in numpy_files:
        print(f"Parsing numpy file {numpy_file}")
        slices = parse_logfile(numpy_file)
        all_slices.extend(slices)
    
    traning_data = np.asarray(np.asarray(all_slices[:, 0]))
    labels = np.asarray(np.asarray(all_slices[:, 1]))
    print(traning_data)
    print(traning_data.shape)
    print(labels)
    print(labels.shape)
    return traning_data, labels


def train_model(training_data, labels):
    model = models.Sequential()
    model.add(layers.Dense(64, activation='relu', input_shape=(RAM_SIZE,) ))
    model.add(layers.Dense(32, activation='relu', ))
    model.add(layers.Dense(32, activation='relu', ))
    model.add(layers.Dense(CONTROLS_INPUT_SIZE, activation='sigmoid'))

    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(training_data, labels. epoch=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()

    parse_all_logfiles(args.directory)


if __name__ == "__main__":
    main()