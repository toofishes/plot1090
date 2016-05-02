#!/usr/bin/env python3
import argparse
import math
from statistics import mean
import sys


# these imports are relatively expensive, so delay them until needed
def import_matplotlib():
    global matplotlib
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot
    global Basemap
    from mpl_toolkits.basemap import Basemap


def extract_positions(data):
    lats = []
    lons = []
    alts = []

    print('processing data...')
    for line in data:
        pieces = line.split(',')
        # only include Airborne Position Messages, 'MSG,3' type
        if pieces[1] != '3':
            continue
        lats.append(float(pieces[14]))
        lons.append(float(pieces[15]))
        alts.append(int(pieces[11]))

    return lats, lons, alts


def calculate_limits(lats, lons, center_lat, center_lon, distance):
    # returns a 6-tuple for helping plot a map:
    # (lower-left lon, lower-left lat,
    #  upper-left lon, upper-right lat,
    #  center lon, center lat)
    if center_lat is None or center_lon is None:
        print('using calculated map limits and center')
        return (min(lons), min(lats),
                max(lons), max(lats),
                mean(lons), mean(lats))
    if distance is None:
        print('using calculated map limits, provided center')
        return (min(lons), min(lats),
                max(lons), max(lats),
                center_lon, center_lat)
    else:
        print('using provided map limits and center')
        # 1 degree of latitude = ~ 60 nautical miles
        lat_offset = distance / 60
        # longitude requires slightly more work
        lon_offset = distance / (math.cos(math.radians(center_lat)) * 60)
        return (center_lon - lon_offset,
                center_lat - lat_offset,
                center_lon + lon_offset,
                center_lat + lat_offset,
                center_lon, center_lat)


def draw_map(lats, lons, limits, px_size, resolution):
    print('drawing map...')
    fig_size = px_size // 100
    figure = matplotlib.pyplot.figure(figsize=(fig_size, fig_size))
    basemap = Basemap(limits[0], limits[1], limits[2], limits[3],
                      lon_0=limits[4], lat_0=limits[5],
                      resolution=resolution, projection='tmerc')
    print('drawing map features...')
    basemap.drawcoastlines()
    basemap.drawstates()
    basemap.drawrivers()
    basemap.fillcontinents(color='0.99', zorder=0)
    figure.tight_layout()

    return figure, basemap


def plot_points(basemap, lats, lons, alts):
    print('plotting %s points...' % len(lons))
    x, y = basemap(lons, lats)
    # we color and size points based on altitude; this prevents a total mess
    # on normal approach and departure patterns
    max_alt = max(alts)
    sizes = [(a * 2.5 / max_alt) + 0.5 for a in alts]
    basemap.scatter(x, y, s=sizes, c=alts, marker='o', lw=0, cmap='plasma')


def save_image(figure, img_path):
    print('saving map image to "%s"...' % img_path)
    figure.savefig(img_path, pad_inches=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='path to input CSV data, - for stdin')
    parser.add_argument('-o', '--output', help='path to output image', default='map.png')
    parser.add_argument('-s', '--size', help='size of produced image in pixels', default=4000,
                        type=int)
    parser.add_argument('--resolution', help='resolution of basemap features',
                        default='h', choices=('c', 'l', 'i', 'h', 'f'))
    parser.add_argument('--lat', help='latitude for center of map projection', type=float)
    parser.add_argument('--lon', help='longitude for center of map projection', type=float)
    parser.add_argument('--distance', help='distance in NM from center to plot', type=float)
    args = parser.parse_args()

    import_matplotlib()

    # allow using stdin; helpful for filtering input before plotting
    if args.input == '-':
        lats, lons, alts = extract_positions(sys.stdin)
    else:
        with open(args.input, 'r') as data:
            lats, lons, alts = extract_positions(data)

    limits = calculate_limits(lats, lons, args.lat, args.lon, args.distance)
    figure, basemap = draw_map(lats, lons, limits, args.size, args.resolution)
    plot_points(basemap, lats, lons, alts)
    save_image(figure, args.output)


if __name__ == '__main__':
    main()
