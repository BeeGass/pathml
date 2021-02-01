import pytest
import numpy as np
import string
import random

from pathml.core.tiles import Tiles
from pathml.core.tile import Tile
from pathml.core.masks import Masks


@pytest.fixture
def emptytiles():
    return Tiles()


@pytest.fixture
def tile_nomasks(shape=(224, 224, 3), i=1, j=3):
    testtile = Tile(np.random.randn(*shape), coords = (i, j))
    return testtile

@pytest.fixture
def tile_withmasks(shape=(224, 224, 3), coords=(1, 3), stack=50, labeltype=str):
    if labeltype == str:
        letters = string.ascii_letters + string.digits
        maskdict = {}
        for i in range(stack):
            randomkey = 'test' + ''.join(random.choice(letters) for _ in range(i))
            maskdict[randomkey] = np.random.randint(2, size = shape)
        masks = Masks(maskdict)
    return Tile(np.random.random_sample(shape), coords = coords, masks = masks)


@pytest.mark.parametrize("incorrect_input", ["string", True, 5, [5, 4, 3], {"dict": "testing"}])
def test_init_incorrect_input(incorrect_input):
    with pytest.raises(ValueError):
        tiles = Tiles(incorrect_input)


def test_init(tile_withmasks):
    tilelist = [tile_withmasks(coords = (k, k)) for k in range(20)]
    tiledict = {(k, k): tile_withmasks(coords = (k, k)) for k in range(20)}
    tiles = Tiles(tilelist)
    tiles2 = Tiles(tiledict)
    assert tiles[str((0, 0))] == tilelist[0]
    assert tiles2[str((0, 0))] == tiledict[str((0, 0))]


@pytest.mark.parametrize("incorrect_input", ["string", None, True, 5, [5, 4, 3], {"dict": "testing"}])
def test_add_incorrect_input(incorrect_input, emptytiles, tile_nomasks):
    tiles = emptytiles
    tile = tile_nomasks
    with pytest.raises(ValueError):
        tiles.add(incorrect_input, tile)
        tiles.add((1, 3), incorrect_input)


def test_add_get_nomasks(emptytiles, tile_nomasks):
    tiles = emptytiles
    tile = tile_nomasks
    tiles.add((1, 3), tile)
    assert (tiles[(1, 3)].image == tile.image).all()
    assert (tiles[0].image == tile.image).all()


def test_add_get_withmasks(emptytiles, tile_withmasks):
    tiles = emptytiles
    testmask = tile_withmasks.masks[0]
    tile = tile_withmasks
    tiles.add((1, 3), tile)
    assert (tiles[(1, 3)].masks[0] == testmask).all()
    assert (tiles[0].masks[0] == testmask).all()


@pytest.mark.parametrize("incorrect_input", ["string", None, True, 5, [5, 4, 3], {"dict": "testing"}])
def test_remove_incorrect_input(incorrect_input, emptytiles, tile_nomasks):
    tiles = emptytiles
    tile = tile_nomasks
    tiles.add((1, 3), tile)
    with pytest.raises(KeyError):
        tiles.remove(incorrect_input)


def test_remove_nomasks(emptytiles, tile_nomasks):
    tiles = emptytiles
    tile = tile_nomasks
    tiles.add((1, 3), tile)
    tiles.remove((1, 3))
    with pytest.raises(Exception):
        triggerexception = tiles['(1, 3)']

def test_slice_nomasks(emptytiles, tile_nomasks):
    # slice one tile
    tiles = emptytiles
    tile = tile_nomasks
    tiles.add((1,3), tile)
    slices = [slice(2,5)]
    for s in tiles.slice(slices):
        print(s)

def test_slice_withmasks(emptytiles, tile_withmasks):
    tiles = emptytiles
    tile = tile_withmasks
    tiles.add((1,3), tile)
    slices = [slice(2,5)]
    for s in tiles.slice(slices):
        print(s)
