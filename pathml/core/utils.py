"""
Copyright 2021, Dana-Farber Cancer Institute and Weill Cornell Medicine
License: GNU GPL 2.0
"""

from collections import OrderedDict
import numpy as np
import ast
from dataclasses import asdict

import pathml.core.slide_backends
import pathml.core.slide_data


# TODO: Fletcher32 checksum?
def writedataframeh5(h5, name, df):
    """
    Write dataframe as h5 dataset.
    """
    dataset = h5.create_dataset(
        str(name),
        data = df,
        chunks = True,
        compression = "gzip",
        compression_opts = 5,
        shuffle = True
    )


def writestringh5(h5, name, st):
    """
    Write string as h5 attribute.
    """
    stringasarray = np.string_(str(st))
    h5.attrs[str(name)] = stringasarray


def writedicth5(h5, name, dic):
    """
    Write dict as h5 dataset. This is not an attribute to accomodate vals that are not strings.
    """
    h5.create_group(str(name))
    for key, val in dic.items():
        h5[name].attrs.create(
            str(key),
            data = val
        )


def writetupleh5(h5, name, tup):
    """
    Write tuple as h5 attribute.
    """
    tupleasarray = np.string_(str(tup))
    h5.attrs[str(name)] = tupleasarray


def readtupleh5(h5, key):
    """
    Read tuple from h5.
    """
    return eval(h5.attrs[key]) if key in h5.attrs.keys() else None 


def writetilesdicth5(h5, name, dic):
    """
    Write tiles as h5py.Dataset.
    """
    if name not in h5.keys():
        h5.create_group(str(name), track_order = True)
    assert isinstance(name, (str, tuple)), f"name of h5py.Dataset where tilesdict is written"
    name = str(name)
    for tile in dic.keys():
        tile = str(tile)
        h5[name].create_group(tile, track_order = True)
        for field in dic[tile]:
            # field is name, coords
            if isinstance(dic[tile][field], (str, type(None))):
                stringasarray = np.string_(str(dic[tile][field]))
                h5[name][tile].create_dataset(
                    field,
                    data = stringasarray,
                    track_order = True
                )
            # field is labels
            elif isinstance(dic[tile][field], (dict, OrderedDict)):
                h5[name][tile].create_group(str(field))
                for key, val in dic[tile][field].items():
                    h5[name][tile][field].attrs.create(
                        str(key),
                        data = val
                    )
            # field is slide_type -- convert to dict
            elif isinstance(dic[tile][field], pathml.core.SlideType):
                h5[name][tile].create_group(str(field))
                slide_type_dict = asdict(dic[tile][field])
                for key, val in slide_type_dict.items():
                    h5[name][tile][field].attrs.create(
                        str(key),
                        data = val
                    )
            else:
                raise Exception(f"could not write tilesdict element. field={field}. type(dic[tile][field])={type(dic[tile][field])}")


def readtilesdicth5(h5):
    """
    Read tiles to dict from h5py.Dataset.

    Usage:
        tiles = readtilesdicth5(h5['tiles'])
    """
    tilesdict = OrderedDict()
    for tile in h5.keys():
        name = ast.literal_eval(h5[tile]['name'][...].item().decode('UTF-8')) if 'name' in h5[tile].keys() else None
        labels = h5[tile]['labels'] if 'labels' in h5[tile].keys() else None
        # read the attributes
        if labels:
            labeldict = {}
            # iterate over key/val pairs stored in labels.attr
            for attr in labels.attrs:
                val = labels.attrs[attr]
                # check if val is a single element
                # if val is bytes then decode to str, otherwise leave it (it is a float or int)
                if isinstance(val, bytes):
                    val = val.decode('UTF-8')
                labeldict[attr] = val
            labels = labeldict if labeldict else None
        coords = h5[tile]['coords'][...].item().decode('UTF-8') if 'coords' in h5[tile].keys() else None
        subdict = {
                'name': name,
                'labels': labels,
                'coords': coords,
        }
        tilesdict[tile] = subdict
    return tilesdict
