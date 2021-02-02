from pathml.core.slide_data import SlideData
from pathml.core.slide_backends import OpenSlideBackend


class RGBSlide(SlideData):
    """
    Class for any RGB slide. Uses OpenSlide backend.
    Refer to :class:`~pathml.core.slide_data.SlideData` for full documentation.
    """
    def __init__(self, *args, **kwargs):
        kwargs["slide_backend"] = OpenSlideBackend
        super().__init__(*args, **kwargs)


class HESlide(RGBSlide):
    """
    Class for any H&E slide. Uses OpenSlide backend.
    Refer to :class:`~pathml.core.slide_data.SlideData` for full documentation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
