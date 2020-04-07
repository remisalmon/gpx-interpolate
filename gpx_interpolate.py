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
def gpx_interpolate(lat, lon, ele, tstamp, res, deg = 1):
    # input: lat = list[float]
    #        lon = list[float]
    #        ele = list[float]
    #        tsamp = list[float]
    #        res = float
    #        deg = int
    # output: lat_interp = list[float]
    #         lon_interp = list[float]
    #         ele_interp = list[float]
    #         tsamp_interp = list[float]

    if not type(deg) == int:
        raise TypeError('deg must be int')

    if not 1 <= deg <= 5:
        raise ValueError('deg must be in [1-5]')

    if not len(lat) > deg:
        raise Warning('number of data points must be > deg')

    dist = gpx_calculate_dist(lat, lon, ele) # dist between points

    dist_cum_norm = np.cumsum(dist)/np.sum(dist) # normalized cumulative dist between points

    # interpolate spatial data
    data = [lat, lon, ele]

    tck, _ = splprep(x = data, u = dist_cum_norm, k = deg, s = 0, nest = len(lat)+deg+1)

    u_interp = np.linspace(0, 1, 1+int(np.sum(dist)/res))

    data_interp = splev(u_interp, tck)

    lat_interp = data_interp[0]
    lon_interp = data_interp[1]
    ele_interp = data_interp[2]

    # interpolate time data linearly to preserve monotonicity
    data = [tstamp, tstamp] # splprep does not accept 1D inputs...

    tck, _ = splprep(x = data, u = dist_cum_norm, k = 1, s = 0, nest = len(lat)+1+1)

    data_interp = splev(u_interp, tck)

    tstamp_interp = data_interp[0]

    # remove insignificant digits
    lat_interp = np.round(lat_interp*1e6)/1e6
    lon_interp = np.round(lon_interp*1e6)/1e6
    ele_interp = np.round(ele_interp*1e6)/1e6
    tstamp_interp = np.round(tstamp_interp*1e2)/1e2 # round to hundredth of seconds

    return lat_interp.tolist(), lon_interp.tolist(), ele_interp.tolist(), tstamp_interp.tolist()

def gpx_calculate_dist(lat, lon, ele):
    # input: lat = list[float]
    #        lon = list[float]
    #        ele = list[float]
    # output: dist = numpy.array[float]

    dist = np.zeros(len(lat))

    for i in np.arange(1, len(dist)):
        lat1 = np.radians(lat[i-1])
        lon1 = np.radians(lon[i-1])
        lat2 = np.radians(lat[i])
        lon2 = np.radians(lon[i])

        delta_lat = np.abs(lat2-lat1)
        delta_lon = np.abs(lon2-lon1)

        c = 2.0*np.arcsin(np.sqrt(np.sin(delta_lat/2.0)**2+np.cos(lat1)*np.cos(lat2)*np.sin(delta_lon/2.0)**2)) # haversine formula

        dist_lat_lon = EARTH_RADIUS*c # great-circle distance

        dist_ele = ele[i]-ele[i-1] # elevation change

        dist[i] = np.sqrt(dist_lat_lon**2+dist_ele**2)

    return dist

def gpx_read(gpx_file):
    # input: gpx_file = str
    # output: lat = list[float]
    #         lon = list[float]
    #         ele = list[float]
    #         tsamp = list[float]

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

    return lat, lon, ele, tstamp

def gpx_write(gpx_file, lat, lon, ele, tstamp):
    # input: gpx_file = str
    #        lat = list[float]
    #        lon = list[float]
    #        ele = list[float]
    #        tsamp = list[float]
    # output: None

    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_segment = gpxpy.gpx.GPXTrackSegment()

    gpx.tracks.append(gpx_track)

    gpx_track.segments.append(gpx_segment)

    for i in range(len(lat)):
        gpx_point = gpxpy.gpx.GPXTrackPoint(lat[i],
                                            lon[i],
                                            ele[i],
                                            datetime.fromtimestamp(tstamp[i]))

        gpx_segment.points.append(gpx_point)

    with open(gpx_file, 'w') as file:
        file.write(gpx.to_xml())

    return None

# main
def main():
    import argparse

    parser = argparse.ArgumentParser(description = 'Interpolate GPX file(s) using linear/spline interpolation')

    parser.add_argument('gpx_files', type = str, metavar = 'FILE', nargs = '+', help = 'GPX file(s)')
    parser.add_argument('-d', '--deg', type = int, default = 1, help = 'Interpolation degree, 1=linear, 2-5=spline (default: 1)')
    parser.add_argument('-r', '--res', type = float, default = 1, help = 'Interpolation resolution in meters (default: 1)')

    args = parser.parse_args()

    for gpx_file in args.gpx_files:
        if not gpx_file[-17:] == '_interpolated.gpx':
            print('Reading {}...'.format(gpx_file))

            lat, lon, ele, tstamp = gpx_read(gpx_file)

            lat_interp, lon_interp, ele_interp, tstamp_interp = gpx_interpolate(lat, lon, ele, tstamp, args.res, args.deg)

            output_file = gpx_file[:-4]+'_interpolated.gpx'

            print('Writing {}...'.format(output_file))

            gpx_write(output_file, lat_interp, lon_interp, ele_interp, tstamp_interp)

    print('Done')

if __name__ == '__main__':
    main()
