from warnings import warn
import numpy as np

from pathml.core.multiparametric_slide import MultiparametricSlide2d

import javabridge
import bioformats


# there's something that causes pytest to hang...
# may be related to: https://github.com/microsoft/vscode-python/issues/7055
"""@pytest.fixture
def smalltif_example():
    path = "tests/testdata/smalltif.tif"
    javabridge.start_vm(class_path=bioformats.JARS, run_headless = True)
    data = bioformats.formatreader.load_using_bioformats(path, rescale=False)
    im_np = np.asarray(data, dtype = np.uint8)
    return im_np"""

"""
def test_multiparametric_slide():
    wsi = MultiparametricSlide2d(path = "tests/testdata/smalltif.tif")
    assert wsi.name == "smalltif"
    assert wsi.path == "tests/testdata/smalltif.tif"
    slide_data = wsi.load_data()

    # load manually for comparison
    path = "tests/testdata/smalltif.tif"
    javabridge.start_vm(class_path = bioformats.JARS)
    data = bioformats.formatreader.load_using_bioformats(path, rescale = False)
    javabridge.kill_vm()
    im_np = np.asarray(data, dtype = np.uint8)

    assert np.allclose(slide_data.image, im_np)

    # make sure slide class hierarchy is working

    assert isinstance(wsi, BaseSlide)
    assert isinstance(wsi, Slide2d)
"""
