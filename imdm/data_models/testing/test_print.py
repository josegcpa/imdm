from ..generic_models import pprint

def test_print():
    pprint({"a":True,"b":False,
            "c":{"1":False,"2":True},
            "f":False})
    
test_print()