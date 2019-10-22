# Copyright (c) 2019 Remi Salmon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# imports
import gpxpy

import numpy as np

from datetime import datetime

from scipy.interpolate import splprep, splev

# constants
EARTH_RADIUS = 6371e3 # meters

# functions
def GPX_interpolate(lat, lon, ele, tstamp, res, deg):
    if not 1 <= deg <= 5:
        print('ERROR deg out of [1-5] range, skipping interpolation')

        return(lat, lon, ele, tstamp)

    elif not len(lat) == len(lon) == len(ele) == len(tstamp):
        print('ERROR data input size mismatch, skipping interpolation')

        return(lat, lon, ele, tstamp)

    else:
        # calculate distance data
        dist = GPX_calculate_dist(lat, lon, ele)

        # calculate normalized cumulative distance
        dist_cum_norm = np.cumsum(dist)/np.sum(dist)

        # interpolate spatial data
        data = [lat, lon, ele]

        tck, _ = splprep(x = data, u = dist_cum_norm, k = int(deg), s = 0, nest = len(lat)+deg+1)

        u_interp = np.linspace(0, 1, 1+int(np.sum(dist)/res))

        out = splev(u_interp, tck)

        lat_interp = out[0]
        lon_interp = out[1]
        ele_interp = out[2]

        # interpolate time data linearly to preserve monotonicity
        data = [tstamp, tstamp] # splprep does not accept 1D inputs...

        tck, _ = splprep(x = data, u = dist_cum_norm, k = 1, s = 0, nest = len(lat)+deg+1)

        out = splev(u_interp, tck)

        tstamp_interp = out[0]

        # remove insignificant digits
        lat_interp = np.round(lat_interp*1e6)/1e6
        lon_interp = np.round(lon_interp*1e6)/1e6
        ele_interp = np.round(ele_interp*1e1)/1e1
        tstamp_interp = np.round(tstamp_interp)

    return(lat_interp, lon_interp, ele_interp, tstamp_interp)

def GPX_calculate_dist(lat, lon, ele): # calculate distance between trackpoints
    dist = np.zeros(len(lat))

    for i in np.arange(1, len(lat)):
        lat1 = np.radians(lat[i-1])
        lon1 = np.radians(lon[i-1])
        lat2 = np.radians(lat[i])
        lon2 = np.radians(lon[i])

        # haversine formula
        delta_lat = np.abs(lat2-lat1)
        delta_lon = np.abs(lon2-lon1)

        c = 2.0*np.arcsin(np.sqrt(np.sin(delta_lat/2.0)**2+np.cos(lat1)*np.cos(lat2)*np.sin(delta_lon/2.0)**2))

        dist_lat_lon = EARTH_RADIUS*c

        # calculate elevation change
        dist_ele = ele[i]-ele[i-1]

        dist[i] = np.sqrt(dist_lat_lon**2+dist_ele**2)

    return(dist)

def GPX_read(gpx_file): # read lat, lon, ele and tstamp data from GPX file
    # initialize lists
    lat = []
    lon = []
    ele = []
    tstamp = []

    with open(gpx_file, 'r') as file:
        gpx = gpxpy.parse(file)

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    lat.append(point.latitude)
                    lon.append(point.longitude)
                    ele.append(point.elevation)
                    tstamp.append(point.time.timestamp())

    # convert to NumPy arrays
    lat = np.array(lat)
    lon = np.array(lon)
    ele = np.array(ele)
    tstamp = np.array(tstamp)

    return(lat, lon, ele, tstamp)

def GPX_write(gpx_file, lat, lon, ele, tstamp): # write interpolated data to GPX file
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_segment = gpxpy.gpx.GPXTrackSegment()

    gpx.tracks.append(gpx_track)

    gpx_track.segments.append(gpx_segment)

    for i in range(len(lat)):
        gpx_point = gpxpy.gpx.GPXTrackPoint(lat[i], lon[i], ele[i], datetime.fromtimestamp(tstamp[i]))

        gpx_segment.points.append(gpx_point)

    with open(gpx_file, 'w') as file:
        file.write(gpx.to_xml())

    return()

def CSV_write(csv_file, lat, lon, ele, tstamp): # write interpolated data to CVS file
    with open(csv_file, 'w') as file:
        file.write('lat,lon,ele,time\n') # header

        for i in range(len(lat)):
            date = datetime.fromtimestamp(tstamp[i]).strftime('%Y-%m-%dT%H:%M:%SZ') # re-format timestamp to string

            file.write(str(lat[i])+','+str(lon[i])+','+str(ele[i])+','+date+'\n')

    return()

def main():
    res = 0.5 # interpolation resolution (in meters)
    deg = 2 # interpolation degree N (N = 1 for linear interpolation, 2 <= N <= 5 for spline interpolation)

    GPX_files = glob('*.gpx')

    for GPX_file in GPX_files:
        if not GPX_file[-17:] == '_interpolated.gpx':
            print('reading '+GPX_file+'...')

            lat, lon, ele, tstamp = GPX_read(GPX_file)

            print('interpolating GPX data...')

            lat_interp, lon_interp, ele_interp, tstamp_interp = GPX_interpolate(lat, lon, ele, tstamp, res, deg)

            output_file = GPX_file[:-4]+'_interpolated.gpx'

            print('writing '+output_file+'...')

            GPX_write(output_file, lat_interp, lon_interp, ele_interp, tstamp_interp)

            print('done')

if __name__ == '__main__':
    from glob import glob

    main()
