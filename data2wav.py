import numpy as np
from scipy.io.wavfile import write

# Sample rate (samples per second)
sample_rate = 44100

# Generate a 1-second sine wave at 440 Hz (A4 note)
t = np.linspace(0, 1, sample_rate, False)  # 1 second
frequency = 440  # Hz
amplitude = 32767  # Max amplitude for int16
data = amplitude * np.sin(2 * np.pi * frequency * t)

# Ensure your data is in the correct format (int16)
data = data.astype(np.int16)

# Write the data to a .wav file
write('output.wav', sample_rate, data)

print("WAV file created successfully.")
