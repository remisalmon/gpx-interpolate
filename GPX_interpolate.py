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
import glob
import gpxpy
import datetime

import numpy as np
import scipy.interpolate as sp

# functions
def GPX_read(gpx_file): # read lat, lon, ele and timestamps data from GPX file
    # initialize lists
    lat = []
    lon = []
    ele = []
    timestamps = []

    with open(gpx_file, 'r') as file:
        gpx = gpxpy.parse(file)

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    lat.append(point.latitude)
                    lon.append(point.longitude)
                    ele.append(point.elevation)
                    timestamps.append(point.time.timestamp())

    # convert to NumPy arrays
    lat = np.array(lat)
    lon = np.array(lon)
    ele = np.array(lat)
    timestamps = np.array(timestamps)

    return(lat, lon, ele, timestamps)

def GPX_write(gpx_file, lat_new, lon_new, ele_new, timestamps_new): # write interpolated data to GPX file
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for i in range(lat_new.shape[0]):
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat_new[i], lon_new[i], ele_new[i], datetime.datetime.fromtimestamp(timestamps_new[i])))

    with open(gpx_file, 'w') as file:
        file.write(gpx.to_xml())

    return

def CSV_write(csv_file, lat_new, lon_new, ele_new, timestamps_new): # write interpolated data to CVS file
    with open(csv_file, 'w') as file:
        file.write('lat,lon,ele,time\n') # header

        for i in range(lat_new.shape[0]):
            date = datetime.datetime.fromtimestamp(timestamps_new[i]).strftime('%Y-%m-%dT%H:%M:%SZ') # re-format timestamp to string

            file.write(str(lat_new[i])+','+str(lon_new[i])+','+str(ele_new[i])+','+date+'\n')

    return

def GPX_calculate_dist(lat, lon, ele): # calculate distance between trackpoints
    dist = np.zeros(lat.shape)

    for i in np.arange(1, lat.shape[0]):
        lat1 = np.radians(lat[i-1])
        lat2 = np.radians(lat[i])
        lon1 = np.radians(lon[i-1])
        lon2 = np.radians(lon[i])

        # haversine formula
        delta_lat = lat2-lat1
        delta_lon = lon2-lon1

        a = np.power(np.sin(delta_lat/2.0), 2)+np.cos(lat1)*np.cos(lat2)*np.power(np.sin(delta_lon/2.0), 2)
        c = 2.0*np.arctan2(np.sqrt(a), np.sqrt(1.0-a))

        dist[i] = 6371e3*c

    return(dist)

def GPX_interpolate(lat, lon, ele, timestamps, interpolate_res, interpolate_deg):
    # get distance data
    dist = GPX_calculate_dist(lat, lon, ele)

    # calculate normalized cumulative distance
    norm_cum_dist = np.cumsum(dist)/np.sum(dist)

    # interpolate
    if interpolate_res <= 0:
        print('WARNING: interpolate_res must be positive, skipping interpolation')
        lat_new = lat
        lon_new = lon
        ele_new = ele
        timestamps_new = timestamps

    elif interpolate_deg < 1 or interpolate_deg > 5:
        print('WARNING: interpolate_deg out of [1-5] range, skipping interpolation')
        lat_new = lat
        lon_new = lon
        ele_new = ele
        timestamps_new = timestamps

    else:
        data = (lat, lon, ele)

        (tck, u) = sp.splprep(x = data, u = norm_cum_dist, k = interpolate_deg, s = 0, nest = lat.shape[0]+interpolate_deg+1)

        unew = np.linspace(0, 1, int(dist.sum()/interpolate_res+1))

        out = sp.splev(unew, tck)

        lat_new = out[0]
        lon_new = out[1]
        ele_new = out[2]

        # ensure we interpolate timestamps linearly to preserve monotonicity
        data = (timestamps, timestamps) # splprep does not accept 1D inputs...

        (tck, u) = sp.splprep(x = data, u = norm_cum_dist, k = 1, s = 0, nest = lat.shape[0]+1+1)

        out = sp.splev(unew, tck)

        timestamps_new = out[0]

    return(lat_new, lon_new, ele_new, timestamps_new)

def main():
    # parameters
    interpolate_res = 5 # interpolation resolution in meters
    interpolate_deg = 2 # interpolation degree N (N = 1 for linear interpolation, 2 <= N <= 5 for B-spline interpolation)

    GPX_files = glob.glob('*.gpx')

    for gpx_file in GPX_files:
        print('reading '+gpx_file+'...')
        (lat, lon, ele, timestamps) = GPX_read(gpx_file)

        print('interpolating GPX data...')
        (lat_new, lon_new, ele_new, timestamps_new) = GPX_interpolate(lat, lon, ele, timestamps, interpolate_res, interpolate_deg)

        output_file = gpx_file[:-4]+'_interpolated.gpx'

        print('writing '+output_file+'...')

        GPX_write(output_file, lat_new, lon_new, ele_new, timestamps_new)

        output_file = gpx_file[:-4]+'_interpolated.csv'

        print('writing '+output_file+'...')

        CSV_write(output_file, lat_new, lon_new, ele_new, timestamps_new)

        print('done!')

if __name__ == '__main__':
    # execute only if run as a script
    main()
