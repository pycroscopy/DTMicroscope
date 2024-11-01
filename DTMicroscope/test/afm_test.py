import unittest
import numpy as np
from DTMicroscope.base.microscope import BaseMicroscope  # Assuming the base class is already implemented
from SciFiReaders import NSIDReader
from  DTMicroscope.base.afm import AFM_Microscope

line3_ph = np.array([123.34255981445312,
 122.10791015625,
 133.32247924804688,
 130.43826293945312,
 125.31623840332031,
 108.81644439697266,
 78.21248626708984,
 -4.370241165161133,
 20.95421028137207,
 76.33377838134766,
 46.400306701660156,
 127.32804870605469,
 129.2752227783203,
 134.39981079101562,
 130.99310302734375,
 133.9613800048828,
 122.14908599853516,
 127.47921752929688,
 128.55990600585938,
 130.01792907714844,
 127.25704193115234,
 128.34339904785156,
 131.3284454345703,
 127.8362045288086,
 132.04078674316406,
 121.31623077392578,
 130.38595581054688,
 123.7817153930664,
 129.32781982421875,
 132.73358154296875,
 129.8618927001953,
 131.8264923095703,
 122.63969421386719,
 128.13504028320312,
 136.00375366210938,
 134.32879638671875,
 134.6331329345703,
 131.2651824951172,
 130.87371826171875,
 129.71031188964844,
 130.8373565673828,
 127.67769622802734,
 127.14580535888672,
 119.92971801757812,
 126.35240936279297,
 124.21472930908203,
 131.801025390625,
 83.6107177734375,
 51.2043342590332,
 104.67825317382812,
 121.03378295898438,
 133.5195770263672,
 137.7744140625,
 127.23084259033203,
 135.69442749023438,
 109.52317810058594,
 41.82383728027344,
 -57.76834487915039,
 -25.465299606323242,
 262.770263671875,
 -25.17596435546875,
 -30.883255004882812,
 -20.184051513671875,
 -29.9472713470459,
 7.938072681427002,
 88.44839477539062,
 108.72044372558594,
 117.66561126708984,
 120.39826965332031,
 138.48953247070312,
 144.3465118408203,
 118.75675964355469,
 135.1234893798828,
 135.22479248046875,
 142.81809997558594,
 138.57736206054688,
 138.99020385742188,
 133.50706481933594,
 134.47409057617188,
 132.78074645996094,
 134.38192749023438,
 133.5863494873047,
 132.96112060546875,
 137.53933715820312,
 138.2801971435547,
 126.71375274658203,
 138.89102172851562,
 141.96502685546875,
 137.7485809326172,
 127.56150817871094,
 129.30801391601562,
 129.75961303710938,
 129.3818817138672,
 129.8499298095703,
 136.89561462402344,
 124.47149658203125,
 130.24440002441406,
 129.47979736328125,
 133.62295532226562,
 135.93099975585938,
 134.13995361328125,
 130.7757568359375,
 120.79013061523438,
 99.06024169921875,
 66.17826843261719,
 133.7450714111328,
 122.23259735107422,
 113.9019775390625,
 128.21035766601562,
 105.80747985839844,
 136.73886108398438,
 134.47821044921875,
 145.87460327148438,
 141.7366943359375,
 138.45460510253906,
 135.3292236328125,
 140.06031799316406,
 137.3602752685547,
 139.651123046875,
 135.50088500976562,
 134.90586853027344,
 137.6546173095703,
 140.41932678222656,
 139.5673065185547,
 138.504638671875,
 140.1568145751953,
 134.25852966308594,
 132.27041625976562,
 131.7182159423828,
 136.25582885742188,
 139.16709899902344,
 141.1025390625,
 143.28030395507812,
 141.04336547851562,
 141.11167907714844,
 140.3524169921875,
 139.52442932128906,
 138.15208435058594,
 138.62890625,
 139.6957550048828,
 140.568359375,
 141.9024658203125,
 139.32395935058594,
 138.9962158203125,
 139.66046142578125,
 137.57138061523438,
 138.93267822265625,
 139.06553649902344,
 138.61349487304688,
 140.67672729492188,
 138.2957000732422,
 141.03956604003906,
 139.2021484375,
 140.04083251953125,
 139.8758544921875,
 142.22682189941406,
 143.00311279296875,
 142.84397888183594,
 140.6061553955078,
 142.20460510253906,
 135.4689178466797,
 -0.5861163139343262,
 -50.20473098754883,
 -43.314369201660156,
 -39.85655212402344,
 -46.22553253173828,
 -39.29964065551758,
 -40.6684455871582,
 -41.15817642211914,
 -41.57318878173828,
 -39.94390869140625,
 -37.673255920410156,
 -40.750823974609375,
 -41.93741226196289,
 -42.97772216796875,
 -43.84722900390625,
 -44.41682434082031,
 -42.749603271484375,
 -43.61915588378906,
 -43.53081512451172,
 -41.32977294921875,
 -41.705989837646484,
 -38.86102294921875,
 -41.50654220581055,
 -41.02728271484375,
 -43.14088439941406,
 -42.0030517578125,
 -45.602210998535156,
 -46.805641174316406,
 -46.90151596069336,
 -47.33455276489258,
 -46.891387939453125,
 -47.191837310791016,
 -50.8460578918457,
 -53.535430908203125,
 -52.394527435302734,
 -47.470977783203125,
 -45.829811096191406,
 -48.50856399536133,
 -48.88615417480469,
 -47.81865692138672,
 -49.89114761352539,
 -45.709564208984375,
 -44.192138671875,
 -47.180057525634766,
 -43.928768157958984,
 -42.91154479980469,
 -43.9992790222168,
 -46.595848083496094,
 -46.349578857421875,
 -44.09819793701172,
 -45.25212860107422,
 -45.40621566772461,
 -45.8501091003418,
 -45.05611038208008,
 -46.76697540283203,
 -45.10070037841797,
 -43.208885192871094,
 -44.646827697753906,
 -43.68178939819336,
 -46.04923629760742,
 -48.192474365234375,
 -45.280731201171875,
 -47.30607604980469,
 -46.43729782104492,
 -45.50105667114258,
 -48.00909423828125,
 -46.75545120239258,
 -48.0703125,
 -53.58605194091797,
 -0.13102054595947266,
 46.65485763549805,
 96.70652770996094,
 141.10379028320312,
 144.14768981933594,
 141.40159606933594,
 136.836669921875,
 130.4855194091797,
 33.549434661865234,
 -18.393474578857422,
 -16.96117401123047,
 -33.23447799682617,
 -40.888580322265625,
 -33.82117462158203,
 -36.055240631103516,
 -28.181411743164062,
 -38.10243225097656,
 -30.301151275634766,
 -21.667163848876953,
 -19.937589645385742,
 -18.900047302246094,
 -28.02667999267578,
 -56.40511703491211,
 -55.98585510253906,
 -78.67002868652344,
 38.925655364990234])

