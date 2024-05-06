import os

import numpy as np
import matplotlib.pyplot as plt


def load_spectrum(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()[22:]
    data = {}
    for line in lines:
        x, y = map(float, line.strip().split('\t'))
        data[x] = y
    return data


def average_spectrum(spectrums: [dict]):
    sum_dict = {}
    count_dict = {}

    for spectrum in spectrums:
        for key, value in spectrum.items():
            if key in sum_dict:
                sum_dict[key] += value
                count_dict[key] += 1
            else:
                sum_dict[key] = value
                count_dict[key] = 1

    average_dict = {key: sum_dict[key] / count_dict[key] for key in sum_dict}

    return average_dict


def plot_data(original_data, normalized_data, name, path):

    plt.plot(list(original_data.keys()), list(original_data.values()), label='Original')
    plt.plot(list(normalized_data.keys()), list(normalized_data.values()), label='Normalized')

    plt.xlabel('Wavelength')
    plt.ylabel('Intensity')
    plt.title(name)
    plt.legend()

    plt.ylim(0, 0.5)

    # plt.show()
    os.makedirs(path, exist_ok=True)
    plt.savefig(f'{path}/{name}.png')
    plt.clf()  # Clear the plot


def fourier_smooth(data):
    # Perform Fourier transform
    fft = np.fft.fft(list(data.values()))

    # Define the fraction of components to keep
    keep_fraction = 0.05

    # Make a copy of the original (complex) array
    fft2 = fft.copy()

    # Set r fraction of components to zero
    fft2[int(fft2.size * keep_fraction):] = 0

    # Perform inverse Fourier transform
    smoothed_values = np.fft.ifft(fft2)
    return dict(zip(data.keys(), smoothed_values.real))


def get_reference_data(filter_specs: dict):
    data_dir = 'data/reference'

    reference_data = {}

    for folder in os.listdir(data_dir + '/input'):
        reference_data[folder] = {}
        folder_path = os.path.join(data_dir + '/input', folder)
        if os.path.isdir(folder_path):
            files = [f for f in os.listdir(folder_path) if f.endswith('.spz')]
            try:
                spektralon = [f for f in files if 'spektralon' in f.lower()][0]
            except IndexError:
                print(f'No spektralon file found in {folder}')
                continue
            files.remove(spektralon)

            spektralon = load_spectrum(os.path.join(folder_path, spektralon))
            data = [load_spectrum(os.path.join(folder_path, f)) for f in files]

            average_data = average_spectrum(data)

            max_spectralon = max(spektralon.values())
            factors = {key: max_spectralon / value for key, value in spektralon.items()}

            average_data_percentage = {key: value / max_spectralon for key, value in average_data.items()}
            average_data_normalized = {key: value * factors[key] for key, value in average_data_percentage.items()}

            average_data_normalized_smoothed = fourier_smooth(average_data_normalized)

            plot_data(average_data_percentage, average_data_normalized_smoothed, folder, data_dir + '/plots')

            # save the normalized data
            os.makedirs(data_dir + '/normalized_data/', exist_ok=True)
            with open(f'{data_dir}/normalized_data/{folder}.csv', 'w') as f:
                f.write('Wavelength\tReflectance\n')
                for key, value in average_data_normalized.items():
                    f.write(f'{key}\t{value}\n')

            filter_data = {}
            for part, layers in filter_specs.items():
                filter_data[part] = {}
                for layer, values in layers.items():
                    weighted_center = values['weighted_center']
                    hmr = values['half_max_rising']
                    hmf = values['half_max_falling']

                    filtered_data = {key: value for key, value in average_data_normalized.items() if hmr <= key <= hmf}
                    average_reflectance = sum(filtered_data.values()) / len(filtered_data)

                    filter_data[part][layer] = {'weighted_center': weighted_center,
                                                'half_max_rising': hmr,
                                                'half_max_falling': hmf,
                                                'average_reflectance': average_reflectance}

            reference_data[folder] = filter_data

    return reference_data
