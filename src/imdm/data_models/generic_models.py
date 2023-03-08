#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generic data types and classes used to construct data models to be used in data
validation.
"""

__author__ = "José Guilherme de Almeida"
__version__ = "0.1.0"
__license__ = "MIT"
__email__ = "jose.gcp.almeida@gmail.com"

import logging
import numpy as np
from termcolor import colored

from dataclasses import dataclass

from typing import Dict, Sequence, Union, Any, Tuple, Callable

DataStructure = Union[
    Sequence[Any],
    Dict[str,Any]]

@dataclass
class DataValidator:
    """
    Class to perform individual data validation with minimal validation 
    methods (type checking, length checking, shape checking and range 
    checking). All validation methods are called using ``self.validate``.
    
    To add and remove tests, the functions ``self.add_test`` and 
    ``self.remove_test`` should be used to ensure that everything works. The 
    ``preprocess_fn`` and ``values_fn`` arguments can be used to preprocess the
    data before other tests and to obtain values from the data, respectively.
    To make sure that tests are applied to the correct stages of the data (
    "raw", "preprocessed_data" and "values"), tests should be annotated with
    this when being added with the function ``self.add_test``: for instance, if
    a test ``test_something`` is to be applied to the preprocessed input, then to
    add this test one should run 
    ``self.add_test("key",test_something,"preprocessed")``. The value extraction
    function (``values_fn``) is applied _after_ the input has been preprocessed
    (if any preprocessing function is provided).
    
    args:
        type (Any, optional): checks if data has this type. Defaults to None.
        length (int, optional): checks if data has this len. Defaults to None.
        shape (Sequence[int], optional): checks if data has this shape. 
            Defaults to None.
        range (Tuple[Union[int,float],Union[int,float]], optional): checks if 
            data is within a given range. Defaults to None.
        dtype (Any, optional): checks if data has a specific data type (as 
            determined by ``data.dtype``). Defaults to None.
        preprocess_fn (Callable, optional): preprocessing function. Defaults to
            None (no preprocessing).
        values_fn (Callable, optional): function to extract values from 
            (preprocessed) data. Defaults to None (no value value extraction).
        verbose (int, optional): sets the level of verbosity. Defaults to 
            logging.WARNING.
    """
    type: Any = None
    length: int = None
    shape: Sequence[int] = None
    range: Tuple[Union[int,float],Union[int,float]] = None
    dtype: Any = None
    preprocess_fn: Callable = None
    values_fn: Callable = None
    verbose: int = logging.WARNING

    def __post_init__(self):
        self._test_dict = {
            "raw":{},
            "preprocessed_data":{
                "type": self.check_type
            },
            "values":{
                "length": self.check_length,
                "shape": self.check_shape,
                "range": self.check_range,
                "dtype": self.check_dtype
            },
            
        }

        self.test_names = ["type","length","shape","range","dtype"]
        self.logger = logging.getLogger('data_validator')
        self.logger.setLevel(self.verbose)
    
    @property
    def test_dict(self) -> Dict[str,Tuple[Callable,str]]:
        """Returns the test dictionary.

        Returns:
            Dict[str,Tuple[Callable,str]]: dictionary with tests and their
                respective data stages.
        """
        return self._test_dict
    
    def __len__(self) -> int:
        """Returns the number of tests.

        Returns:
            int: number of tests.
        """
        return len(self._test_dict)
    
    def __setattr__(self, attr: str, value: Any):
        """Overrinding the default __setattr__ method to prevent direct 
        definition of ``test_dict``.

        Args:
            attr (str): attribute name.
            value (Any): attribute value.

        Raises:
            ValueError: raises an error if attr == "test_dict".
        """
        if attr == "test_dict":
            raise ValueError("test_dict cannot be altered. Please use the \
                add_test and remove_test methods")
        else:
            super().__setattr__(attr, value)

    def add_test(self, key: str, test_fn: Callable, data_stage: str):
        """Adds a test to the test dictionary.

        Args:
            key (str): name of the dictionary.
            test_fn (Callable): function corresponding to the test. Must return
                a boolean (True or False).
            data_stage (str): data stage for the application of this test.
        """
        if key in self.test_names:
            raise ValueError(f"'{key}' test is already defined")
        self._test_dict[data_stage][key] = (test_fn)
    
    def remove_test(self, key: str, data_stage: str=None):
        """Removes a test.

        Args:
            key (str): key of the test to be removed.
            data_stage (str, optional): data stage at which the test is 
                performed. Defaults to None (removes any instances of key).
        """
        if data_stage is not None:
            del self._test_dict[data_stage][key]
        else:
            for data_stage in self._test_dict:
                if key in self.test_dict[data_stage]:
                    del self.test_dict[data_stage][key]
        if key in self.test_names:
            self.test_names.remove(key)
        
    def check_dtype(self, data: Any) -> Union[bool,None]:
        """Tests whether ``data.dtype`` is the same as ``self.dtype``.

        Args:
            data (Any): input data.

        Returns:
            Union[bool,None]: boolean if ``self.dtype`` is defined (True if 
                data.dtype == self.dtype and False otherwise). None if 
                self.dtype is None.
        """
        if self.dtype is not None:
            return data.dtype == self.type
    
    def check_type(self, data: Any) -> Union[bool,None]:
        """Tests whether ``type(data)`` is the same as ``self.type``.

        Args:
            data (Any): input data.

        Returns:
            Union[bool,None]: boolean if ``self.type`` is defined (True if 
                type(data) == self.type and False otherwise). None if 
                self.type is None.
        """
        if self.type is not None:
            return type(data) == self.type
    
    def check_length(self, data: Any) -> Union[bool,None]:
        """Tests whether ``len(data)`` is the same as ``self.length``.

        Args:
            data (Any): input data.

        Returns:
            Union[bool,None]: boolean if ``self.length`` is defined (True if 
                len(data) == self.length and False otherwise). None if 
                self.length is None.
        """
        if self.length is not None:
            return len(data) == self.length
    
    def check_shape(self, data: Any) -> Union[bool,None]:
        """Tests whether ``data.shape`` is the same as ``self.shape``.

        Args:
            data (Any): input data.

        Returns:
            Union[bool,None]: boolean if ``self.shape`` is defined (True if 
                data.shape == self.shape and False otherwise). None if 
                self.shape is None.
        """
        if self.shape is not None:
            print(data.shape)
            return data.shape == self.shape
    
    def check_range(self, data: Any) -> Union[bool,None]:
        """Tests whether the minimum and maximum values of data (obtained using
        ``np.min`` and ``np.max``, respectively) correspond to ``self.range[0]`` and
        ``self.range[1]``.
        
        Args:
            data (Any): input data.

        Returns:
            Union[bool,None]: boolean if ``self.range`` is defined (True if 
                the minimum and maximum values of data are within self.range, 
                False otherwise). None if self.range is None.
        """
        if self.range is not None:
            check = True
            if self.range[0] is not None:
                if np.min(data) < self.range[0]:
                    check = False
            if self.range[1] is not None:
                if np.max(data) > self.range[1]:
                    check = False
            return check
    
    def validate(self, 
                 data: Any, 
                 strict: bool=True) -> Dict[str,Union[bool,None]]:
        """Runs all of the tests in test_dict on the input data. Tests are 
        performed sequentially by data stages and execution halts if a test
        in the previous stage fails. To avoid this behaviour, set ``strict``
        to ``True``.

        Args:
            data (Any): input data.
            strict (bool, optional): requires that tests at a previous stage
                succeed (no ``False`` values) to execute the next stages. 
                Defaults to ``True``.

        Returns:
            Dict[str,Union[bool,None]]: a dictionary where the keys are the 
                same as those in ``test_dict`` and the values are the result of
                the checks.
        """
        stop = False
        validation_dict = {k:None for k in self.test_names}
        for k in self.test_dict["raw"]:
            result = self.test_dict["raw"][k](data)
            if result == False:
                stop = True
            validation_dict[k] = result

        if (stop is False) or (strict is False):
            if self.preprocess_fn is not None:
                data = self.preprocess_fn(data)
            for k in self.test_dict["preprocessed_data"]:
                result = self.test_dict["preprocessed_data"][k](data)
                if result == False:
                    stop = True
                validation_dict[k] = result

        if (stop is False) or (strict is False):
            if self.values_fn is not None:
                data = self.values_fn(data)
            for k in self.test_dict["values"]:
                result = self.test_dict["values"][k](data)
                if result == False:
                    stop = True
                validation_dict[k] = result

        return validation_dict

DataValidationStructure = Union[
    Sequence[DataValidator],
    Dict[str,DataValidator]]
DataModelOutput = Dict[str,Union[bool,Dict[str,bool]]]

@dataclass
class DataModel:
    """Orchestrates a series of ``DataValidator`` objects and applies them to a
    complex input data structure. The supported data structures are sequences
    and dictionaries. For instance, defining ``structures`` as:

    ``{"a":DataValidator(type=str),"b":DataValidator(type=int)}``
    
    will expect the input to the validate function to be a dictionary with, at
    least, keys ``"a"`` and ``"b"``. 
    
    Args:
        structures (DataValidationStructure): sequence or dictionary of 
            DataValidator objects.
        strict (bool, optional): if the input data to ``validate`` does not have
            the same structure as ``structures``, does not perform any individual
            check.
        verbose (int, optional): sets the level of verbosity. Defaults to 
            logging.WARNING.
    """
    structures: DataValidationStructure
    strict: bool = False
    verbose: int = logging.WARNING
    
    def __post_init__(self):
        self.is_dict = isinstance(self.structures,dict)

        self.logger = logging.getLogger('data_model_validator')
        self.logger.setLevel(self.verbose)
    
    def check_type(self, data_structure: DataStructure) -> bool:
        """Checks if ``type(data_structure) == type(self.structures)``.

        Args:
            data_structure (DataStructure): input sequence or dictionary.

        Returns:
            bool: True if ``type(data_structure) == type(self.structures)``, False
                otherwise.
        """
        return type(data_structure) == type(self.structures)
    
    def check_length(self, data_structure: DataStructure) -> bool:
        """Checks if ``len(data_structure) == len(self.structures)``.

        Args:
            data_structure (DataStructure): input sequence or dictionary.

        Returns:
            bool: True if ``len(data_structure) == len(self.structures)``, False
                otherwise.
        """
        return len(data_structure) == len(self.structures)
    
    def check_keys(self, data_structure: DataStructure) -> Union[bool,None]:
        """Checks if ``data_structure.keys() == self.structures.keys()``. Works 
        only for dictionaries.

        Args:
            data_structure (DataStructure): input sequence or dictionary.

        Returns:
            Union[bool,None]: True if the intersection of 
                ``data_structure.keys()`` and ``structures.keys()`` is the same 
                length as ``self.structure.keys()``, False otherwise. Returns 
                None if input is not a dictionary.
        """
        if isinstance(data_structure,dict) and isinstance(self.structures,dict):
            structure_keys = set(self.structures.keys())
            data_keys = set(data_structure.keys())
            inter_size = len(set.intersection(structure_keys,data_keys))
            correct_size = len(structure_keys)
            return inter_size == correct_size
        return None
    
    def validate(self, data_structure: DataStructure) -> DataModelOutput:
        """Runs all the checks defined in ``self.structures``.

        Args:
            data_structure (DataStructure): input data structure. Should be a
                sequence or a dictionary.

        Returns:
            DataModelOutput: dictionary containing all checks. Particularly,
                checks if the type, length and keys (if dict) are the same 
                between ``data_structure`` and ``self.structures`` (in 
                ``"structure_type"``, ``"structure_length"`` and 
                ``"structure_keys"``). After this, it runs all of the checks in
                ``self.structures`` and stores the output dictionary in the 
                ``"data_check"`` key.
        """
        validation_dict = {
            "structure_type": self.check_type(data_structure),
            "structure_length": self.check_length(data_structure),
            "structure_keys": self.check_keys(data_structure),
            "data_check": None
        }
        
        failed_tests = [validation_dict[k] == False for k in validation_dict]
        
        if any(failed_tests) and self.strict == True:
            return validation_dict
        
        if self.is_dict == True:
            validation_dict["data_check"] = {}
            for k in data_structure:
                validation_dict["data_check"][k] = self.structures[k].validate(
                    data_structure[k])
        
        else:
            validation_dict["data_check"] = {}
            for element in data_structure:
                validation_dict["data_check"].append(
                    self.structures[k].validate(element))
            validation_dict["data_check"] = type(self.structures)(
                validation_dict["data_check"])
        
        return validation_dict

def pprint(validation_dict: DataModelOutput):
    """Provides a nicer way to inspect data model outputs.

    Args:
        validation_dit (DataModelOutput): _description_
    """
    def color_val(val: bool):
        if val == True:
            return colored(val, "green")
        else:
            return colored(val, "red")

    for key in validation_dict:
        val = validation_dict[key]
        if isinstance(val,dict):
            print("{}:".format(key))
            for sub_key in validation_dict[key]:
                sub_val = validation_dict[key][sub_key]
                print(" - {}: {}".format(sub_key,color_val(sub_val)))
        else:
            print("{}: {}".format(key,color_val(val)))