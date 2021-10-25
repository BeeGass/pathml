HDF5 Integration
================

.. note:: For advanced users

Overview
--------

A single whole-slide image may contain on the order of 10\ :superscript:`10` pixels, making it infeasible to
process entire images in RAM. ``PathML`` supports efficient manipulation of large-scale imaging data via
the **h5path** format, a hierarchical data structure which allows users to access small regions of the processed WSI
without loading the entire image. This feature reduces the RAM required to run a ``PathML`` workflow (pipelines can be
run on a consumer laptop), simplifies the reading and writing of processed WSIs, improves data exploration utilities,
and enables fast reading for downstream tasks (e.g. PyTorch Dataloaders). Since slides are managed on disk, your drive
must have sufficient storage. Performance will benefit from storage with fast read/write (SSD, NVMe). 

How it Works
------------

Each :class:`~pathml.core.slide_data.SlideData` object is backed by an ``.h5path`` file on disk.
All interaction with the ``.h5path`` file is handled automatically by the :class:`~pathml.core.h5managers.h5pathManager`.
For example, when a user calls ``slidedata.tiles[tile_key]``, the :class:`~pathml.core.h5managers.h5pathManager` will
retrieve the tile from disk and return it, without the user needing to worry about accessing the HDF5 file themself.
As tiles are extracted and passed to a preprocessing pipeline, the :class:`~pathml.core.h5managers.h5pathManager` also
handles aggregating the processed tiles into the ``.h5path`` file.
At the conclusion of preprocessing, the h5py object can optionally be
permanently written to disk in ``.h5path`` format via the
:meth:`SlideData.write() <pathml.core.SlideData.write>` method.

About HDF5
----------

The internals of ``PathML`` as well as the ``.h5path`` file format are based on the hierarchical data format
`HDF5 <https://en.wikipedia.org/wiki/Hierarchical_Data_Format>`_, implemented by
`h5py <https://docs.h5py.org/en/stable/>`_.

HDF5 format consists of 3 types of elements:

.. list-table::
    :widths: 15 30
    :align: center

    * - Groups
      - A "container," similar to a directory in a filesystem. Groups may contain Datasets, Attributes, or other Groups.
    * - Datasets
      - Rectangular collection of data elements. Wraps ``np.ndarray`` .
    * - Attributes
      - Small named metadata elements. Each attribute is attached to a Group or Dataset.

``Groups`` are container-like and can be queried like dictionaries:

.. code-block::

   import h5py
   root = h5py.File('path/to/file.h5path', 'r')
   masks = root['masks']

``Datasets`` can be treated like ``numpy.ndArray`` objects:

.. important::

    To retrieve a ``numpy.ndArray`` object from ``h5py.Dataset`` you must slice the Dataset with
    NumPy fancy-indexing syntax: for example [...] to retrieve the full array, or [a:b, ...] to
    return the array with first dimension sliced to the interval [a, b].

.. code-block::

   import h5py
   root = h5py.File('path/to/file.h5path', 'r')
   im = root['array'][...]
   im_slice = root['array'][0:100, 0:100, :]

``Attributes`` are stored in a ``.attrs`` object which can be queried like a dictionary:

.. code-block::

   import h5py
   root = h5py.File('path/to/file.h5path', 'r')
   tile_shape = root['tiles'].attrs['tile_shape']

``.h5path`` File Format
-----------------------

**h5path** utilizes a self-describing hierarchical file system similar to :class:`~pathml.core.slide_data`.

The full-resolution whole-slide image is stored in the ``array`` Dataset.

Whole-slide masks are stored in the ``masks/`` Group. All masks are enforced to be the same shape as the image array.

Tile metadata is stored in the ``tiles/`` Group, but tile-level images and masks are not stored separately.
Instead, to retrieve an individual tile, the coordinates and tile_shape attributes are used to slice the
corresponding region from the whole-slide image and masks.

Here we examine the **h5path** file format in detail:

::

    root/                           (Group)
    ├── fields/                     (Group)
    │   ├── name                    (Attribute, str)
    │   ├── shape                   (Attribute, tuple)
    │   ├── labels                  (Group)
    │   │   ├── label1              (Attribute, [str, int, float, array])
    │   │   ├── label2              (Attribute, [str, int, float, array])
    │   │   └── etc...
    │   └── slide_type              (Group)
    │       ├── stain               (Attribute, str)
    │       ├── tma                 (Attribute, bool)
    │       ├── rgb                 (Attribute, bool)
    │       ├── volumetric          (Attribute, bool)
    │       └── time_series         (Attribute, bool)
    ├── array                       (Dataset)
    ├── masks/                      (Group)
    │   ├── mask1                   (Dataset, array)
    │   ├── mask2                   (Dataset, array)
    │   └── etc...
    ├── counts                      (Group)
    │   └── `.h5ad` format
    └── tiles/                      (Group)
        ├── tile_shape              (Attribute, tuple)
        ├── tile_key1/              (Group)
        │   ├── coords              (Attribute, tuple)
        │   ├── name                (Attribute, str)
        │   └── labels/             (Group)
        │       ├── label1          (Attribute, [str, int, float, array])
        │       ├── label2          (Attribute, [str, int, float, array])
        │       └── etc...
        ├── tile_key2/              (Group)
        │   └── etc...
        └── etc...


Reading and Writing
-------------------

:class:`~pathml.core.slide_data.SlideData` objects are easily written to **h5path** format
by calling :meth:`SlideData.write() <pathml.core.slide_data.SlideData.write>`.
All files with ``.h5`` or ``.h5path`` extensions are loaded to :class:`~pathml.core.slide_data.SlideData` objects
automatically.
