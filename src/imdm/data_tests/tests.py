"""
Contains generic and speicifc testing functions for data validators.
"""

__author__ = "José Guilherme de Almeida"
__version__ = "0.1.0"
__license__ = "MIT"
__email__ = "jose.gcp.almeida@gmail.com"

import numpy as np
from abc import ABC
from dataclasses import dataclass
from typing import Any,Sequence,Tuple,Union

@dataclass
class Test(ABC):
    target: Any=None
    
    def __post_init__(self):
        self._success_msg = ""
        self._fail_msg = ""

    def get_name(self):
        try:
            name = str(self.target.__name__)
        except:
            name = str(self)
        return name

    def unpack(self, x: Any):
        return x
    
    def compare(self, unpacked_x: Any) -> bool:
        return unpacked_x == self.target
    
    def __call__(self, x: Any) -> bool:
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
class TestType(Test):
    target: Any
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target type {name} is equal to input type"
        self._fail_msg = f"Target type {name} is not equal to input type"

    def unpack(self, x: Any) -> Any:
        return type(x)
        
@dataclass
class TestLength(Test):
    target: int
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target length {name} is equal to input length"
        self._fail_msg = f"Target length {name} is not equal to input length"

    def check_target(self):
        error_msg = "Input to {} should be {}".format(self.get_name(),"int")
        if self.target is not None:
            if isinstance(self.target,int) is False:
                raise ValueError(error_msg)
            
    def unpack(self, x: Any) -> Any:
        return len(x)

@dataclass
class TestDType(Test):
    target: Any
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target dtype {name} is equal to input dtype"
        self._fail_msg = f"Target dtype {name} is not equal to input dtype"
        
    def unpack(self, x: Any) -> Any:
        return x.dtype

@dataclass
class TestShape(Test):
    target: Sequence[int]
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target shape {name} is equal to input shape"
        self._fail_msg = f"Target shape {name} is not equal to input shape"
    
    def check_target(self):
        error_msg = "Input to {} should be {}".format(
            self.get_name(),"Sequence[int]")
        types = (tuple,list)
        if self.target is not None:
            if isinstance(self.target,types) is False:
                raise ValueError(error_msg)
            elif all([isinstance(x,int) for x in self.target]) == False:
                raise ValueError(error_msg)

    def unpack(self, x: Any) -> Any:
        return x.shape

@dataclass
class TestRange(Test):
    target: Tuple[Union[int,float],Union[int,float]]
    
    def __post_init__(self):
        if hasattr(self,"check_target"):
            self.check_target()
        name = self.get_name()
        self._success_msg = f"Target shape {name} contains input values"
        self._fail_msg = f"Target shape {name} does not contain input values"

    def check_target(self):
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
        return np.min(x),np.max(x)

    def compare(self, unpacked_x: Any) -> Any:
        within_range = True
        if self.target[0] is not None:
            if unpacked_x[0] < self.target[0]:
                within_range = False
        if self.target[1] is not None:
            if unpacked_x[1] > self.target[1]:
                within_range = False
        return within_range
