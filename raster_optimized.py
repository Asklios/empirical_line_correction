import rasterio
from rasterio.enums import Resampling


def apply_correction(input_raster, output_raster, corrections, correction_func):
    with rasterio.open(input_raster) as src:
        new_profile = src.profile.copy()
        new_profile.update(dtype=rasterio.float32, count=len(corrections) + 1)
        new_profile.update(tiled=True, blockxsize=256, blockysize=256, compress='lzw')

        write_id = {k: i + 1 for i, k in enumerate(corrections.keys())}

        with rasterio.open(output_raster, 'w', **new_profile) as dst:
            for band_id, correction in corrections.items():
                band_id = int(band_id)
                print(f'Band {band_id}: {correction}')

                band = src.read(band_id)
                corrected_band = correction_func(band, correction)
                dst.write(corrected_band.astype(rasterio.float32), write_id[band_id])

            dst.write(src.read(19).astype(rasterio.float32), len(corrections) + 1)
            dst.build_overviews([2, 4, 8, 16, 32], resampling=Resampling.average)
            dst.update_tags(ns='rio_overview', resampling='average')


def apply_empirical_line_correction(coefficients, input_raster, output_raster):
    def empirical_line_correction(band, correction):
        coefficient, intercept = correction
        return band * coefficient + intercept
    coefficients = {int(k): v for k, v in coefficients.items()}
    apply_correction(input_raster, output_raster, coefficients, empirical_line_correction)


def apply_factors(factors, input_raster, output_raster):
    def factor_correction(band, correction):
        return band * correction['factor']
    apply_correction(input_raster, output_raster, factors, factor_correction)
