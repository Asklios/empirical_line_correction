import rasterio


def apply_empirical_line_correction(coefficients, input_raster, output_raster):
    with rasterio.open(input_raster) as src:
        new_profile = src.profile.copy()
        new_profile.update(dtype=rasterio.float32, count=len(coefficients) + 1)

        write_id = {int(k): i + 1 for i, k in enumerate(coefficients.keys())}

        with rasterio.open(output_raster, 'w', **new_profile) as dst:
            for band_id, coef in coefficients.items():
                band_id = int(band_id)
                coefficient = coef[0]
                intercept = coef[1]
                print(f'Band {band_id}: {coefficient} * band + {intercept}')

                band = src.read(band_id)
                corrected_band = band * coefficient + intercept
                dst.write(corrected_band.astype(rasterio.float32), write_id[band_id])

            dst.write(src.read(19).astype(rasterio.float32), len(coefficients) + 1)


def apply_factors(factors, input_raster, output_raster):
    with rasterio.open(input_raster) as src:
        new_profile = src.profile.copy()
        new_profile.update(dtype=rasterio.float32, count=len(factors) + 1)

        write_id = {k: i + 1 for i, k in enumerate(factors.keys())}

        with rasterio.open(output_raster, 'w', **new_profile) as dst:
            for band_id, factor in factors.items():
                band_id = int(band_id)
                print(f'Band {band_id}: {factor}')

                band = src.read(band_id)
                corrected_band = band * factor['factor']
                dst.write(corrected_band.astype(rasterio.float32), write_id[band_id])

            dst.write(src.read(19).astype(rasterio.float32), len(factors) + 1)
