# GPX_interpolate.py

Python function to interpolate GPX data (latitude, longitude, elevation, time) using linear or spline interpolation

## Usage

### GPX_interpolate() function

```python
from GPX_interpolate import GPX_interpolate

lat_interp, lon_interp, ele_interp, tstamp_interp = GPX_interpolate(lat, lon, ele, tstamp, res, deg)
```

where:  
`lat`, `lon` and `ele` are the GPX latitude, logitude and elevation data (Nx1 NumPy arrays)  
`tstamp` is the GPX time data in epoch time (Nx1 NumPy array)  
`res` is the interpolation spatial resolution (in meters)  
`deg` is the interpolation polynomial resolution (`1` for linear interpolation, `2-5` for spline interpolation)

### GPX_interpolate.py script

To run as a script:

* Copy your GPX file(s) to the current directory
* Run `python3 GPX_interpolate.py`
* The interpolated GPX data is saved to a new `_interpolated.gpx` GPX file

In `GPX_interpolate.py`, set:

`interpolate_res`: the interpolation resolution (in meters)  
`interpolate_deg`: the interpolation polynomial resolution (`1` for linear interpolation, `2-5` for B-spline interpolation)

### Example
With `interpolate_res = 1; interpolate_deg = 2` (:black_circle: = original GPX data, :red_circle: = interpolated data):  
![plot.png](plot.png)

## Python dependencies

```
* numpy >= 1.15.4
* scipy >= 1.1.0
* gpxpy >= 1.3.4
```
