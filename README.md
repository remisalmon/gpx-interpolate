# GPX_interpolate.py

Interpolate GPS data (latitude, longitude, elevation, time) using linear/B-splines interpolation

## Usage:

* Add a GPX file `file.gpx` to the current directory
* Run `python3 GPX_interpolate.py`
* The interpolated GPS data is saved to a CSV file `file_interpolated.csv` in the current directory

In `GPX_interpolate.py`:

`interpolate_res` is the interpolation resolution in meters

`interpolate_deg` is the B-spline degree (use `interpolate_deg = 1` for linear interpolation)

Example with `interpolate_res = 1` and `interpolate_deg = 2`:

![plot.png](plot.png)

## Python dependencies:

* Python 3 (tested with Python 3.7.0)
* NumPy
* SciPy

## ToDo:

* Add command-line arguments for `GPX_files`, `interpolate_res` and `interpolate_deg`
* Implement `GPX_write()` function
