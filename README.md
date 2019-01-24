# GPX_interpolate.py

Python script to batch interpolate GPX files (latitude, longitude, elevation, time) using linear/B-splines interpolation

## Usage

* Copy your GPX files to the current directory
* Run `python3 GPX_interpolate.py`
* The interpolated GPX data is saved to a new `_interpolated.gpx` GPX file and a `_interpolated.csv` CSV file

In `GPX_interpolate.py`, set:

`interpolate_res`: the interpolation resolution (in meters)

`interpolate_deg`: the B-spline degree (between 2 and 5, set to 1 for linear interpolation)

Example with `interpolate_res = 1; interpolate_deg = 2`:  
![plot.png](plot.png)

## Python dependencies

```
* Python >= 3.7.1
* NumPy >= 1.15.4
* SciPy >= 1.1.0
* gpxpy >= 1.3.4
```
