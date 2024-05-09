import json

import calculate_factors
from calculate_linear_correction import calculate_correction_data, calculate_regression
from raster import apply_factors, apply_empirical_line_correction
from reference import get_reference_data

filter_specs = json.loads(open('data/filter_specs.json', 'r').read())

new_filter_specs = {}
for part, layers in filter_specs.items():
    new_filter_specs[part] = {}
    for layer, values in layers.items():
        if int(layer) < 500:
            rgb_layer = 'b'
        elif int(layer) < 600:
            rgb_layer = 'g'
        else:
            rgb_layer = 'r'
        new_filter_specs[part][rgb_layer] = values
filter_specs = new_filter_specs

reference_data = get_reference_data(filter_specs)

# Bands are ordered alphabetically by part and then by color (r, g, b)
band_source = {'BLQ_r': 1, 'BLQ_g': 2, 'BLQ_b': 3,
               'BMQ_r': 4, 'BMQ_g': 5, 'BMQ_b': 6,
               'BRQ_r': 7, 'BRQ_g': 8, 'BRQ_b': 9,
               'TLQ_r': 10, 'TLQ_g': 11, 'TLQ_b': 12,
               'TMQ_r': 13, 'TMQ_g': 14, 'TMQ_b': 15,
               'TRQ_r': 16, 'TRQ_g': 17, 'TRQ_b': 18}

used_bands = [f"{part}_{layer}" for part, layers in filter_specs.items() for layer in layers]
centers = [(filter_specs[band.split('_')[0]][band.split('_')[1]]['weighted_center'], band) for band in used_bands]
centers.sort()
used_bands = [band for center, band in centers]
centers = [str(center) for center, band in centers]
print(';'.join(centers))
used_band_ids = [band_source[band] for band in used_bands]

zonal_stats = json.loads(open('data/zonal_stats.json', 'r').read())
correction_data = calculate_correction_data(filter_specs, reference_data, band_source, zonal_stats)

input_raster = 'E:/20240426/ArcGIS/south_v2_20240426_georef_dop40.tif'
# input_raster = 'E:/20240426/Metashape/mini_test/mini_test.tif'

factors = calculate_factors.calculate_factors(zonal_stats, band_source, reference_data)
factors = {b: factors[b] for b in used_band_ids}
with open('factors.json', 'w') as f:
    f.write(json.dumps(factors, indent=4))

#apply_factors(factors, input_raster, 'E:/20240426/output_factors.tif')

coefficients = calculate_regression(correction_data, band_source, plot_path='plots/no_skip', skip=None)

coefficients = calculate_regression(correction_data, band_source, plot_path='plots/skip_non_veg',
                                    skip=[["Parkplatz", "Strase", "Acker", "Tartan"], ["TLQ_r"]])

#apply_empirical_line_correction(coefficients, input_raster, 'E:/20240426/output_skip_non_veg.tif')

coefficients = calculate_regression(correction_data, band_source, plot_path='plots/skip_veg',
                                    skip=[["Fussballplatz", "Ackergruen", "Wiese"], ["TLQ_r", "BMQ_r"]])
#apply_empirical_line_correction(coefficients, input_raster, 'E:/20240426/output_skip_veg.tif')


