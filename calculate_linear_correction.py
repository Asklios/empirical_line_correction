import json
import os

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression


def calculate_correction_data(filter_specs, reference_data, band_source, zonal_stats):
    data = {}
    for name, values in zonal_stats.items():
        if name not in reference_data.keys():
            print(f'No filter data found for "{name}"')
            continue
        filter_data = reference_data[name]
        data[name] = {}
        for part, layers in filter_data.items():
            data[name][part] = {}
            for layer, layer_data in layers.items():
                band_id = band_source[f'{part}_{layer}']

                data[name][part][layer] = {
                    **layer_data,
                    'mean': values[str(band_id)]['mean'],
                    'max': values[str(band_id)]['max']
                }

    # create a dict with part_layer as key and weighted_center as value
    sorted_layers = {}
    for part, layers in filter_specs.items():
        for layer, values in layers.items():
            sorted_layers[f'{part}_{layer}'] = values['weighted_center']
    sorted_layers = dict(sorted(sorted_layers.items(), key=lambda item: item[1]))

    sorted_data = {}
    for name, parts in data.items():
        sorted_data[name] = {}
        for part, layer in [k.split('_') for k in sorted_layers.keys()]:
            sorted_data[name][f'{part}_{layer}'] = parts[part][layer]

    reordered_data = {}
    for name, parts in sorted_data.items():
        for part, values in parts.items():
            if part not in reordered_data:
                reordered_data[part] = {}
            reordered_data[part][name] = values

    return reordered_data


def plot_regression(non_max_mean_values, non_max_avg_reflectance, non_max_probes, max_mean_values, max_avg_reflectance,
                    max_probes, name, model, plot_path):
    plt.figure(figsize=(8, 8))
    plt.scatter(non_max_mean_values, non_max_avg_reflectance)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.xlabel('Mean Value')
    plt.ylabel('Average Reflectance')
    plt.title(name)
    for i, txt in enumerate(non_max_probes):
        plt.annotate(txt, (non_max_mean_values[i], non_max_avg_reflectance[i]))
    if len(max_mean_values) > 0:
        plt.scatter(max_mean_values, max_avg_reflectance, marker='x')
        for i, txt in enumerate(max_probes):
            plt.annotate(txt, (max_mean_values[i], max_avg_reflectance[i]))
    x = np.linspace(0, 1, 100)
    y = model.predict(x.reshape(-1, 1))
    plt.plot(x, y, color='red')
    plt.savefig(f'{plot_path}/{name}.png')
    plt.close()


def calculate_regression(correction_data, band_source, skip=None, plot_path='plots'):
    os.makedirs(plot_path, exist_ok=True)
    if skip is None:
        skip = []
    if skip is None:
        skip = []
    coefficients_list = {}
    r_squared_list = {}
    for key in correction_data.keys():

        max_mean_values = []
        max_avg_reflectance = []
        max_probes = []
        non_max_mean_values = []
        non_max_avg_reflectance = []
        non_max_probes = []

        for probe in correction_data[key].keys():

            if skip:
                # skip some probes
                if probe in skip[0]:
                    if key in skip[1]:
                        continue

            max_value = correction_data[key][probe]['max']

            if max_value == 65535:
                max_mean_values.append(correction_data[key][probe]['mean'])
                max_avg_reflectance.append(correction_data[key][probe]['average_reflectance'])
                max_probes.append(probe)
            else:
                non_max_mean_values.append(correction_data[key][probe]['mean'])
                non_max_avg_reflectance.append(correction_data[key][probe]['average_reflectance'])
                non_max_probes.append(probe)

        max_mean_values = np.array(max_mean_values) / 65535
        non_max_mean_values = np.array(non_max_mean_values) / 65535
        model = LinearRegression().fit(non_max_mean_values.reshape(-1, 1), non_max_avg_reflectance)

        plot_regression(non_max_mean_values, non_max_avg_reflectance, non_max_probes, max_mean_values,
                        max_avg_reflectance,
                        max_probes, key, model, plot_path)

        r_squared = model.score(non_max_mean_values.reshape(-1, 1), non_max_avg_reflectance)
        coefficients = model.coef_, model.intercept_

        r_squared_list[key] = r_squared

        band_id = str(band_source[key])
        coefficients_list[band_id] = [coefficients[0][0], coefficients[1]]

    with open(plot_path + '/r_squared_part_layer.json', 'w') as f:
        f.write(json.dumps(r_squared_list, indent=4))

    with open(plot_path + '/r_squared.json', 'w') as f:
        f.write(json.dumps({correction_data[key][list(correction_data[key].keys())[0]]['weighted_center']: value
                            for key, value in r_squared_list.items()}, indent=4))

    with open(plot_path + '/coefficients.json', 'w') as f:
        f.write(json.dumps({key: f'* {value[0]} + {value[1]}'
                            for key, value in coefficients_list.items()}, indent=4))

    return coefficients_list
