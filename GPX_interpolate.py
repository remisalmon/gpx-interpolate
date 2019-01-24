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
import re
import datetime

import numpy as np
import scipy.interpolate as sp

# parameters
interpolate_res = 1 # interpolation resolution in meters
interpolate_deg = 2 # interpolation degree N (N = 1 for linear interpolation, 2 <= N <= 5 for B-spline interpolation)

# functions
def GPX_read(file): # read lat, lon, ele and timestamps data from GPX file
    # initialize lists
    lat = []
    lon = []
    ele = []
    timestamps = []

    gpx_read_time = False # don't read first <time> field (metadata)

    # read file
    with open(file, 'r') as f:
        for line in f:
            # get trackpoints latitude, longitude
            if '<trkpt' in line:
                tmp = re.findall('-?\d*\.?\d+', line)

                lat.append(float(tmp[0]))
                lon.append(float(tmp[1]))

            # get trackpoints elevation
            elif '<ele' in line:
                tmp = re.findall('\d+\.\d+', line)

                ele.append(float(tmp[0]))

            # get trackpoints timestamp
            elif '<time' in line:
                tmp = re.findall('\d+.*Z', line)

                date = datetime.datetime.strptime(tmp[0], '%Y-%m-%dT%H:%M:%SZ') # format string to datetime object

                if gpx_read_time:
                    timestamps.append(date.timestamp())
                else:
                    gpx_read_time = True

    # convert to NumPy arrays
    lat = np.array(lat)
    lon = np.array(lon)
    ele = np.array(lat)
    timestamps = np.array(timestamps)

    return(lat, lon, ele, timestamps)

def GPX_write(file, lat_new, lon_new, ele_new, timestamps_new): # write interpolated data to GPX file
    # TODO

    return

def CSV_write(file, lat_new, lon_new, ele_new, timestamps_new): # write interpolated data to CVS file
    with open(file, 'w') as file:
        file.write('lat,lon,ele,time\n') # header

        for t in range(len(lat_new)):
            date = datetime.datetime.fromtimestamp(timestamps_new[t]).strftime('%Y-%m-%dT%H:%M:%SZ') # re-format timestamp to string

            file.write(str(lat_new[t])+','+str(lon_new[t])+','+str(ele_new[t])+','+date+'\n')

    return

def GPX_calculate_dist(lat, lon, ele): # calculate distance between trackpoints
    dist = np.zeros(lat.shape)

    for t in range(len(lat)-1):
        lat1 = np.radians(lat[t])
        lat2 = np.radians(lat[t+1])
        lon1 = np.radians(lon[t])
        lon2 = np.radians(lon[t+1])

        # haversine formula
        delta_lat = lat2-lat1
        delta_lon = lon2-lon1

        a = np.power(np.sin(delta_lat/2), 2)+np.cos(lat1)*np.cos(lat2)*np.power(np.sin(delta_lon/2), 2)
        c = 2.0*np.arctan2(np.sqrt(a), np.sqrt(1-a))

        dist[t+1] = 6371e3*c

    return(dist)

def GPX_interpolate(lat, lon, ele, timestamps, interpolate_res, interpolate_deg):
    # get distance data
    dist = GPX_calculate_dist(lat, lon, ele)

    # calculate normalized cumulative distance
    norm_cum_dist = np.cumsum(dist)/np.sum(dist)

    # interpolate
    if interpolate_deg > 1 and interpolate_deg <= 5: # B-spline interpolation
        data = (lat, lon, ele)

        (tck, u) = sp.splprep(x = data, u = norm_cum_dist, k = interpolate_deg, s = 0, nest = len(lat)+interpolate_deg+1)

        unew = np.linspace(0, 1, int(dist.sum()/interpolate_res+1))

        out = sp.splev(unew, tck)

        lat_new = out[0]
        lon_new = out[1]
        ele_new = out[2]

        # interpolate timestamps linearly to preserve monotonicity
        data = (timestamps, timestamps) # splprep does not accept 1D inputs...

        (tck, u) = sp.splprep(x = data, u = norm_cum_dist, k = 1, s = 0, nest = len(lat)+1+1)

        out = sp.splev(unew, tck)

        timestamps_new = out[0]

    elif interpolate_deg == 1: # linear interpolation
        data = (lat, lon, ele, timestamps)

        (tck, u) = sp.splprep(x = data, u = norm_cum_dist, k = interpolate_deg, s = 0, nest = len(lat)+interpolate_deg+1)

        unew = np.linspace(0, 1, int(dist.sum()/interpolate_res+1))

        out = sp.splev(unew, tck)

        lat_new = out[0]
        lon_new = out[1]
        ele_new = out[2]
        timestamps_new = out[3]

    else: # default to input arguments if parameters are out of range
        lat_new = lat
        lon_new = lon
        ele_new = ele
        timestamps_new = timestamps

    return(lat_new, lon_new, ele_new, timestamps_new)

def main():
    GPX_files = glob.glob('*.gpx')

    for file in GPX_files:
        print('reading '+file+'...')
        (lat, lon, ele, timestamps) = GPX_read(file)

        print('interpolating GPX data...')
        (lat_new, lon_new, ele_new, timestamps_new) = GPX_interpolate(lat, lon, ele, timestamps, interpolate_res, interpolate_deg)

        file_interp = file[:-4]+'_interpolated.csv'

        print('writing '+file_interp+'...')

        CSV_write(file_interp, lat_new, lon_new, ele_new, timestamps_new)

        print('done!')

if __name__ == '__main__':
    # execute only if run as a script
    main()
