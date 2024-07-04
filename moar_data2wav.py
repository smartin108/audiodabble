import numpy as np
from scipy.io.wavfile import write
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from pathlib import Path


def dB2dec(dB):
    return 10**(dB/20)


def dec2dB(dec):
    return 20 * np.log10(dec)


def get_file_content(filename:str, col=1, norm=-3):
    data = np.genfromtxt(filename, delimiter=',', skip_header=1)
    if norm:
        max_value = np.abs(data[:, col]).max() # normalize per-channel
        # max_value = np.abs(data[:, 1:4]).max() # normalize per-data set
    adjustment_factor = dB2dec(norm) / max_value
    print(max_value, dB2dec(norm), adjustment_factor)
    return data[:, col] * adjustment_factor


def get_parent_folder_name(fqpn:str):
    return Path(fqpn).parent.name


bit_depth = 16
sample_rate = 44100
amplitude = 2**(bit_depth-1) - 1
# amplitude = 32767
counter = 1

Tk().withdraw()
filename = askopenfilename()
experiment_name = get_parent_folder_name(filename)

for col in range(1,4):
    data = get_file_content(filename=filename, col=col)
    data = amplitude * data
    data = data.astype(np.int16)
    outfile_name = f'{experiment_name}.csv'
    write(f'{experiment_name}-{counter}.wav', sample_rate, data)
    counter += 1
