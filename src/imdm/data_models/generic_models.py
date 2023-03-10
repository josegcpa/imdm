#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generic data types and classes used to construct data models to be used in data
validation.
"""

import logging
import numpy as np
from termcolor import colored
from ..data_checks import (
    CheckType,CheckLength,CheckShape,CheckRange,CheckDType)

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
    
    To add and remove checks, the functions ``self.add_check`` and 
    ``self.remove_check`` should be used to ensure that everything works. The 
    ``preprocess_fn`` and ``values_fn`` arguments can be used to preprocess the
    data before other checks and to obtain values from the data, respectively.
    To make sure that checks are applied to the correct stages of the data (
    "raw", "preprocessed_data" and "values"), checks should be annotated with
    this when being added with the function ``self.add_check``: for instance, if
    a check ``check_something`` is to be applied to the preprocessed input, then to
    add this check one should run 
    ``self.add_check("key",check_something,"preprocessed")``. The value extraction
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
        self._check_dict = {
            "raw":{},
            "preprocessed_data":{
                "type": CheckType(self.type)
            },
            "values":{
                "length": CheckLength(self.length),
                "shape": CheckShape(self.shape),
                "range": CheckRange(self.range),
                "dtype": CheckDType(self.dtype)
            },
        }

        self.check_names = ["type","length","shape","range","dtype"]
        self.logger = logging.getLogger('data_validator')
        self.logger.setLevel(self.verbose)
    
    @property
    def check_dict(self) -> Dict[str,Tuple[Callable,str]]:
        """Returns the check dictionary.

        Returns:
            Dict[str,Tuple[Callable,str]]: dictionary with checks and their
                respective data stages.
        """
        return self._check_dict
    
    def __len__(self) -> int:
        """Returns the number of checks.

        Returns:
            int: number of checks.
        """
        return len(self._check_dict)
    
    def __setattr__(self, attr: str, value: Any):
        """Overrinding the default __setattr__ method to prevent direct 
        definition of ``check_dict``.

        Args:
            attr (str): attribute name.
            value (Any): attribute value.

        Raises:
            ValueError: raises an error if attr == "check_dict".
        """
        if attr == "check_dict":
            raise ValueError("check_dict cannot be altered. Please use the \
                add_check and remove_check methods")
        else:
            super().__setattr__(attr, value)

    def add_check(self, key: str, check_fn: Callable, data_stage: str):
        """Adds a check to the check dictionary.

        Args:
            key (str): name of the dictionary.
            check_fn (Callable): function corresponding to the check. Must return
                a boolean (True or False).
            data_stage (str): data stage for the application of this check.
        """
        if key in self.check_names:
            raise ValueError(f"'{key}' check is already defined")
        self._check_dict[data_stage][key] = (check_fn)
    
    def remove_check(self, key: str, data_stage: str=None):
        """Removes a check.

        Args:
            key (str): key of the check to be removed.
            data_stage (str, optional): data stage at which the check is 
                performed. Defaults to None (removes any instances of key).
        """
        if data_stage is not None:
            del self._check_dict[data_stage][key]
        else:
            for data_stage in self._check_dict:
                if key in self.check_dict[data_stage]:
                    del self.check_dict[data_stage][key]
        if key in self.check_names:
            self.check_names.remove(key)
    
    def validate(self, 
                 data: Any, 
                 strict: bool=True) -> Dict[str,Union[bool,None]]:
        """Runs all of the checks in check_dict on the input data. Checks are 
        performed sequentially by data stages and execution halts if a check
        in the previous stage fails. To avoid this behaviour, set ``strict``
        to ``True``.

        Args:
            data (Any): input data.
            strict (bool, optional): requires that checks at a previous stage
                succeed (no ``False`` values) to execute the next stages. 
                Defaults to ``True``.

        Returns:
            Dict[str,Union[bool,None]]: a dictionary where the keys are the 
                same as those in ``check_dict`` and the values are the result of
                the checks.
        """
        stop = False
        validation_dict = {k:None for k in self.check_names}
        for k in self.check_dict["raw"]:
            result = self.check_dict["raw"][k](data)
            if result == False:
                stop = True
            validation_dict[k] = result
        
        if (stop is False) or (strict is False):
            if self.preprocess_fn is not None:
                data = self.preprocess_fn(data)
                print(len(data))
            for k in self.check_dict["preprocessed_data"]:
                result = self.check_dict["preprocessed_data"][k](data)
                if result == False:
                    stop = True
                validation_dict[k] = result

        if (stop is False) or (strict is False):
            if self.values_fn is not None:
                data = self.values_fn(data)
            for k in self.check_dict["values"]:
                result = self.check_dict["values"][k](data)
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
        
        failed_checks = [validation_dict[k] == False for k in validation_dict]
        
        if any(failed_checks) and self.strict == True:
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
