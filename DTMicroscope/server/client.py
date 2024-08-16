
import matplotlib.pylab as plt
import numpy as np
import Pyro5.api


if __name__== "__main__":
    uri = "PYRO:microscope.server@0.0.0.0:9091"
    mic_server = Pyro5.api.Proxy(uri)
    mic_server.activate_microscope("dummy")
    array_list, shape, dtype = mic_server.get_overview_image((128,128))
    im_array = np.array(array_list, dtype=dtype).reshape(shape)
    plt.imshow(im_array)
    plt.show()
    
