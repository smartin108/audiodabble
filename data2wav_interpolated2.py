import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator, CubicSpline
from scipy.io.wavfile import write as wavwrite

TIME_COL = 'Time (s)'
X_COL = 'Linear Acceleration x (m/s^2)'
Y_COL = 'Linear Acceleration y (m/s^2)'
Z_COL = 'Linear Acceleration z (m/s^2)'
ABS_COL = 'Absolute acceleration (m/s^2)'

def phyphox_to_wav_fixed(
    csv_path: str,
    wav_path: str,
    out_rate: int = 44100,
    speed: float = 10.0,          # 1.0 = real time; 2.0 = 2× faster; 0.5 = half speed
    interp: str = "pchip",       # "pchip" (recommended) or "cubic"
    mode: str = "xyz",           # "xyz" or "abs"
    normalize: bool = True,
    dc_remove: bool = True,
    dtype=np.float32,            # saves RAM; float32 is plenty here
):
    df = pd.read_csv(csv_path)

    t = df[TIME_COL].to_numpy(dtype=float)
    order = np.argsort(t)
    t = t[order]

    if mode.lower() == "abs":
        data = df[ABS_COL].to_numpy(dtype=float)[order].reshape(-1, 1)
    else:
        x = df[X_COL].to_numpy(dtype=float)[order]
        y = df[Y_COL].to_numpy(dtype=float)[order]
        z = df[Z_COL].to_numpy(dtype=float)[order]
        data = np.column_stack([x, y, z])

    good = np.isfinite(t) & np.all(np.isfinite(data), axis=1)
    t = t[good]
    data = data[good]

    _, uniq_idx = np.unique(t, return_index=True)
    t = t[uniq_idx]
    data = data[uniq_idx]

    if len(t) < 4:
        raise ValueError("Not enough samples to interpolate after cleaning.")

    dur_in = t[-1] - t[0]
    if dur_in <= 0:
        raise ValueError("Non-positive duration; check timestamps.")

    # Output duration is scaled by speed:
    # speed=1 => same duration; speed=2 => half duration; speed=0.5 => double duration
    dur_out = dur_in / speed
    n_out = int(np.floor(dur_out * out_rate)) + 1

    print(f"Input duration: {dur_in:.3f} s, output duration: {dur_out:.3f} s")
    print(f"Output samples: {n_out:,}  (~{n_out*out_rate**0*0} samples)")

    # Output sample times (in output/playback time)
    t_out = np.arange(n_out, dtype=np.float64) / out_rate

    # Map output time back into input-time coordinates for interpolation
    # At speed=2, you traverse the input twice as fast, so t_in_equiv increases faster.
    t_in_equiv = t[0] + t_out * speed

    y_out = np.zeros((n_out, data.shape[1]), dtype=dtype)

    for c in range(data.shape[1]):
        y = data[:, c].astype(np.float64)
        if dc_remove:
            y = y - np.mean(y)

        if interp.lower() == "cubic":
            f = CubicSpline(t, y, bc_type="natural")
        else:
            f = PchipInterpolator(t, y)

        y_out[:, c] = f(t_in_equiv).astype(dtype)

    if normalize:
        peak = float(np.max(np.abs(y_out)))
        if peak > 0:
            y_out = (y_out / peak).astype(dtype)

    pcm16 = np.clip(y_out, -1.0, 1.0)
    pcm16 = (pcm16 * 32767.0).astype(np.int16)

    if pcm16.shape[1] == 1:
        pcm16 = pcm16[:, 0]

    wavwrite(wav_path, out_rate, pcm16)
    print(f"Wrote: {wav_path}")

phyphox_to_wav_fixed(
    csv_path=r"C:\Users\Z40\Documents\git\audiodabble\acceleration_air_filter\Raw Data.csv",
    wav_path="accel_xyz_pchip.wav",
    speed=20.0,
    out_rate=44100,
    interp="pchip",
    mode="xyz",
)