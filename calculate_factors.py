from collections import defaultdict


def calculate_factors(zonal_stats, band_source, reference_data):
    factors = defaultdict(dict)
    sum_factors = defaultdict(lambda: defaultdict(int))
    count_factors = defaultdict(lambda: defaultdict(int))
    average_factors = defaultdict(dict)
    band_factors = {}

    for name, values in zonal_stats.items():
        filter_data = reference_data.get(name)
        if filter_data is None:
            print(f'No filter data found for "{name}"')
            continue

        for part, layers in filter_data.items():
            for layer, data in layers.items():
                key = f'{part}_{layer}'
                band_id = band_source[key]
                band_id_str = str(band_id)

                mean_value_band = values[band_id_str]['mean']
                average_reflectance = data['average_reflectance']
                factor = (average_reflectance / mean_value_band) * 65535

                factors[name].setdefault(part, {})[layer] = {'factor': factor, **data, **values[band_id_str]}

    for name, parts in factors.items():
        for part, layers in parts.items():
            for layer, values in layers.items():
                if values['max'] == 65535:
                    print(f'{name} {part} {layer} is saturated! Will not be included in the average.')
                    continue

                sum_factors[part][layer] += values['factor']
                count_factors[part][layer] += 1

    for part, layers in sum_factors.items():
        for layer, sum_factor in layers.items():
            count = count_factors[part][layer]
            average_factors[part][layer] = sum_factor / count if count else 0

    for part, layers in average_factors.items():
        for layer, factor in layers.items():
            key = f'{part}_{layer}'
            band = band_source[key]
            center = factors[next(iter(factors))][part][layer]['weighted_center']
            band_factors[band] = {'factor': factor, 'center': center}

    return band_factors
