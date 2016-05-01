#!/usr/bin/env python3
import argparse
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


def draw_map(lats, lons, px_size, resolution):
    print('drawing map...')
    fig_size = px_size // 100
    figure = matplotlib.pyplot.figure(figsize=(fig_size, fig_size))
    basemap = Basemap(llcrnrlon=min(lons), llcrnrlat=min(lats),
                      urcrnrlon=max(lons), urcrnrlat=max(lats),
                      lon_0=mean(lons), lat_0=mean(lats),
                      resolution='i', projection='tmerc')
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
    parser.add_argument('--resolution', help='resolution of basemap', default='h',
                        choices=('c', 'l', 'i', 'h', 'f'))
    parser.add_argument('-s', '--size', help='size of produced image in pixels', default=4000,
                        type=int)
    args = parser.parse_args()

    import_matplotlib()
    if args.input == '-':
        lats, lons, alts = extract_positions(sys.stdin)
    else:
        with open(args.input, 'r') as data:
            lats, lons, alts = extract_positions(data)
    figure, basemap = draw_map(lats, lons, args.size, args.resolution)
    plot_points(basemap, lats, lons, alts)
    save_image(figure, args.output)


if __name__ == '__main__':
    main()
