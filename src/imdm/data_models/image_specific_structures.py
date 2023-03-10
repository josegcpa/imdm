#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MRI-specific data models.
"""

import os
import numpy as np
import pydicom
import SimpleITK as sitk
from PIL import Image
from dataclasses import dataclass,field

from .generic_models import DataValidator
from typing import Sequence,Tuple,Union,Callable,Any

def dicom_to_array(dcm_dataset: pydicom.dataset.FileDataset) -> np.ndarray:
    """Converts a ``pydicom`` ``FileDataset`` into a numpy array by accessing its
    pixel_array attribute.

    Args:
        dcm_dataset (pydicom.dataset.FileDataset): DICOM dataset.

    Returns:
        np.ndarray: numpy array.
    """
    return dcm_dataset.pixel_array

def sitk_to_array(sitk_image: sitk.SimpleITK.Image) -> np.ndarray:
    """Converts an SITK image into a numpy array using the 
    sitk.GetArrayFromImage function.

    Args:
        dcm_dataset (pydicom.dataset.FileDataset): SITK image.

    Returns:
        np.ndarray: numpy array.
    """
    return sitk.GetArrayFromImage(sitk_image)

@dataclass
class DicomFile(DataValidator):
    """DICOM file data validator. Expects as input to the ``validate`` method
    a path to a given file.

    Args:
        length (int, optional): checks the length of the pydicom FileDataset.
            Defaults to None.
        shape (int, optional): checks the shape of the pixel array. Defaults to
            None.
        range (int, optional): checks the values of the pixel array. Defaults 
            to None.
    """
    length: int = None
    shape: Sequence[int] = None
    range: Tuple[Union[int,float],Union[int,float]] = None
    type: Any = field(default=pydicom.dataset.FileDataset,
                      init=False,repr=False)

    def __post_init__(self):
        super().__post_init__()
        self.preprocess_fn = pydicom.dcmread
        self.values_fn = dicom_to_array
        self.add_check("path",os.path.exists,"raw")

@dataclass
class SitkFile(DataValidator):
    """SITK file data validator. Expects as input to the ``validate`` method
    a path to a given file.

    Args:
        length (int, optional): checks the length of the SITK Image (number of 
            pixels in the image). Defaults to None.
        shape (int, optional): checks the shape of the pixel array. Defaults to
            None.
        range (int, optional): checks the values of the pixel array. Defaults 
            to None.
    """
    length: int = None
    shape: Sequence[int] = None
    range: Tuple[Union[int,float],Union[int,float]] = None
    type: Any = sitk.SimpleITK.Image
    
    def __post_init__(self):
        super().__post_init__()
        self.preprocess_fn = sitk.ReadImage
        self.values_fn = sitk_to_array

        self.add_check("path",os.path.exists,"raw")

@dataclass
class NumpyFile(DataValidator):
    """Numpy file data validator. Expects as input to the ``validate`` method
    a path to a given file.

    Args:
        length (int, optional): checks the length of the numpy array (number of 
            pixels in the image). Defaults to None.
        shape (int, optional): checks the shape of the array. Defaults to None.
        range (int, optional): checks the values of the array. Defaults to
            None.
    """
    length: int = None
    shape: Sequence[int] = None
    range: Tuple[Union[int,float],Union[int,float]] = None
    type: Any = np.ndarray

    def __post_init__(self):
        super().__post_init__()
        self.preprocess_fn = np.load
        self.values_fn = None

        self.add_check("path",os.path.exists,"raw")

@dataclass
class ImageFile(DataValidator):
    """Image file data validator. Expects as input to the ``validate`` method
    a path to a given file.

    Args:
        length (int, optional): checks the length of the image (number of 
            pixels in the image). Defaults to None.
        shape (int, optional): checks the shape of the array. Defaults to None.
        range (int, optional): checks the values of the array. Defaults to
            None.
    """
    length: int = None
    shape: Sequence[int] = None
    range: Tuple[Union[int,float],Union[int,float]] = None
    type: Any = Image

    def __post_init__(self):
        super().__post_init__()
        self.preprocess_fn = Image.open
        self.values_fn = np.array

        self.add_check("path",os.path.exists,"raw")
