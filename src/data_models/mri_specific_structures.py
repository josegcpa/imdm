"""
MRI-specific data models.
"""

__author__ = "José Guilherme de Almeida"
__version__ = "0.1.0"
__license__ = "MIT"
__email__ = "jose.gcp.almeida@gmail.com"

import os
import numpy as np
import pydicom
import SimpleITK as sitk
from dataclasses import dataclass

from .generic_models import DataValidator
from typing import Sequence,Tuple,Union

def dicom_to_array(dcm_dataset: pydicom.dataset.FileDataset) -> np.ndarray:
    return dcm_dataset.pixel_array

def sitk_to_array(sitk_image: sitk.SimpleITK.Image) -> np.ndarray:
    return sitk.GetArrayFromImage(sitk_image)

@dataclass
class DicomFile(DataValidator):
    length: int = None
    shape: Sequence[int] = None
    range: Tuple[Union[int,float],Union[int,float]] = None

    def __post_init__(self):
        super().__post_init__()
        self.type = pydicom.dataset.FileDataset
        self.preprocess_fn = pydicom.dcmread
        self.values_fn = dicom_to_array
        
        self.add_test("path",os.path.exists,"raw")

@dataclass
class SitkFile(DataValidator):
    length: int = None
    shape: Sequence[int] = None
    range: Tuple[Union[int,float],Union[int,float]] = None

    def __post_init__(self):
        super().__post_init__()
        self.type = sitk.SimpleITK.Image
        self.preprocess_fn = sitk.ReadImage
        self.values_fn = sitk_to_array
