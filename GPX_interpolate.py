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
def GPX_interpolate(lat, lon, ele, tstamp, interpolate_res, interpolate_deg):
    if not 1 <= interpolate_deg <= 5:
        print('ERROR: interpolate_deg out of [1-5] range, skipping interpolation')

        lat_new = lat
        lon_new = lon
        ele_new = ele
        tstamp_new = tstamp

    else:
        # calculate distance data
        dist = GPX_calculate_dist(lat, lon, ele)

        # calculate normalized cumulative distance
        norm_cum_dist = np.cumsum(dist)/np.sum(dist)

        # interpolate spatial data
        data = (lat, lon, ele)

        (tck, u) = sp.splprep(x = data, u = norm_cum_dist, k = interpolate_deg, s = 0, nest = lat.shape[0]+interpolate_deg+1)

        unew = np.linspace(0, 1, int(dist.sum()/interpolate_res+1))

        out = sp.splev(unew, tck)

        lat_new = out[0]
        lon_new = out[1]
        ele_new = out[2]

        # interpolate time data linearly to preserve monotonicity
        data = (tstamp, tstamp) # splprep does not accept 1D inputs...

        (tck, u) = sp.splprep(x = data, u = norm_cum_dist, k = 1, s = 0, nest = lat.shape[0]+1+1)

        out = sp.splev(unew, tck)

        tstamp_new = out[0]

        # remove insignificant digits
        lat_new = np.round(lat_new*1e6)/1e6
        lon_new = np.round(lon_new*1e6)/1e6
        ele_new = np.round(ele_new*1e1)/1e1
        #tstamp_new = np.round(tstamp_new) # uncomment to round tstamp_new to seconds

    return(lat_new, lon_new, ele_new, tstamp_new)

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

        delta_d = 6371e3*c

        # calculate elevation change
        delta_ele = ele[i]-ele[i-1]

        dist[i] = np.sqrt(np.power(delta_d, 2)+np.power(delta_ele, 2))

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

def GPX_write(gpx_file, lat_new, lon_new, ele_new, tstamp_new): # write interpolated data to GPX file
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for i in range(lat_new.shape[0]):
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat_new[i], lon_new[i], ele_new[i], datetime.datetime.fromtimestamp(tstamp_new[i])))

    with open(gpx_file, 'w') as file:
        file.write(gpx.to_xml())

    return

def CSV_write(csv_file, lat_new, lon_new, ele_new, tstamp_new): # write interpolated data to CVS file
    with open(csv_file, 'w') as file:
        file.write('lat,lon,ele,time\n') # header

        for i in range(lat_new.shape[0]):
            date = datetime.datetime.fromtimestamp(tstamp_new[i]).strftime('%Y-%m-%dT%H:%M:%SZ') # re-format timestamp to string

            file.write(str(lat_new[i])+','+str(lon_new[i])+','+str(ele_new[i])+','+date+'\n')

    return

def main():
    interpolate_res = 0.5 # interpolation resolution (in meters)
    interpolate_deg = 2 # interpolation degree N (N = 1 for linear interpolation, 2 <= N <= 5 for spline interpolation)

    GPX_files = glob.glob('*.gpx')

    for gpx_file in GPX_files:
        if not gpx_file[-17:] == '_interpolated.gpx':
            print('reading '+gpx_file+'...')
            (lat, lon, ele, tstamp) = GPX_read(gpx_file)

            print('interpolating GPX data...')
            (lat_new, lon_new, ele_new, tstamp_new) = GPX_interpolate(lat, lon, ele, tstamp, interpolate_res, interpolate_deg)

            output_file = gpx_file[:-4]+'_interpolated.gpx'

            print('writing '+output_file+'...')

            GPX_write(output_file, lat_new, lon_new, ele_new, tstamp_new)

            #output_file = gpx_file[:-4]+'_interpolated.csv'

            #print('writing '+output_file+'...')

            #CSV_write(output_file, lat_new, lon_new, ele_new, tstamp_new)

            print('done')

if __name__ == '__main__':
    # execute only if run as a script
    main()
