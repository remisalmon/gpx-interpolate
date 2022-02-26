# gpx_interpolate.py

Python script to interpolate GPX files using piecewise cubic Hermite splines.

Interpolates latitude, longitude, elevation and speed at any spatial resolution.

## Usage

### Script
```
usage: gpx_interpolate.py [-h] [-r RES] [-n NUM] [-s] FILE [FILE ...]

interpolate GPX files using piecewise cubic Hermite splines

positional arguments:
  FILE               GPX file

optional arguments:
  -h, --help         show this help message and exit
  -r RES, --res RES  interpolation resolution in meters (default: 1)
  -n NUM, --num NUM  force point count in output (default: disabled)
  -s, --speed        save interpolated speed
```

### Module
```python
from gpx_interpolate import gpx_interpolate

gpx_data = {'lat':lat,
            'lon':lon,
            'ele':ele,
            'tstamp':tstamp,
            'tzinfo':tzinfo}

gpx_data_interp = gpx_interpolate(gpx_data, res = 1.0, num = 0)
```

where:
* `lat`, `lon` are the trackpoints latitude and longitude (in degree)
* `ele` (optional) is the trackpoints elevation (in meter)
* `tstamp` (optional) is the trackpoints timestamps (in second)
* `tzinfo` (optional) is the trackpoints timezone as a `datetime.tzinfo` subclass instance (`None` for UTC)
* `res` (optional) is the interpolation resolution in meters: disabled if `num > 0`
* `num` (optional) is the number of trackpoints of the interpolated data: `0` to disable (default)

`ele`, `tstamp` and `tzinfo` are optional and in that case must be set to `None`

### Example
:black_circle: = input GPX data, :red_circle: = interpolated GPX data  
![plot.png](plot.png)

## Tests

Run `test/test.sh`

## Requirements
```
gpxpy==1.5.0
scipy==1.8.0
numpy==1.22.2
```
