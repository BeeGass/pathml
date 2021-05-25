"""
Copyright 2021, Dana-Farber Cancer Institute and Weill Cornell Medicine
License: GNU GPL 2.0
"""

import numpy as np
import os
from pathlib import Path
from collections import OrderedDict
import h5py

import pathml.core.h5managers


class Masks:
    """
    Object holding masks.

    Args:
        masks(dict): dictionary of np.ndarray objects representing ex. labels, segmentations.
    """

    def __init__(self, h5manager, masks = None):
        self.h5manager = h5manager
        if masks:
            if not isinstance(masks, dict):
                raise ValueError(f"masks must be passed as dicts of the form key1:mask1,key2:mask2,...")
            for val in masks.values():
                if not isinstance(val, np.ndarray):
                    raise ValueError(f"can not add {type(val)}, mask must be of type np.ndarray")
            for key in masks.keys():
                if not isinstance(key, str):
                    raise ValueError(f"can not add {type(key)}, key must be of type str")
            self._masks = OrderedDict(masks)
        else:
            self._masks = OrderedDict()
        for mask in self._masks:
            self.h5manager.add_mask(mask, self._masks[mask])
        del self._masks

    def __repr__(self):
        rep = f"Masks(keys={self.h5manager.h5['masks'].keys()})"
        return rep

    def __len__(self):
        return len(self.h5manager.h5["masks"].keys())

    def __getitem__(self, item):
        return self.h5manager.get_mask(item)

    def __setitem__(self, key, mask):
        self.h5manager.update_mask(key, mask)

    def add(self, key, mask):
        """
        Add mask indexed by key to self.h5manager.

        Args:
            key (str): key
            mask (np.ndarray): array of mask. Must contain elements of type int8
        """
        self.h5manager.add_mask(key, mask)

    def slice(self, slicer):
        """
        Slice all masks in self.h5manager extending of numpy array slicing.

        Args:
            slices: list where each element is an object of type slice indicating
                    how the dimension should be sliced
        """
        if not (isinstance(slicer, list) and all([isinstance(a, slice) for a in slicer])):
            raise KeyError(f"slices must of of type list[slice] but is {type(slicer)} with elements {type(slicer[0])}")
        sliced = {key:mask for key, mask in self.h5manager.slice_masks(slicer)} 
        return sliced

    def remove(self, key):
        """
        Remove mask.

        Args:
            key(str): key indicating mask to be removed
        """
        self.h5manager.remove_mask(key)
