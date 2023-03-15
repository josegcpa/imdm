#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Contains generic and specific checking functions for data validators.
"""

import numpy as np
from abc import ABC
from dataclasses import dataclass,field
from typing import Any,Sequence,Tuple,Union,Dict

@dataclass
class Check(ABC):
    """
    Abstract check class. The Check class structure can be defined as follows:
    
    - A ``target`` should be the only input. This variable is the value against
        which the input data will be compared;
    - An ``unpack`` method will be used to convert the input data to the same
        domain as ``target``. For example, if a type check is setup, ``unpack``
        should return ``type(input_data)``. Be default this returns the input
        data
    - A ``compare`` method will be used to compare the unpacked data with 
        ``target``. By default this returns whether the unpacked data is 
        the same as ``target`` (equality).
    
    To implement custom checks, the ``unpack`` and ``compare`` methods should
    be redefined.
    
    Two additional class constants - ``_success_msg`` and ``_fail_msg`` - are
    also defined by default (as ""). These messages are helpful if verbosity is
    an important part of theses checks. If the check succeeds, ``_success_msg`` 
    will be stored as ``self.msg``; otherwise, ``_fail_msg`` will be selected.
    
    We also recommend the definition of a ``check_target`` method that can be
    used to check whether the target variable is correct.
    
    Args:
        target (Any): the value against which the data will be compared.
    """
    target: Any=None
    msg: str=field(default="Check has not been run",init=False)
    _success_msg: str=field(default="",init=False,repr=False)
    _fail_msg: str=field(default="",init=False,repr=False)
    
    def check_target(self):
        pass
    
    def get_name(self) -> str:
        """Returns the name of the class.

        Returns:
            str: name of the class.
        """
        try:
            name = str(self.target.__name__)
        except:
            name = str(self)
        return name

    def unpack(self, x: Any) -> Any:
        """Unpacks the input data.

        Args:
            x (Any): input data.

        Returns:
            Any: unpacked data.
        """
        return x
    
    def compare(self, unpacked_x: Any) -> bool:
        """Performs the check comparison using the unpacked data.

        Args:
            unpacked_x (Any): unpacked data.

        Returns:
            bool: whether the comparison was successful or not.
        """
        return unpacked_x == self.target
    
    def __call__(self, x: Any) -> bool:
        """Performs the comparison using the input data and defines the 
        ``self.msg``.

        Args:
            x (Any): input data.

        Returns:
            bool: whether the comparison was successful or not.
        """
        if self.target is None:
            return self.target
        unpacked_x = self.unpack(x)
        result = self.compare(unpacked_x)
        if result == True:
            self.msg = self._success_msg
        if result == False:
            self.msg = self._fail_msg
        return result

@dataclass
class CheckType(Check):
    """Checks whether the input data type is the same as ``target``.

    Args:
        target (Any): target type.
    """
    target: Any
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target type {name} is equal to input type"
        self._fail_msg = f"Target type {name} is not equal to input type"

    def unpack(self, x: Any) -> Any:
        """Returns the type of the input data.

        Args:
            x (Any): input data.

        Returns:
            Any: input data type.
        """
        return type(x)
        
@dataclass
class CheckLength(Check):
    """Checks whether the input data length is the same as ``target``.

    Args:
        target (int): target length.
    """
    target: int
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target length {name} is equal to input length"
        self._fail_msg = f"Target length {name} is not equal to input length"

    def check_target(self):
        """Checks whether the target has been correctly defined.

        Raises:
            ValueError: raises an error if the self.target is not an int.
        """
        error_msg = "Input to {} should be {}".format(self.get_name(),"int")
        if self.target is not None:
            if isinstance(self.target,int) is False:
                raise ValueError(error_msg)
            
    def unpack(self, x: Any) -> int:
        """Returns the length of the input data.

        Args:
            x (Any): input data.

        Returns:
            int: length of the input data.
        """
        return len(x)

@dataclass
class CheckDType(Check):
    """Checks whether the input data dtype is the same as ``target``.

    Args:
        target (int): target dtype.
    """
    target: Any
    
    def __post_init__(self):
        name = self.get_name()
        self._success_msg = f"Target dtype {name} is equal to input dtype"
        self._fail_msg = f"Target dtype {name} is not equal to input dtype"
        
    def unpack(self, x: Any) -> Any:
        """Returns the input data data type.

        Args:
            x (Any): input data.

        Returns:
            Any: input data data type.
        """
        return x.dtype

@dataclass
class CheckShape(Check):
    """Checks whether the input data shape is the same as ``target``.

    Args:
        target (int): target shape.
    """
    target: Sequence[int]
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target shape {name} is equal to input shape"
        self._fail_msg = f"Target shape {name} is not equal to input shape"
    
    def check_target(self):
        """Checks whether the target has been correctly defined.

        Raises:
            ValueError: raises an error if the ``self.target`` is not a 
            sequence (tuple or list) of integers.
        """
        error_msg = "Input to {} should be {}".format(
            self.get_name(),"Sequence[int]")
        types = (tuple,list)
        if self.target is not None:
            if isinstance(self.target,types) is False:
                raise ValueError(error_msg)
            elif all([isinstance(x,int) for x in self.target]) == False:
                raise ValueError(error_msg)

    def unpack(self, x: Any) -> Sequence[int]:
        """Returns the shape of the data (using the ``x.shape`` attribute).

        Args:
            x (Any): input data.

        Returns:
            Sequence[int]: input data shape.
        """
        sh = x.shape
        try:
            sh = type(self.target)(sh)
        except Exception:
            pass
        return sh

@dataclass
class CheckRange(Check):
    """Checks whether the input data values are contained within ``target``.

    Args:
        target (Tuple[Union[int,float],Union[int,float]]): two integer or float
            values, used as the maximum and minimum of the range. If these 
            values are ``None``, then it is assumed that there is no bound.
    """
    target: Tuple[Union[int,float],Union[int,float]]
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target shape {name} contains input values"
        self._fail_msg = f"Target shape {name} does not contain input values"

    def check_target(self):
        """Checks whether the target has been correctly defined.

        Raises:
            ValueError: raises and error if ``self.target`` is not a sequence
                of two numbers or ``None``.
        """
        error_message = "Input to {} should be {}".format(
                self.get_name(),"a sequence of two numbers/None")
        types = (tuple,list,np.ndarray)
        if self.target is not None:
            if isinstance(self.target,types) is False:
                raise ValueError(error_message)
            elif len(self.target) != 2:
                raise ValueError(error_message)
            elif all([isinstance(x,(int,float)) or x == None
                    for x in self.target]) == False:
                raise ValueError(error_message)

    def unpack(self, x: Any) -> Any:
        """Returns the minimum and maximum of ``x``.

        Args:
            x (Any): input data.

        Returns:
            Any: input data minimum and maximum.
        """
        return float(np.min(x)),float(np.max(x))

    def compare(self, unpacked_x: Tuple[float,float]) -> bool:
        """Checks whether ``unpacked_x`` is within the values specified in
        ``target``.

        Args:
            unpacked_x (Any): minimum and maximum value of ``x``.

        Returns:
            bool: True if the minimum of ``x`` is larger than 
                ``self.target[0]`` (if defined) and the maximum of ``x`` is 
                smaller than ``self.target[1]`` (if defined). False otherwise.
        """
        within_range = True
        if self.target[0] is not None:
            if unpacked_x[0] < self.target[0]:
                within_range = False
        if self.target[1] is not None:
            if unpacked_x[1] > self.target[1]:
                within_range = False
        return within_range

@dataclass
class CheckDICOMMetadata(Check):
    """Checks whether a set of metadata tags is equal to specific values.

    Args:
        target (Dict[str,Any]): dictionary with key-value metadata pairs. Each
            key should be either a tuple with two strings corresponding to 
            an hex-encoded integer (i.e. ``("0020","000D")``), an integer or a
            string corresponding to an attribute in a ``pydicom`` dataset.
    """
    target: Dict[str,Any]
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target shape {name} contains input values"
        self._fail_msg = f"Target shape {name} does not contain input values"

    def check_target(self):
        """Checks whether the target has been correctly defined.

        Raises:
            ValueError: raises an error if the input is not a DICOM metadata
                dictionary with key-value pairs.
        """
        error_message = "Input to {} should be {}".format(
                self.get_name(),"a dictionary of metadata key-value pairs")
        error_message += "\n"
        error_message += "The input should have one of the following formats:"
        error_message += "\n\t - {('0020','000D'):'value'}"
        error_message += "\n\t - {2097165:'value'}"
        error_message += "\n\t - {('StudyUID'):'value'}"
        if self.target is not None:
            if isinstance(self.target,dict) is False:
                raise ValueError(error_message)
            for k in self.target:
                if isinstance(self.target[k],tuple):
                    if isinstance(self.target[k][0],str) == False:
                        raise ValueError(error_message)
                elif isinstance(self.target[k],(str,int)) == False:
                    raise ValueError(error_message)

    def unpack(self, x: Any) -> Dict[str,Any]:
        """Returns the relevante values for the metadata key-value comparison.

        Args:
            x (Any): input data.

        Returns:
            Dict[str,Any]: dictionary containing the metadata values to be 
                compared against the ``target`` specified in the constructor.
        """
        comparison_dict = {key:None for key in self.target}
        for key in self.target:
            if isinstance(key,tuple):
                key_ = int("0x" + self.target[0] + self.target[1],16)
                if key_ in x:
                    value = x[key_].value
                    if isinstance(self.target[key],str):
                        value = str(value)
                    comparison_dict[key] = value
            elif isinstance(key,str):
                if hasattr(x,key):
                    value = getattr(x,key).value
                    if isinstance(self.target[key],str):
                        value = str(value)
                    comparison_dict[key] = value
        return comparison_dict

    def compare(self, unpacked_x: Any) -> bool:
        """Checks whether the values in ``unpacked_x`` are equal to those in
        ``target``.

        Args:
            unpacked_x (Any): dictionary with key-value pairs.

        Returns:
            bool: True if all values in ``unpacked_x`` are identical to those 
                in ``target``. False otherwise.
        """
        all_val_identical = True
        for key in self.target:
            if unpacked_x[key] is None:
                all_val_identical = False
            else:
                if unpacked_x[key] != self.target[key]:
                    all_val_identical = False
        return all_val_identical
