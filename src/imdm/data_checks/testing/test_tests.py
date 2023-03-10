import numpy as np

from ..checkers import (
    CheckDType,CheckLength,
    CheckRange,CheckShape,CheckType)

def test_check_dtype():
    test = CheckDType(np.int32)
    assert test(np.ones(1,dtype=np.int32)) == True
    assert test(np.ones(1,dtype=np.float32)) == False
    
def test_check_type():
    test = CheckType(int)
    assert test(1) == True
    assert test(1.0) == False
    
def test_check_length():
    test = CheckLength(10)
    assert test([1 for _ in range(10)]) == True
    assert test([1 for _ in range(11)]) == False
    
def test_check_shape():
    test = CheckShape([10,10])
    
    assert test(np.ones([10,10])) == True
    assert test(np.ones([10])) == False

def test_check_range():
    test = CheckRange([-10,10])
    
    assert test(-5) == True
    assert test(np.random.uniform(0,1,size=[100])) == True
    assert test(np.ones([10])*100) == False
