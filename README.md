# gpx_interpolate.py

Python script to interpolate GPX files using linear or spline interpolation

Interpolate latitude, longitude, elevation and speed at any spatial resolution

## Usage

### Script
```
usage: gpx_interpolate.py [-h] [-d DEG] [-r RES] [-s] FILE [FILE ...]

positional arguments:
  FILE               GPX file(s)

optional arguments:
  -h, --help         show this help message and exit
  -d DEG, --deg DEG  interpolation degree, 1=linear, 2-5=spline (default: 1)
  -r RES, --res RES  interpolation resolution in meters (default: 1)
  -s, --speed        Save interpolated speed
```

### Module
```python
from gpx_interpolate import gpx_interpolate

gpx_data = {'lat':lat,
            'lon':lon,
            'ele':ele,
            'tstamp':tstamp,
            'tzinfo':tzinfo}

gpx_data_interp = gpx_interpolate(gpx_data, res, deg)
```

where:  
`lat`, `lon` and `ele` (optional) are the trackpoints latitude, longitude and elevation  
`tstamp` (optional) is the trackpoints POSIX time  
`tzinfo` (optional) is the timezone in `datetime.tzinfo` format (`None` for UTC)  
`res` is the interpolation resolution in meters  
`deg` is the interpolation in degree: `1` for linear interpolation (default) or `2-5` for spline interpolation  

`ele`, `tstamp` and `tzinfo` are optional and can be set to `None`

### Example
:black_circle: = input GPX data, :red_circle: = interpolated GPX data  
![plot.png](plot.png)

## Requirements
```
gpxpy==1.4.2
scipy==1.5.4
numpy==1.19.4
```
