import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator, CubicSpline
from scipy.io.wavfile import write as wavwrite

TIME_COL = 'Time (s)'
X_COL = 'Linear Acceleration x (m/s^2)'
Y_COL = 'Linear Acceleration y (m/s^2)'
Z_COL = 'Linear Acceleration z (m/s^2)'
ABS_COL = 'Absolute acceleration (m/s^2)'

def phyphox_accel_to_wav(
    csv_path: str,
    wav_path: str,
    expansion_factor: float,
    out_rate: int = 44100,
    interp: str = "pchip",   # "pchip" (recommended) or "cubic"
    mode: str = "xyz",       # "xyz" or "abs"
    normalize: bool = True,
    dc_remove: bool = True,
):
    df = pd.read_csv(csv_path)

    # time and data
    t = df[TIME_COL].to_numpy(dtype=float)

    # sort by time, drop duplicates
    order = np.argsort(t)
    t = t[order]

    if mode.lower() == "abs":
        y = df[ABS_COL].to_numpy(dtype=float)[order]
        data = y.reshape(-1, 1)
    else:
        x = df[X_COL].to_numpy(dtype=float)[order]
        y = df[Y_COL].to_numpy(dtype=float)[order]
        z = df[Z_COL].to_numpy(dtype=float)[order]
        data = np.column_stack([x, y, z])

    # drop NaNs
    good = np.isfinite(t) & np.all(np.isfinite(data), axis=1)
    t = t[good]
    data = data[good]

    # unique time stamps (keep first)
    _, uniq_idx = np.unique(t, return_index=True)
    t = t[uniq_idx]
    data = data[uniq_idx]

    if len(t) < 4:
        raise ValueError("Not enough samples to interpolate after cleaning.")

    # estimate input sample rate
    dt = np.diff(t)
    fs_in = 1.0 / np.median(dt)
    ratio = out_rate / fs_in
    print(f"Estimated fs_in ≈ {fs_in:.3f} Hz")
    print(f"out_rate/fs_in ≈ {ratio:.2f} (this is your raw 'speed-up' factor)")

    # build output time axis (expanded)
    dur_in = t[-1] - t[0]
    dur_out = dur_in * expansion_factor
    n_out = int(np.floor(dur_out * out_rate)) + 1
    t_out = np.linspace(0.0, dur_out, n_out)

    # map output times back into input time for interpolation
    t_in_equiv = t[0] + (t_out / expansion_factor)

    # interpolate each channel
    y_out = np.zeros((n_out, data.shape[1]), dtype=np.float64)

    for c in range(data.shape[1]):
        y = data[:, c].astype(np.float64)

        if dc_remove:
            y = y - np.mean(y)

        if interp.lower() == "cubic":
            f = CubicSpline(t, y, bc_type="natural")
        else:
            f = PchipInterpolator(t, y)

        y_out[:, c] = f(t_in_equiv)

    # normalize to int16
    if normalize:
        peak = np.max(np.abs(y_out))
        if peak > 0:
            y_out /= peak

    pcm = np.clip(y_out, -1.0, 1.0)
    pcm16 = (pcm * 32767.0).astype(np.int16)

    # mono needs shape (N,), not (N,1)
    if pcm16.shape[1] == 1:
        pcm16 = pcm16[:, 0]

    wavwrite(wav_path, out_rate, pcm16)

    effective_speedup = (out_rate / fs_in) / expansion_factor
    print(f"Wrote {wav_path}")
    print(f"expansion_factor E = {expansion_factor:.3f}")
    print(f"Effective playback speedup ≈ {effective_speedup:.3f}× (1.0× means ~real time)")

# --- Example usage ---
# First run once to see fs_in, then choose E.
# A good starting point for ~real-time reconstruction is:
#   E ≈ out_rate / fs_in  (script prints out_rate/fs_in)

phyphox_accel_to_wav(
    csv_path=r"C:\Users\Z40\Documents\git\audiodabble\acceleration_air_filter\Raw Data.csv",
    wav_path="accel_xyz_pchip.wav",
    expansion_factor=787.5,   # rough if fs_in ~ 56 Hz
    out_rate=44100,
    interp="pchip",
    mode="xyz",
)


if __name__ == '__main__':
    print('this version was a chatgpt mistake')
