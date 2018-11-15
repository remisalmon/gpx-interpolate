# GPX_interpolate.py

Interpolate GPS data (latitude, longitude, elevation, time) using linear/B-splines interpolation

## Usage:

* Add a GPX file `file.gpx` to the current directory
* Run `python3 GPX_interpolate.py`
* The interpolated GPS data is saved to a CSV file `file_interpolated.csv` in the current directory

Example with `interpolate_deg = 2`:

![plot.png](plot.png)

## Python dependencies:

* Python 3 (tested with Python 3.7.0)
* NumPy
* SciPy

## ToDo:

* Implement `GPX_write()` function
