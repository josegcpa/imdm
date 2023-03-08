from ..mri_specific_structures import DicomFile,SitkFile

test_dcm_path = "test_data/MRBRAIN.dcm"
test_sitk_path = "test_data/CT_Philips.nii.gz"

def test_dicom_data_validator():
    data_validator = DicomFile(shape=(512,512),range=None)
    
    output = data_validator.validate(test_dcm_path)
    assert output["type"] == True
    assert output["shape"] == True

    data_validator = DicomFile(shape=(256,512),range=None)
    
    output = data_validator.validate(test_dcm_path)
    assert output["type"] == True
    assert output["shape"] == False

def test_sitk_data_validator():
    data_validator = SitkFile(shape=(256, 232, 185),range=[-1000,None])
    
    output = data_validator.validate(test_sitk_path)
    assert output["type"] == True
    assert output["shape"] == True
    assert output["range"] == False
