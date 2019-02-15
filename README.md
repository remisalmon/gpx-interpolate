# GPX_interpolate.py

Python function to interpolate GPX data (latitude, longitude, elevation, time) using linear or spline interpolation

## Usage

### GPX_interpolate() function

`(lat_interp, lon_interp, ele_interp, tstamps_interp) = GPX_interpolate(lat, lon, ele, tstamps, res, deg)`

where:

`lat`, `lon` and `ele` are numpy arrays of the GPX latitude, logitude and elevation data  
`tstamps` is a numpy array of the timestamps of the GPX time data (in seconds)  
`res` is the interpolation spatial resolution (in meters)  
`deg` is the interpolation polynomial resolution (1 for linear interpolation, 2-5 for spline interpolation)

### GPX_interpolate.py script

To run interactively:

* Copy your GPX files to the current directory
* Run `python3 GPX_interpolate.py`
* The interpolated GPX data is saved to a new `_interpolated.gpx` GPX file and a `_interpolated.csv` CSV file

In `GPX_interpolate.py`, set:

`interpolate_res`: the interpolation resolution (in meters)

`interpolate_deg`: the B-spline degree (between 2 and 5, set to 1 for linear interpolation)

### Example
With `interpolate_res = 1; interpolate_deg = 2`:  
![plot.png](plot.png)

## Python dependencies

```
* numpy >= 1.15.4
* scipy >= 1.1.0
* gpxpy >= 1.3.4
```
