#!/usr/bin/env python3
import os
# import multiprocessing
import argparse
import matplotlib
if os.name == 'posix':
    matplotlib.use('Qt4Agg')
elif os.name == 'nt':
    matplotlib.rcParams['backend'] = 'TkAgg'
import matplotlib.pyplot as plt


def _getpath(filename):
    return os.path.realpath(os.path.expanduser(filename))


def _parse_default_file(file_url):
    with open(file_url) as f:
        data = []
        for line in f:
            line_split = line.split()
            if len(line_split) != 3:
                raise ValueError(f'This file is not in the simple format: {line}')  # noqa

            if line_split[1] != line_split[2]:
                data += [[int(line_split[0]), float(line_split[1]), float(line_split[2])]]  # noqa

    data.sort(key=lambda x: [x[0], x[1], x[1] - x[2]])
    return data


def _parse_java_file(file_url):
    with open(file_url) as f:
        data = []
        dimension = -1
        for line in f:
            if line[:9] == 'Dimension':
                dimension = int(line.split(' ')[1])
            else:
                split_line = line.strip('[)\n').split(', ')
                data_entry = [dimension] + list(map(float, split_line))
                data += [data_entry]

    data.sort(key=lambda x: [x[0], x[1], x[1] - x[2]])
    return data


def _parse_data_by_dim(data):

    dim, x, y = list(map(list, zip(*data)))
    N = len(dim)

    data_by_dim = {}
    regular_x = []
    regular_y = []
    infinite_x = []
    max_val = 0
    for i in range(N):

        if y[i] == float('inf'):
            infinite_x += [x[i]]
            max_val = max(x[i], max_val)
        else:
            regular_x += [x[i]]
            regular_y += [y[i]]
            max_val = max(x[i], y[i], max_val)

        if i == N - 1 or dim[i + 1] > dim[i]:
            data_in_dim = {}
            data_in_dim['regular'] = [regular_x, regular_y]
            data_in_dim['infinite'] = infinite_x
            data_by_dim[dim[i]] = data_in_dim

            regular_x = []
            regular_y = []
            infinite_x = []

    data_by_dim['max_val'] = max_val * 1.1
    data_by_dim['max_dim'] = dim[-1]
    return data_by_dim


def _parse_bool_from_str(string):
    truthy = ['1', 'true', 'True', 't', 'T', 'yes', 'Yes', 'y', 'Y']
    falsy = ['0', 'false', 'False', 'f', 'F', 'no', 'No', 'n', 'N']

    if string in truthy:
        return True
    elif string in falsy:
        return False
    else:
        return bool(string)


def _parse_options(options):
    kw = {}
    options_list = [option.split('=') for option in options]
    for option in options_list:
        kw[option[0]] = option[1]
    alpha = float(kw.get('alpha', 0.5))
    title = kw.get('title', None)
    cmap_name = kw.get('cmap', 'rainbow')
    cmap = getattr(plt.cm, cmap_name)
    figsize_str = kw.get('figsize', '(5, 5)')
    figsize = tuple(map(float, figsize_str.strip('()').split(',')))
    linewidth = float(kw.get('linewidth', 1.5))
    dual = _parse_bool_from_str(kw.get('dual', 'True'))
    image_format = kw.get('format', 'eps')

    kw = {'alpha': alpha,
          'title': title,
          'cmap': cmap,
          'figsize': figsize,
          'linewidth': linewidth,
          'dual': dual,
          'format': image_format}
    return kw


def _plot_diagram_by_dim(data_in_dim, ax, **kw):
    alpha = kw['alpha']
    color = kw['color']
    label = kw['label']
    max_val = kw['max_val']

    regular_x, regular_y = data_in_dim['regular']
    infinite_x = data_in_dim['infinite']

    ax.scatter(regular_x, regular_y,
               color=color, clip_on=False, alpha=alpha, label=label)
    ax.scatter(infinite_x, [max_val] * len(infinite_x),
               color=color, clip_on=False, alpha=alpha, marker='^')

    return ax


def plot_diagram(data_by_dim, ax, **kw):
    title = kw['title']
    cmap = kw['cmap']
    x_bins = kw['x_bins']
    y_bins = kw['y_bins']

    max_val = data_by_dim['max_val']
    max_dim = data_by_dim['max_dim']

    kw['max_val'] = max_val

    diagram_title = f'Persistence Diagram for {title}' \
                    if (title is not None) \
                    else 'Persistence Diagram'
    ax.set_title(diagram_title)

    for dim in range(0, max_dim + 1):
        data_in_dim = data_by_dim[dim]
        kw['label'] = f'{dim}D features'
        kw['color'] = cmap(dim / max_dim)
        ax = _plot_diagram_by_dim(data_in_dim, ax, **kw)

    ax.set_xlim(0, max_val)
    ax.set_ylim(0, max_val)
    ax.plot([0, 1], [0, 1],
            transform=ax.transAxes)  # draw a diagonal line across the diagram
    ax.xaxis.major.locator.set_params(nbins=x_bins)
    ax.yaxis.major.locator.set_params(nbins=y_bins)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc=4)


