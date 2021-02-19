"""Peak based wave stats ufuncs."""
import numpy as np
import xarray as xr

from wavespectra.core.attributes import attrs
from wavespectra.core.npstats import tps, tp


def peak_wave_period(dset, smooth=True):
    """Smooth Peak wave period Tp.

    Args:
        - dset (xr.DataArray, xr.Dataset): Spectra array or dataset in wavespectra convention.
        - smooth (bool): Choose between the smooth (tps) or the raw (tp) peak wave period type.

    Returns:
        - tp (xr.DataArray): Peak wave period data array.

    """
    # Ensure DataArray
    if isinstance(dset, xr.Dataset):
        dset = dset[attrs.SPECNAME]
    # Choose peak period function
    if smooth:
        func = tps
    else:
        func = tp
    # Integrate over directions
    if attrs.DIRNAME in dset.dims:
        dset = dset.sum(dim=attrs.DIRNAME)
    # Vectorize won't work if dataset does not have dims other than (freq, dir)
    if set(dset.dims) - {attrs.FREQNAME, attrs.DIRNAME}:
        vectorize = True
    else:
        vectorize = False
    # Apply function over the full dataset
    darr = xr.apply_ufunc(
        func,
        dset,
        dset[attrs.FREQNAME],
        input_core_dims=[[attrs.FREQNAME], [attrs.FREQNAME]],
        vectorize=vectorize,
        dask="parallelized",
        output_dtypes=["float32"],
    )
    # Finalise
    darr.name = "tp"
    darr.attrs = {
        "standard_name": attrs.ATTRS.tp.standard_name,
        "units": attrs.ATTRS.tp.units
    }
    return darr


if __name__ == "__main__":

    import datetime
    from wavespectra import read_wavespectra

    dset = read_wavespectra("/source/consultancy/jogchum/route/route_feb21/p04/spec.nc")

    ds = dset.chunk({"time": 10000})

    t = datetime.datetime(1980, 4, 9, 12)
    dsi = ds.sel(time=t)

    # tp2 = ds.spec.tp2().load()
    # tp = ds.spec.tp().load()