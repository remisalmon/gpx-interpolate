"""
GPX_interpolate.py

Remi Salmon, 2018
salmon.remi@gmail.com
"""

#!/usr/bin/env python3

# imports
import glob
import re
import datetime
import math

import numpy as np
import scipy.interpolate as sp
import matplotlib.pyplot as plt # debug

# global variables
interpolate_res = 1 # interpolation resolution in meters
interpolate_deg = 2 # interpolation degree N (N = 1 for linear interpolation, 2 < N <= 5 for B-spline interpolation)

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

                tmp = datetime.datetime.strptime(tmp[0], '%Y-%m-%dT%H:%M:%SZ')

                if gpx_read_time:
                    timestamps.append(tmp.timestamp())
                else:
                    gpx_read_time = True

    # convert to NumPy arrays
    lat = np.array(lat)
    lon = np.array(lon)
    ele = np.array(lat)
    timestamps = np.array(timestamps)

    return(lat, lon, ele, timestamps)

def GPX_write(file, file_new, lat_new, lon_new, ele_new, timestamps_new): # write interpolated data to GPX file
    #file_new = file[:-4]+'_interpolated.gpx'

    # TODO

    return

def CSV_write(file, lat_new, lon_new, ele_new, timestamps_new): # write interpolated data to CVS file
    file_new = file[:-4]+'_interpolated.csv'

    with open(file_new, 'w') as f:
        for t in range(len(lat_new)):
            date = datetime.datetime.fromtimestamp(timestamps_new[t]).strftime('%Y-%m-%dT%H:%M:%SZ')

            f.write(str(lat_new[t])+','+str(lon_new[t])+','+str(ele_new[t])+','+date+'\n')

    return

def GPX_calculate_dist(lat, lon, ele): # calculate distance between trackpoints
    dist = np.zeros(lat.shape)

    for t in range(len(lat)-1):
        lat1 = math.radians(lat[t])
        lat2 = math.radians(lat[t+1])
        lon1 = math.radians(lon[t])
        lon2 = math.radians(lon[t+1])

        # haversine formula
        delta_lat = lat2-lat1
        delta_lon = lon2-lon1

        a = math.pow(math.sin(delta_lat/2), 2)+math.cos(lat1)*math.cos(lat2)*math.pow(math.sin(delta_lon/2), 2)
        c = 2.0*math.atan2(math.sqrt(a), math.sqrt(1-a))

        dist[t+1] = (6371e3)*c

    return(dist)

def calculate_norm_cum_dist(dist): # calculate normalized cumulative distance from distance data
    norm_cum_dist = np.zeros(dist.shape)

    for t in range(len(dist)-1):
        norm_cum_dist[t+1] = norm_cum_dist[t]+dist[t+1]

    norm_cum_dist = norm_cum_dist/dist.sum()

    return(norm_cum_dist)

def GPX_interpolate(lat, lon, ele, timestamps, interpolate_res, interpolate_deg):
    # get distance data
    dist = GPX_calculate_dist(lat, lon, ele)

    # get normalized cumulative distance
    norm_cum_dist = calculate_norm_cum_dist(dist)

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

    return(lat_new, lon_new, ele_new, timestamps_new)

def main():
    GPX_files = glob.glob('*.gpx')

    for file in GPX_files:
        print('reading '+file+'...')
        (lat, lon, ele, timestamps) = GPX_read(file)

        # downsample for testing
        lat = lat[::60]
        lon = lon[::60]
        ele = ele[::60]
        timestamps = timestamps[::60]

        print('interpolating GPX data...')
        (lat_new, lon_new, ele_new, timestamps_new) = GPX_interpolate(lat, lon, ele, timestamps, interpolate_res, interpolate_deg)

        #print('writing '+file[:-4]+'_interpolated.gpx...')
        #GPX_write(file, lat_new, lon_new, ele_new, timestamps_new)

        print('writing '+file[:-4]+'_interpolated.csv...')
        CSV_write(file, lat_new, lon_new, ele_new, timestamps_new)

        print('done!')

        plt.figure()
        plt.plot((6371e3)*np.radians(lon_new), (6371e3)*np.log(np.tan(np.radians(lat_new)/2+math.pi/4)), 'r', marker = None)
        plt.scatter((6371e3)*np.radians(lon), (6371e3)*np.log(np.tan(np.radians(lat)/2+math.pi/4)), c = 'black', marker = '.')
        plt.axis('equal')
        plt.show()

if __name__ == '__main__':
    # execute only if run as a script
    main()
