# `imdm` - Python data models for image

## What's the point

This module contains a few helpful and flexible data models which can be easily extended for other applications. Here, I focused on making some (very) specific validators focusing on MRI data. These can be used to test DICOM files, SITK-readable images or numpy-loadable arrays.

## Installation

The project should be readily instalable with `poetry` (recommended) by running `poetry install`. 

## Usage

Two fundamental classes are used here: `DataValidator`, which focuses on validating a specific type of data, and `DataModel` which focuses on validating a sample (composed by multiple types of data).

### `DataValidators`

Defining `DataValidators` is relatively easy:

```python
from mridm import DataValidator

data_validator = DataValidator(type=str,length=11,shape=None,range=None)
```

and running data validations is just as easy:

```python
output = data_validator.validate("test_string")

print(output)

>>> {"type":True,"length":True,"shape":None,"range":None}
```

The `DataValidator` method automatically checks for `type`, `length`, `shape` and `range` (if specified). If necessary, users can also add their own methods. For example, if you would to check whether a given path exists:

```python
import os

data_validator.add_test(key="path",test_fn=os.path.exists,data_stage="raw")

output = data_validator.validate("test_string")

print(output)

>>> {"type":True,"length":True,"shape":None,"range":None,"path":False}
```

Easy! All arguments are relatively clear, but `data_stage` is somewhat more ellusive; for this reason I introduce here the concept of three data stages:

* `raw` - the input exactly as it is. This is useful to test whether a file exists.
* `preprocessed_data` - if a `preprocess_fn` is specified in the `DataValidator` constructor, tests can be applied to these functions. For instance, the `type` check is automatically ran on the `preprocessed_data` stage. 
* `value_data` - some files (SITK-readable files, for instance) require some non-obvious wrangling before one can actually use their values as `numpy` arrays, which is the assumed format for checking the `range`. This function (`value_fn`) is applied to the output of `preprocess_fn`. 

If no `preprocess_fn` or `value_fn` are supplied, then `preprocessed_data` and `value_fn` will be identical to the input data.

### `DataModel`

A `DataModel` is simply a structure of `DataValidators`, i.e.

```python
from mridm import DataValidator,DataModel

data_model = DataModel(structures={
    "a":DataValidator(type=str,length=11,shape=None,range=None),
    "b":DataValidator(type=int,length=None,shape=None,range=[-10,10])
    })
```

This `data_model` can then be applied to any given data input that follows a structure similar to `data_model.structures`.

### MRI- and image-specific data validators

An easy-to-use data validators have been implemented specifically for image data (`ImageFile`). I work with images, so these were especially useful for me. 

Additionally, since I work with a lot of MRI data, specific methods for MRI data were also implemented (`DicomFile` and `SitkFile`). A more generic method for `numpy` files has also been (`NumpyFile`).

### `pprint`

`pprint` is a simple function that allows you to more easily inspect the output of `DataValidator` and `DataModel`. It comes with colours!

## Testing

Tests for the data validators and models are available in `mridm/data_models/testing`. Test images were collected from:

* https://www.rubomedical.com/dicom_files/ (.dcm)
* https://github.com/neurolabusc/niivue-images (.nii.gz)