# GPX_interpolate.py

Python script to batch interpolate GPX files (latitude, longitude, elevation, time) using linear/B-splines interpolation

## Usage:

* Copy GPX files to the current directory
* Run `python3 GPX_interpolate.py`
* The interpolated GPX data is saved to a CSV file of the same name (`file.gpx` -> `file.csv`)

In `GPX_interpolate.py`, set:

`interpolate_res`: the interpolation resolution (in meters)

`interpolate_deg`: the B-spline degree (set `interpolate_deg = 1` for linear interpolation)

Example with `interpolate_res = 1; interpolate_deg = 2`:

![plot.png](plot.png)

## Python dependencies:

```
* Python >= 3.7.0
* NumPy >= 1.15.4
* SciPy >= 1.1.0
```

## Todo:

* Add command-line arguments for `GPX_files`, `interpolate_res` and `interpolate_deg`
* Implement `GPX_write()` function
