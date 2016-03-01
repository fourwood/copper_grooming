#!/usr/bin/env python3
import pylab as plt
import json
import numpy as np

datafile = "groomed_runs.json"

try:
    with open(datafile, 'r') as f:
        json_data = json.load(f)

        dates = sorted(list(json_data['new_snow_24hr'].keys()))

        runs = sorted(list(json_data['runs'].keys()))
        table_data = np.zeros((len(runs), len(dates)))

        for i, run_name in enumerate(runs):
            groomed_dates = json_data['runs'][run_name]
            groomed_idx = [j for j,x in enumerate(dates) if x in groomed_dates]
            table_data[i, groomed_idx] = 192

        params = {'figure.subplot.left':    0.20,
                  'figure.subplot.right':   1.00,
                  'figure.subplot.bottom':  0.00,
                  'figure.subplot.top':     0.94,
                  'font.size':              10}
        plt.rcParams.update(params)
        fig, ax = plt.subplots(figsize=(8.5,17))
        ax.set_frame_on(False)

        cmap = plt.cm.Greens
        cmap.set_under('w')
        table = ax.pcolormesh(table_data, cmap=cmap,
                edgecolors=cmap(cmap.N-1), vmin=1, vmax=255)
        #table = ax.pcolor(table_data, cmap=cmap,
        #        edgecolors=cmap(cmap.N-1), vmin=1, vmax=255)

        ax.xaxis.tick_top()
        ax.invert_yaxis()

        ax.set_yticks(np.arange(table_data.shape[0]) + 0.5, minor=False)
        ax.set_xticks(np.arange(table_data.shape[1]) + 0.5, minor=False)
        ax.tick_params(axis='both', which='both', bottom='off', top='off',
                left='off', right='off')

        ax.set_xticklabels(dates, minor=False)
        plt.xticks(rotation=90)
        ax.set_yticklabels(runs, minor=False)

        #ax.grid(False)

        ax = plt.gca()
        for t in ax.xaxis.get_major_ticks():
            t.tick10n = False
            t.tick20n = False
        for t in ax.yaxis.get_major_ticks():
            t.tick10n = False
            t.tick20n = False

        plt.tight_layout()
        fig.savefig("groomed_runs.pdf", dpi=300, bbox_inches='tight')
        plt.close()

except FileNotFoundError as e:
    print("Run grooming data file not found:\n{0}".format(e))

def main():
    pass

if __name__ == "__main__":
    main()
