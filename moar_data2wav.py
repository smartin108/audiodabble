""" audiodabble

    convert phone sensor data to audio

    designed to work in concert with phyphox, and specifically with csv output
    from these experiments:
        *   Acceleration (without g preferred)
        *   Gyroscope rotation rate

    Confirmed can not / will not support these experiments:
        *   Acceleration Spectrum

"""


import numpy as np
from scipy.io.wavfile import write
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from pathlib import Path


# NORMALIZE_BY = 'all' # use this to to apply normalization per data set
NORMALIZE_BY = 'col' # use this to apply normalization per column
NORMALIZE_LEVEL = -1 # dBfs to normalize to
BIT_DEPTH = 32
assert BIT_DEPTH in (16, 32)
SAMPLE_RATE = 44100

SCALE = 2**(BIT_DEPTH-1) - 1


def dB2dec(dB):
    return 10**(dB/20)


def normalize(data:np.array, normal_level):
    """ linear normalization is applied to data
        data: pass a numpy.array with at least one column
        normalization will be applied over all data
        level: max signal in return set (specify in dBfs)

    """
    max_value = np.abs(data).max()
    adjustment_factor = dB2dec(normal_level) / max_value
    return data * adjustment_factor


def get_file_content(filename:str):
    """ read & return the experiment data as numpy.array
    """
    data = np.genfromtxt(filename, delimiter=',', skip_header=1)
    return data


def get_parent_folder_name(fqpn:str):
    return Path(fqpn).parent.name


def write_converted_data(data, experiment_name, col):
    data = data * SCALE

    # it's non-obvious why 24 bit cannot be supported in this way
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html#r8b5f41f7cc22-1
    if BIT_DEPTH == 16:
        data = data.astype(np.int16)
    elif BIT_DEPTH == 32:
        data = data.astype(np.int32)
    else:
        raise ValueError(f'bit depth {BIT_DEPTH} is unsupported')
    write(f'{experiment_name}-{col}.wav', SAMPLE_RATE, data)


def main():

    Tk().withdraw()
    filename = askopenfilename()
    while filename:
        experiment_name = get_parent_folder_name(filename)

        data = get_file_content(filename=filename)

        if NORMALIZE_BY == 'all':
            data = normalize(data[:, 1:4], normal_level=NORMALIZE_LEVEL)
            for col in range(1,4):
                write_converted_data(data[:, col], experiment_name, col)
        elif NORMALIZE_BY == 'col':
            for col in range(1,4):
                data_subset = normalize(data[:, col], normal_level=NORMALIZE_LEVEL)
                write_converted_data(data_subset, experiment_name, col)
        else:
            print('what? I did not understand what to do')
        Tk().withdraw()
        filename = askopenfilename()


if __name__ == '__main__':
    main()