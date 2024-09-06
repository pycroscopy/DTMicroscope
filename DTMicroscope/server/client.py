
import matplotlib.pylab as plt
import numpy as np
import Pyro5.api


if __name__== "__main__":
    uri = "PYRO:microscope.server@localhost:9091"
    mic_server = Pyro5.api.Proxy(uri)
    mic_server.activate_microscope("STEM")
    mic_server.setup_microscope()
    array_list, shape, dtype = mic_server.get_overview_image()
    im_array = np.array(array_list, dtype=dtype).reshape(shape)
    plt.imshow(im_array)
    plt.axis("off")
    plt.title("Overview Image")
    plt.show()
    plt.close()
    array_list, shape, dtype= mic_server.get_point_data(1, 1, 1)
    spec_at_111 = np.array(array_list, dtype=dtype).reshape(shape)
    
    # plot two subigure, overview image witha mark where the spectrum is taken and then on side spectrum plot
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    ax[0].imshow(im_array)
    ax[0].axis("off")
    ax[0].set_title("Overview Image")
    ax[0].plot(1, 1, 'ro')
    ax[1].plot(spec_at_111)
    ax[1].set_title("Spectrum at x=1 and y=1")
    ax[1].set_xlabel('Energy (eV)')
    ax[1].set_ylabel('Intensity (a.u.)')
    plt.show()
    
    
