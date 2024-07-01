import numpy as np
from scipy.io.wavfile import write




def get_file_content(col=1):
    data = np.genfromtxt(myfile, delimiter=',', skip_header=1)
    return data[:, col]

sample_rate = 44100
amplitude = 32767
counter = 1

for file in range(1,3):
    for col in range(1,4):
        myfile = f'Raw Data {file}.csv'
        data = get_file_content(col=col)
        data = amplitude * data
        data = data.astype(np.int16)
        write(f'output {counter}.wav', sample_rate, data)
        counter += 1
