import pytest
from dask.distributed import Client
import numpy as np
from pathlib import Path

from pathml.core.slide_classes import HESlide
from pathml.core.slide_data import SlideData
from pathml.core.slide_dataset import SlideDataset
from pathml.core.tile import Tile
from pathml.preprocessing.pipeline import Pipeline
from pathml.preprocessing.transforms import BoxBlur


@pytest.fixture()
def slide_dataset():
    n = 4
    labs = {"testing": "testlabel", "test2": np.array([2, 3, 4])}
    slide_list = [HESlide("tests/testdata/small_HE.svs", name = f"slide{i}", labels = labs) for i in range(n)]
    slide_dataset = SlideDataset(slide_list)
    return slide_dataset


def test_dataset_len_getitem(slide_dataset):
    # check len and getitem
    assert len(slide_dataset) == 4
    for i in range(len(slide_dataset)):
        assert isinstance(slide_dataset[i], SlideData)


def test_dataset_save(tmp_path, slide_dataset):
    slide_dataset.write(tmp_path)
    # now check each file
    for slide in slide_dataset:
        fname = tmp_path / slide.name + ".h5path"
        assert fname.is_file()


def test_run_pipeline_and_tile_dataset_and_reshape(slide_dataset):
    pipeline = Pipeline([BoxBlur(kernel_size = 15)])
    # start the dask client
    client = Client()
    # run the pipeline
    slide_dataset.run(pipeline = pipeline, client = client, tile_size = 50)
    # close the dask client
    client.close()
    assert len(slide_dataset.tile_dataset) == sum([len(s.tile_dataset) for s in slide_dataset])
    tile, labels = slide_dataset.tile_dataset[0]
    assert isinstance(tile, Tile) and isinstance(labels, dict)
    assert tile.image.shape == (50, 50, 3)

    slide_dataset.reshape(shape = (25, 25, 3))
    tile_after_reshape, labels_after_reshape = slide_dataset.tile_dataset[0]
    assert isinstance(tile_after_reshape, Tile) and isinstance(labels_after_reshape, dict)
    assert tile_after_reshape.image.shape == (25, 25, 3)

    assert labels_after_reshape == labels

