# h5 utils
from collections import OrderedDict
import numpy as np
import h5py
import ast

import pathml.core.slide_classes
import pathml.core.slide_backends


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
    stringasarray = np.array(str(st), dtype = object)
    h5.attrs[str(name)] = stringasarray


def writedicth5(h5, name, dic):
    """
    Write dict as h5 dataset. This is not an attribute to accomodate vals that are not strings.
    """
    h5.create_dataset(
        str(name),
        data = str(dic)
    )               


def writetupleh5(h5, name, tup):
    """
    Write tuple as h5 attribute.
    """
    tupleasarray = np.array(str(tup), dtype = object)
    h5.attrs[str(name)] = tupleasarray


def readtupleh5(h5, key):
    """
    Read tuple from h5.
    """
    return eval(h5.attrs[key]) if key in h5.attrs.keys() else None 


def writetilesdicth5(h5, name, dic):
    """
    Write tilesdict as h5py.Dataset.
    """
    if name not in h5.keys():
        h5.create_group(str(name), track_order = True)
    assert isinstance(name, (str, tuple)), f"name of h5py.Dataset where tilesdict is written"
    name = str(name)
    for tile in dic.keys():
        tile = str(tile)
        h5[name].create_group(tile)
        for field in dic[tile]:
            if isinstance(dic[tile][field], (str, type(None))):
                stringasarray = np.array(str(dic[tile][field]), dtype = object)
                h5[name][tile].create_dataset(
                    field,
                    data = stringasarray
                )
            elif isinstance(dic[tile][field], (dict, OrderedDict)):
                h5[name][tile].create_dataset(
                    str(field),
                    data = str(dic[tile][field]) 
                )               
            else:
                raise Exception(f"could not write tilesdict element {dic[name][tile]}")


def readtilesdicth5(h5):
    """
    Read tilesdict to dict from h5py.Dataset.

    Usage:
        tilesdict = readtilesdicth5(h5['tiles/tilesdict'])
    """
    tilesdict = OrderedDict()
    for tile in h5.keys():
        name = ast.literal_eval(h5[tile]['name'][...].item().decode('UTF-8')) if 'name' in h5[tile].keys() else None
        labels = h5[tile].get('labels')[...].tolist() if 'labels' in h5[tile].keys() else None
        coords = h5[tile]['coords'][...].item().decode('UTF-8') if 'coords' in h5[tile].keys() else None
        slidetype = ast.literal_eval(h5[tile]['slidetype'][...].item().decode('UTF-8')) if 'slidetype' in h5[tile].keys() else None
        if slidetype:
            # TODO: better system for specifying slide classes.
            #  Since it's saved as string here, should have a clean string identifier for each class
            #  currently its using repr essentially
            if slidetype == "<class 'pathml.core.slide_backends.OpenSlideBackend'>":
                slidetype = pathml.core.slide_backends.OpenSlideBackend
            elif slidetype == "<class 'pathml.core.slide_backends.BioFormatsBackend'>":
                slidetype = pathml.core.slide_backends.BioFormatsBackend
            elif slidetype == "<class 'pathml.core.slide_backends.DICOMBackend'>":
                slidetype = pathml.core.slide_backends.DICOMBackend
            elif slidetype == "<class 'pathml.core.slide_classes.HESlide'>":
                slidetype = pathml.core.slide_classes.HESlide
        if labels:
            labels = ast.literal_eval(labels.decode('UTF-8'))
        subdict = {
                'name': name,
                'labels': labels,
                'coords': coords,
                'slidetype': slidetype 
        }
        tilesdict[tile] = subdict
    return tilesdict
