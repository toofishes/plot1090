#!/usr/bin/env python3
import argparse
from statistics import mean
import sys


def import_matplotlib():
    global matplotlib
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot
    global Basemap
    from mpl_toolkits.basemap import Basemap


def main(data, img_path):
    lats = []
    lons = []
    alts = []

    print('processing data...')
    for line in data:
        pieces = line.split(',')
        if pieces[1] == '3':
            lats.append(float(pieces[14]))
            lons.append(float(pieces[15]))
            alts.append(int(pieces[11]))

    print('drawing map...')
    figure = matplotlib.pyplot.figure(figsize=(80, 80))
    my_map = Basemap(llcrnrlon=min(lons), llcrnrlat=min(lats),
                     urcrnrlon=max(lons), urcrnrlat=max(lats),
                     lon_0=mean(lons), lat_0=mean(lats),
                     resolution='h', projection='tmerc')
    print('drawing map features...')
    my_map.drawcoastlines()
    my_map.drawstates()
    my_map.drawrivers()
    my_map.fillcontinents(color='0.99', zorder=0)

    print('plotting %s points...' % len(lons))
    x, y = my_map(lons, lats)
    max_alt = max(alts)
    sizes = [(a * 2.5 / max_alt) + 0.5 for a in alts]
    my_map.scatter(x, y, s=sizes, c=alts, marker='o', lw=0, cmap='plasma')
    figure.savefig(img_path, bbox_inches='tight', pad_inches=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='path to input CSV data, - for stdin')
    parser.add_argument('-o', '--output', help='path to output image', default='map.png')
    args = parser.parse_args()

    import_matplotlib()
    if args.input == '-':
        main(sys.stdin, args.output)
    else:
        with open(args.input, 'r') as data:
            main(data, args.output)
