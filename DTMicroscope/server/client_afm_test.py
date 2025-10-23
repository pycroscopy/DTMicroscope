
import Pyro5.api


if __name__== "__main__":
    uri = "PYRO:microscope.server@localhost:9091"
    mic_server = Pyro5.api.Proxy(uri)
    mic_server.initialize_microscope("AFM", data_path = r"../test/datasets/dset_spm1.h5")
    mic_server.setup_microscope(data_source = 'Compound_Dataset_1')#upload dataset?
    mic_server.get_dataset_info()
    
    


    