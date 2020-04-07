# gpx_interpolate.py

Python module/script to interpolate GPX files using linear or spline interpolation

Interpolate latitude, longitude, elevation and time stamps at any spatial resolution

## Usage

### Module

```python
from gpx_interpolate import gpx_interpolate

lat_interp, lon_interp, ele_interp, tstamp_interp = gpx_interpolate(lat, lon, ele, tstamp, res, deg)
```

where:
`lat`, `lon` and `ele` are the GPX latitude, longitude and elevation data (array-like)  
`tstamp` is the GPX time data in epoch time (array-like)  
`res` is the interpolation spatial resolution in meters (float)  
`deg` is the interpolation polynomial degree: `1` for linear interpolation (default) or `2-5` for spline interpolation (int)

### Script

```
usage: gpx_interpolate.py [-h] [-d DEG] [-r RES] FILE [FILE ...]

Interpolate GPX file(s) using linear/spline interpolation

positional arguments:
  FILE               GPX file(s)

optional arguments:
  -h, --help         show this help message and exit
  -d DEG, --deg DEG  Interpolation degree, 1=linear, 2-5=spline (default: 1)
  -r RES, --res RES  Interpolation resolution in meters (default: 1)
```

### Example
With `res = 1, deg = 2` (:black_circle: = original GPX data, :red_circle: = interpolated data):
![plot.png](plot.png)

## Python dependencies

```
numpy==1.18.1
scipy==1.4.1
gpxpy==1.4.0
```
