import json
import os

from reference import get_reference_data

filter_specs = json.loads(open('../data/filter_specs.json', 'r').read())

used_bands = [f"{part}_{layer}" for part, layers in filter_specs.items() for layer in layers]
centers = [(filter_specs[band.split('_')[0]][band.split('_')[1]]['weighted_center'], band) for band in used_bands]
centers.sort()
used_bands = [band for center, band in centers]
centers = [str(center) for center, band in centers]

reference_data = get_reference_data(filter_specs, data_dir='../data/reference')
print(reference_data)


def load_zonal_stats(file_name):
    with open(file_name, 'r') as f:
        zonal_stats = json.loads(f.read())
    return zonal_stats


zone_files = [f for f in os.listdir('zonal_data') if f.endswith('.json')]

for zone_file in zone_files:
    zone_stats = load_zonal_stats('zonal_data/' + zone_file)

    eval_data = {}

    for location, data in zone_stats.items():
        eval_data[location] = {}
        for band, values in data.items():
            max_value = values['max']
            mean_value = values['mean']

            value_percentage = mean_value / 65535

            band_source = used_bands[int(band) - 1]
            center = centers[int(band) - 1]

            reference = reference_data[location][band_source.split('_')[0]] \
                [band_source.split('_')[1]]

            average_reflectance = reference['average_reflectance']
            hmr = reference['half_max_rising']
            hmf = reference['half_max_falling']

            factor = average_reflectance / value_percentage

            eval_data[location][band] = {
                'max': max_value,
                'mean': mean_value,
                'value_percentage': value_percentage,
                'average_reflectance': average_reflectance,
                'factor': factor,
                'band_source': band_source,
                'center': center,
                'hmr': hmr,
                'hmf': hmf
            }

    os.makedirs('evaluation', exist_ok=True)
    with open(f'evaluation/{zone_file}', 'w') as f:
        f.write(json.dumps(eval_data, indent=4))
