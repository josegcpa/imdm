from ..generic_models import DataValidator,DataModel

def test_data_validator():
    data_validator = DataValidator(type=str,length=4,shape=None,range=None)
    
    output = data_validator.validate("my_test_string")
    assert output["type"] == True
    assert output["length"] == False
    
def test_data_model():
    data_model = DataModel(
        {"a": DataValidator(type=str),
         "b": DataValidator(type=int,range=[-10,None])},)
    
    input_data = {"a":"equis","b":-11}
    output = data_model.validate(input_data)
    
    assert output["structure_type"] == True
    assert output["structure_length"] == True
    assert output["structure_keys"] == True
    assert output["data_check"]["a"]["type"] == True
    assert output["data_check"]["b"]["type"] == True
    assert output["data_check"]["b"]["range"] == False