data_path = r'datasets/dset_spm1.h5'
class TestAFM_Microscope(unittest.TestCase):

    def setUp(self):
        """Initialize the AFM_Microscope instance before each test."""
        self.afm = AFM_Microscope(data_path = data_path)
        self.afm.setup_microscope(data_source='Compound_Dataset_1', dset_subset='image_dataset_0')

#         # Creating dummy coordinates for the test
#         self.afm.x_coords = np.linspace(0, 1, 100)
#         self.afm.y_coords = np.linspace(0, 1, 100)
#
#         # Creating a dummy dataset with simple values for testing purposes
#         self.afm.dataset = {
#             "image_channel": sd.Dataset.from_array(np.random.rand(100, 100), name="test_image")
#         }
#
#         # Assume self.dataset setup with proper sidpy dataset object and data types
#         self.afm._im_ind = {"image_channel": 0}
#         self.afm.scan_ar = np.random.rand(1, 100, 100)
#
    def test_go_to_within_range(self):
        """Test moving the probe to a valid (x, y) location within the range."""
        self.afm.go_to(1e-6, 0.5e-6)
        self.assertEqual(self.afm.x, 1e-6)
        self.assertEqual(self.afm.y, 0.5e-6)
#
    def test_go_to_out_of_range(self):
        """Test clamping of coordinates when moved out of range."""
        self.afm.go_to(2.0, -2.0)
        self.assertEqual(self.afm.x, 2.5e-6)  # Should be clamped to the max value
        self.assertEqual(self.afm.y, -2.5e-6)  # Should be clamped to the max value

    def test_scanning_emulator(self):
        """Test the scanning emulator with horizontal scanning."""
        slices = list(self.afm.scanning_emulator(direction='horizontal'))
        self.assertEqual(len(slices), 256)  # Expecting 100 slices for the 100x100 grid
        self.assertEqual(len(slices[0]), 7)
        self.assertTrue(np.array_equal(slices[2][5], line3_ph))
#
    def test_scan_individual_line(self):
        """Test scanning a specific line in the dataset."""
        line_data = self.afm.scan_individual_line(direction='horizontal', coord=-10e-6)
        self.assertTrue(np.array_equal(self.afm.scan_ar[:,0], line_data))

    def test_find_closest_point(self):
        """Test finding the closest point in coordinates."""
        coords = np.array([[0, 0], [0.5, 0.5], [1, 1]])
        target_point = (0.4, 0.4)
        closest_index = self.afm._find_closest_point(coords, target_point)
        self.assertEqual(closest_index, 1)
#
    def test_real_to_pixel(self):
        """Test converting real-world coordinates to pixel coordinates."""
        coord_ar = np.array([[0.5e-6, 0.5e-6], [0.2e-6, 0.2e-6]])
        pixel_coords = self.afm._real_to_pixel(coord_ar)
        self.assertEqual(pixel_coords.shape, (2, 2))
#
    def test_get_scan(self):
        """Test retrieving the scan data."""
        scan_data = self.afm.get_scan(['HeightRetrace',])
        self.assertEqual(scan_data.shape, (1, 256, 256))
        scan_data = self.afm.get_scan(['HeightRetrace', 'ddd'])
        self.assertEqual(scan_data.shape, (1, 256, 256))
        scan_data = self.afm.get_scan(['HeightRetrace', 'Channel_0'])
        self.assertEqual(scan_data.shape, (2, 256, 256))
#
#     def test_get_spectrum(self):
#         """Test retrieving spectrum data at a specific location."""
#         spectrum, data = self.afm.get_spectrum(location=(0.5, 0.5), channel=None)
#         self.assertIsNotNone(spectrum)
#         self.assertIsNotNone(data)
#
#     def test_process_dataset(self):
#         """Test if dataset processing correctly identifies image indices and extracts scan array."""
#         self.afm.process_dataset(self.afm.dataset)
#         self.assertIn("image_channel", self.afm._im_ind)
#         self.assertIsInstance(self.afm.scan_ar, np.ndarray)
#
if __name__ == '__main__':
    unittest.main()
#