def plot_barcode(data, ax, **kw):
    title = kw['title']
    cmap = kw['cmap']
    linewidth = kw['linewidth']
    x_bins = kw['x_bins']
    y_bins = kw['y_bins']

    diagram_title = f'Barcode for {title}' \
                    if (title is not None) \
                    else 'Barcode'
    ax.set_title(diagram_title)

    dim, birth, death = list(map(list, zip(*data)))

    maximum_val = 1.1 * max(max(birth),
                            max([time for time in death if time < float('inf')]))
    maximum_dim = max(dim)
    height = 0
    step = maximum_val / (len(dim) + 1)
    for i in range(int(len(dim))):
        height += step
        bar_birth = birth[i]
        bar_death = death[i] if death[i] < float('inf') else maximum_val
        bar_dim = dim[i]
        label = f'{dim[i]}D features' if i == 0 or dim[i] != dim[i - 1] else None
        ax.plot([bar_birth, bar_death], [height, height],
                linewidth=linewidth, color=cmap(bar_dim / maximum_dim), label=label)
        if death[i] == float('inf'):
            ax.scatter(bar_death, height, marker='>',
                       clip_on=False, color=cmap(bar_dim / maximum_dim))

    ax.set_xlim(0, maximum_val)
    ax.set_ylim(0, maximum_val)
    ax.xaxis.major.locator.set_params(nbins=x_bins)
    ax.yaxis.major.locator.set_params(nbins=y_bins)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc=3)


def plot_diagrams(data, **kw):
    data_by_dim = _parse_data_by_dim(data)

    if kw['dual']:
        figsize = kw.get('figsize', (8, 4))
        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        kw['x_bins'] = 4
        kw['y_bins'] = 6

        plot_barcode(data, ax1, **kw)
        plot_diagram(data_by_dim, ax2, **kw)

        if kw['save']:
            image_format = kw['format']
            fig.savefig(outfile_url + '.' + image_format, format=image_format)

    else:
        figsize = kw.get('figsize', (5, 5))
        fig1 = plt.figure(figsize=figsize)
        fig2 = plt.figure(figsize=figsize)
        ax1 = fig1.add_subplot(111)
        ax2 = fig2.add_subplot(111)

        kw['x_bins'] = 6
        kw['y_bins'] = 6

        plot_barcode(data, ax1, **kw)
        plot_diagram(data_by_dim, ax2, **kw)

        if kw['save']:
            image_format = kw['format']
            fig1.savefig(outfile_url + '.barcode.' + image_format, format=image_format)
            fig2.savefig(outfile_url + '.diagram.' + image_format, format=image_format)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot barcodes and persistence diagrams.')
    parser.add_argument('-f', '--format',
                        default='j', choices=['s', 'j'],
                        help='Format of the barcode files. Use \'s\' for the simple format, or \'j\' for the javaplex format. ')
    parser.add_argument('intervals',
                        help='Path to the intervals file.')
    parser.add_argument('-o', '--output', nargs='?',
                        const='',
                        help='Use this option to output the image file. Optionally, supply a path for the outputs.')
    parser.add_argument('-p', '--plot',
                        choices=['b', 'd', 'bd'], default='bd',
                        help='The diagrams to be generated. Use \'b\' for barcode, \'d\' for persistence diagram, and \'bd\' for both.')
    parser.add_argument('-n', '--noshow', action='store_true',
                        help='Use this option to control if the graphs are displayed. This option implies --output.')
    parser.add_argument('-O', '--plot-options', nargs='*', default=[],
                        help='Plot options passed to matplotlib.')

    # try:
    args = parser.parse_args()
    # except argparse.ArgumentError as exc:
    #     print(exc.message)
    #     parser.print_help()

    infile_url = _getpath(args.intervals)
    if args.format == 'j':
        data = _parse_java_file(infile_url)
    else:
        data = _parse_default_file(infile_url)

    # TODO: Turn this into a function.
    options = _parse_options(args.plot_options)
    if args.output is not None:
        options['save'] = True
        if args.output == '':
            outfile_url = _getpath(args.intervals)
        elif os.path.isdir(os.path.expanduser(args.output)):
            outfile_url = _getpath(args.output + '/' + args.intervals.split('/')[-1])
        else:
            outfile_url = _getpath(args.output)
        options['outfile_url'] = outfile_url
    else:
        options['save'] = False

    plot_diagrams(data, **options)

    if not args.noshow:
        # plot_process = multiprocessing.Process(target=_plot_worker,
                                                # args=())
        # plot_process.start()
        plt.show()
