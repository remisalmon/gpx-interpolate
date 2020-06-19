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
from scipy.interpolate import interp1d, splprep, splev

# constants
EARTH_RADIUS = 6371e3 # meters

# functions
def gpx_interpolate(gpx_data, res, deg = 1):
    # input: gpx_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float], 'tstamp':list[float], 'tzinfo':datetime.tzinfo}
    #        res = float
    #        deg = int
    # output: gpx_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float], 'tstamp':list[float], 'tzinfo':datetime.tzinfo}

    if not type(deg) is int:
        raise TypeError('deg must be int')

    if not 1 <= deg <= 5:
        raise ValueError('deg must be in [1-5]')

    if not len(gpx_data['lat']) > deg:
        raise ValueError('number of data points must be > deg')

    # interpolate spatial data
    gpx_dist = gpx_calculate_dist(gpx_data)

    gpx_data, gpx_dist = gpx_remove_dup(gpx_data, gpx_dist)

    x = [gpx_data['lat'], gpx_data['lon']]
    if gpx_data['ele']:
        x.append(gpx_data['ele'])

    tck, _ = splprep(x, u = np.cumsum(gpx_dist), k = deg, s = 0)

    u_interp = np.linspace(0, np.sum(gpx_dist), 1+int(np.sum(gpx_dist)/res))
    x_interp = splev(u_interp, tck)

    lat_interp = x_interp[0]
    lon_interp = x_interp[1]
    if gpx_data['ele']:
        ele_interp = x_interp[2]

    # interpolate time data linearly to preserve monotonicity
    if gpx_data['tstamp']:
        f = interp1d(np.cumsum(gpx_dist), gpx_data['tstamp'], fill_value = 'extrapolate')

        tstamp_interp = f(u_interp)

    gpx_data['lat'] = list(lat_interp)
    gpx_data['lon'] = list(lon_interp)
    if gpx_data['ele']:
        gpx_data['ele'] = list(ele_interp)
    if gpx_data['tstamp']:
        gpx_data['tstamp'] = list(tstamp_interp)

    return gpx_data

def gpx_calculate_dist(gpx_data):
    # input: gpx_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float], 'tstamp':list[float], 'tzinfo':datetime.tzinfo}
    # output: gpx_dist = numpy.ndarray[float]

    gpx_dist = np.zeros(len(gpx_data['lat']))

    for i in range(len(gpx_dist)-1):
        lat1 = np.radians(gpx_data['lat'][i])
        lon1 = np.radians(gpx_data['lon'][i])
        lat2 = np.radians(gpx_data['lat'][i+1])
        lon2 = np.radians(gpx_data['lon'][i+1])

        delta_lat = lat2-lat1
        delta_lon = lon2-lon1

        c = 2.0*np.arcsin(np.sqrt(np.sin(delta_lat/2.0)**2+np.cos(lat1)*np.cos(lat2)*np.sin(delta_lon/2.0)**2)) # haversine formula

        dist_latlon = EARTH_RADIUS*c # great-circle distance

        if gpx_data['ele']:
            dist_ele = gpx_data['ele'][i+1]-gpx_data['ele'][i]

            gpx_dist[i+1] = np.sqrt(dist_latlon**2+dist_ele**2)

        else:
            gpx_dist[i+1] = dist_latlon

    return gpx_dist

def gpx_remove_dup(gpx_data, gpx_dist):
    # input: gpx_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float], 'tstamp':list[float], 'tzinfo':datetime.tzinfo}
    #        gpx_dist = numpy.ndarray[float]
    # output: gpx_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float], 'tstamp':list[float], 'tzinfo':datetime.tzinfo}
    #         gpx_dist = numpy.ndarray[float]

    i_dist = np.concatenate(([0], np.nonzero(gpx_dist)[0])) # keep gpx_dist[0] = 0

    gpx_dist = gpx_dist[i_dist]

    for k in ('lat', 'lon', 'ele', 'tstamp'):
        if gpx_data[k]:
            gpx_data[k] = [gpx_data[k][i] for i in i_dist]

    return gpx_data, gpx_dist

def gpx_read(gpx_file):
    # input: gpx_file = str
    # output: gpx_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float], 'tstamp':list[float], 'tzinfo':datetime.tzinfo}

    gpx_data = {'lat':[], 'lon':[], 'ele':[], 'tstamp':[], 'tzinfo':None}

    i = 0
    i_latlon = []
    i_tstamp = []

    with open(gpx_file, 'r') as file:
        gpx = gpxpy.parse(file)

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    gpx_data['lat'].append(point.latitude)
                    gpx_data['lon'].append(point.longitude)

                    i_latlon.append(i)

                    try:
                        gpx_data['ele'].append(point.elevation)
                    except:
                        pass

                    try:
                        gpx_data['tstamp'].append(point.time.timestamp())
                    except:
                        pass
                    else:
                        if not gpx_data['tzinfo']:
                            gpx_data['tzinfo'] = point.time.tzinfo

                        i_tstamp.append(i)

                    i += 1

    if i_tstamp and not len(i_latlon) == len(i_tstamp):
        for k in ('lat', 'lon', 'ele', 'tstamp'):
            if gpx_data[k]:
                gpx_data[k] = [gpx_data[k][i] for i in i_tstamp]

    return gpx_data

def gpx_write(gpx_file, gpx_data):
    # input: gpx_file = str
    #        gpx_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float], 'tstamp':list[float], 'tzinfo':datetime.tzinfo}
    # output: None

    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_segment = gpxpy.gpx.GPXTrackSegment()

    gpx.tracks.append(gpx_track)
    gpx_track.segments.append(gpx_segment)

    for i in range(len(gpx_data['lat'])):
        gpx_point = gpxpy.gpx.GPXTrackPoint(gpx_data['lat'][i],
                                            gpx_data['lon'][i],
                                            gpx_data['ele'][i] if gpx_data['ele'] else None,
                                            datetime.fromtimestamp(gpx_data['tstamp'][i], tz = gpx_data['tzinfo']) if gpx_data['tstamp'] else None)

        gpx_segment.points.append(gpx_point)

    try:
        with open(gpx_file, 'w') as file:
            file.write(gpx.to_xml())

    except:
        exit('ERROR Failed to save {}'.format(gpx_file))

    return

# main
def main():
    import argparse

    parser = argparse.ArgumentParser(description = 'interpolate GPX file(s) using linear or spline interpolation')

    parser.add_argument('gpx_files', metavar = 'FILE', nargs = '+', help = 'GPX file(s)')
    parser.add_argument('-d', '--deg', type = int, default = 1, help = 'interpolation degree, 1=linear, 2-5=spline (default: 1)')
    parser.add_argument('-r', '--res', type = float, default = 1, help = 'interpolation resolution in meters (default: 1)')

    args = parser.parse_args()

    for gpx_file in args.gpx_files:
        if not '_interpolated.gpx' in gpx_file:
            gpx_data = gpx_read(gpx_file)

            print('Read {}'.format(gpx_file))

            gpx_x_interp = gpx_interpolate(gpx_data, args.res, args.deg)

            output_file = '{}_interpolated.gpx'.format(gpx_file[:-4])

            gpx_write(output_file, gpx_x_interp)

            print('Saved {}'.format(output_file))

if __name__ == '__main__':
    main()
