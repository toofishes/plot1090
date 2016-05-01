from statistics import mean
from mpl_toolkits.basemap import Basemap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    lats = []
    lons = []
    alts = []

    print('processing data...')
    with open('testdata.csv', 'r') as data:
        for line in data:
            pieces = line.split(',')
            if pieces[1] == '3':
                lats.append(float(pieces[14]))
                lons.append(float(pieces[15]))
                alts.append(int(pieces[11]))

    print('drawing map...')
    plt.figure(figsize=(80, 80))
    my_map = Basemap(llcrnrlon=min(lons), llcrnrlat=min(lats),
                     urcrnrlon=max(lons), urcrnrlat=max(lats),
                     lon_0=mean(lons), lat_0=mean(lats),
                     resolution='h', projection='tmerc')
    my_map.drawcoastlines()
    my_map.drawstates()
    my_map.drawrivers()
    my_map.fillcontinents(color='0.99', zorder=0)

    print('plotting points...')
    x, y = my_map(lons, lats)
    max_alt = max(alts)
    sizes = [(a * 2.5 / max_alt) + 0.5 for a in alts]
    my_map.scatter(x, y, s=sizes, c=alts, marker='o', lw=0, cmap='plasma')
    plt.savefig('/tmp/my_map.png', bbox_inches='tight', pad_inches=0)


if __name__ == '__main__':
    main()
