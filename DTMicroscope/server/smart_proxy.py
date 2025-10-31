""" First server"""

import sys
import os
import time

import json
import socket

import numpy as np
import Pyro5.api



sys.path.insert(0, "C:\\AE_future\\autoscript_1_14\\")
import autoscript_tem_microscope_client as auto_script

os.environ["PYRO_LOGLEVEL"] = "DEBUG"

# integrate inside TEMServer?
class CEOSacquisitionTCP:
    def __init__(self, host="127.0.0.1", port=7072):
        self.host = host
        self.port = port
        self._next_id = 1

    def _send_recv(self, message: dict) -> dict:
        # Convert to JSON and encode in UTF-8
        json_msg = json.dumps(message, separators=(",", ":"))  # no spaces
        payload = json_msg.encode("utf-8")
        netstring = f"{len(payload)}:".encode("ascii") + payload + b","

        with socket.create_connection((self.host, self.port), timeout=3000) as sock:  # 5 minutes
            sock.sendall(netstring)

            # Read until we hit a complete netstring (ends with b",")
            buffer = b""
            while not buffer.endswith(b","):
                chunk = sock.recv(4096)
                if not chunk:
                    break  # Server closed connection
                buffer += chunk

        # Parse netstring: "length:payload,"
        try:
            length_str, rest = buffer.split(b":", 1)
            length = int(length_str)
            payload = rest[:length]
            return json.loads(payload.decode("utf-8"))
        except Exception as e:
            print("Malformed netstring or response:", buffer)
            raise e

    def _run_rpc(self, method: str, params: dict = None):
        if params is None:
            params = {}
        msg = {
            "jsonrpc": "2.0",
            "id": self._next_id,
            "method": method,
            "params": params,
        }
        self._next_id += 1
        reply = self._send_recv(msg)
        if "error" in reply:
            raise RuntimeError(f"RPC Error: {reply['error']}")
        return reply.get("result", {})

    def run_tableau(self, tab_type="Standard", angle=18):
        return self._run_rpc("acquireTableau", {"tabType": tab_type, "angle": angle})

    def correct_aberration(self, name: str, value=None, target=None, select=None):
        params = {"name": name}
        if value:
            params["value"] = list(value)
        if target:
            params["target"] = list(target)
        if select:
            params["select"] = select
        return self._run_rpc("correctAberration", params)

    def measure_c1a1(self):
        return self._run_rpc("measureC1A1", {})


def default_flu_camera(detector_dict):
    detector_dict['flu_camera'] = {'size': 512,
                                   'exposure': 0.1,
                                   'binning': 1,
                                   'save_to_disc': False}

def default_ceta_camera(detector_dict):
    detector_dict['ceta_camera'] = {'data': np.zeros((512, 512), dtype=np.uint16),
                                    'size': 512,
                                    'exposure': 0.1,
                                    'binning': 1,}
def default_scan(detector_dict):
    detector_dict['scan'] = {'data': np.zeros((512, 512), dtype=np.uint16),
                                    'size': 512,
                                    'exposure': 4e-6,
                                    'field_of_view': (1e-6, 1e-6),
                                    'detectors': ['HAADF'],
                                    'camera_length': 91e-3,}
def default_eds(detector_dict):
    detector_dict['super_x'] = {'data': np.zeros(2048, dtype=np.uint16),
                                'size': 2048,
                                'exposure': 0.1,
                                'binning': 2,
                                'energy_window': (0, 20000),}

default_haadf_detector = {'detector_type': 'HAADF',
                          'collection_angle_inner': 50e-3,
                          'collection_angle_outer': 200e-3,}


def serialize(array):
    array_list = array.tolist()
    dtype = str(array.dtype)
    return array_list, array.shape,  dtype

class MicroscopeServer(object):
    """Class to handle the array server"""
    def __init__(self):
        print('init')
        self.detectors  = {}
        self.log = {time.time(): "Server started"}

        self.microscope = None
        self.available_parameters = []

    @Pyro5.api.expose
    def microscope_command(self, comand):
        """Send a command to the microscope"""
        print(f"Sending command to microscope: {comand}")
        return 1

    @Pyro5.api.expose
    def align_microscope(self, device, order, **args):
        """Align the microscope"""
        
        print(f"Aligning microscope with {device} for {order} order")
        return 1

    @Pyro5.api.expose
    def get_detectors(self):
        """Get the list of available detectors"""
        return list(self.detectors.keys())

    @Pyro5.api.expose
    def activate_device(self, device):
        """Activate the specified device for acquisition"""
        if device in self.detectors:
            print(f"{device.capitalize()} activated")
            return 1
        else:
            print(f"Device {device} not found")
            return 0
        
    @Pyro5.api.expose
    def device_settings(self, device, **args):
        """Set the device settings"""
        if device in self.detectors:
            print(f"Setting {device} settings: {args}")
            return 1
        else:
            print(f"Device {device} not found")
            return 0

    @Pyro5.api.expose
    def get_stage(self):
        """Get the current stage position"""
        positions = [0, 0, 0, 0, 0]
        return positions
    
    @Pyro5.api.expose
    def set_stage(self, stage_positions, relative=True):
        """Set the stage position in nm and degrees"""
        stage_move = auto_script.structures.StagePosition()
        for index, direction in enumerate(['x', 'y', 'z', 'a', 'b']):
            pass
        print(f"Moving stage by {stage_move}")

    @Pyro5.api.expose
    def acquire_image(self, device, **args):
        """Acquire an image from the specified device"""
        if device in self.detectors:
            print(f"Acquiring image from {device}")
            image = np.zeros([512,512], dtype=np.uint16)
            return serialize(image)
            
        else:
            print(f"Device {device} not found")
            return None

    @Pyro5.api.expose
    def acquire_image_stack(self, device):
        """Acquire an image from the specified device"""
        if device in self.detectors:
            print(f"Acquiring image from {device}")
            return self.detectors[device]
        else:
            print(f"Device {device} not found")
            return None

    @Pyro5.api.expose
    def acquire_spectrum(self, device, **args):
        """Acquire a spectrum from the specified device"""
        if device in self.detectors:
            print(f"Acquiring spectrum from {device}")
            return np.zeros((2048,), dtype=np.float32)
        else:
            print(f"Device {device} not found")
            return None

    @Pyro5.api.expose
    def acquire_spectrum_points(self, device, points, **args):
        """Acquire a spectrum stack from the specified device"""
        if device in self.detectors:
            print(f"  at point {point}")
        else:
            print(f"Device {device} not found")
            return None
        
    @Pyro5.api.expose
    def set_beam_position(self, x, y):
        """Set the beam position in nm"""
        print(f"Moving beam to ({x}, {y})")
        return 1
    
    @Pyro5.api.expose
    def get_microscope_status(self, parameters=None):
        """Get the current microscope status"""
        for parameter in parameters:
            if parameter in available_parameters:
                if parameter == 'vacuum':
                    return self.get_vacuum()
                elif parameter == 'column_valve':
                    return "Open"
        return "Idle"
    
    def serialize(self, array):
        """Serialize a numpy array to make it transferable via Pyro"""
        array_list = array.tolist()
        dtype = str(array.dtype)
        return array_list, array.shape,  dtype


    @Pyro5.api.expose
    def close(self):
        """Close the server"""
        print("Closing server")
        return 1
    


@Pyro5.api.expose
class TEMServer(MicroscopeServer):
    """Class to handle the array server"""
    def __init__(self):
        super().__init__()

        default_flu_camera(self.detectors)
        self.available_parameters = ['vacuum', 'column_valve', 'stage_position', 'beam_current']

        self.microscope = auto_script.TemMicroscopeClient()
        self.connect_to_as()
        print('initialized')
        self.ab_corrector = None
        
    def connect_to_as(self):
        ip = "127.0.0.1"
        self.microscope.connect(ip, port = 9095)

    def connect_to_ceos(self):
        self.ab_corrector = CEOSacquisitionTCP(host="10.46.217.241", port=9092)

    def measure_c1a1(self):
        return self.ab_corrector.measure_c1a1()

    def correct_aberration(self, name: str, value=None, target=None, select=None):
        return self.ab_corrector.correct_aberration(name=name, value=value, target=target, select=select)

    def run_tableau(self, tab_type="Standard", angle=18):
        return self.ab_corrector.run_tableau(tab_type=tab_type, angle=angle)

    def get_detectors(self):
        """Get the list of available detectors"""
        return list(self.detectors.keys())

    def activate_device(self, device):
        """Activate the specified device for acquisition"""
        if device in self.detectors:
            print(f"{device.capitalize()} activated")
            return 1
        else:
            print(f"Device {device} not found")
            return 0
        
    def device_settings(self, device, **args):
        """Set the device settings"""
        if device in self.detectors:
            print(f"Setting {device} settings: {args}")
            for key, value in args.items():
                if key in self.detectors[device]:
                    self.detectors[device][key] = value
            return 1
        else:
            print(f"Device {device} not found")
            return 0

    def get_stage(self):
        """Get the current stage position"""
        positions = self.microscope.specimen.stage.position
        if self.microscope.specimen.stage.get_holder_type() == "SingleTilt":
            return [float(positions[0]), float(positions[1]), float(positions[2]), float(positions[3]), 0]
        else:
            return [float(positions[0]), float(positions[1]), float(positions[2]), float(positions[3]), float(positions[4])]

    def set_stage(self, stage_positions, relative=True):
        """Set the stage position in nm and degrees"""
        stage_move = auto_script.structures.StagePosition()
        for index, direction in enumerate(['x', 'y', 'z', 'a', 'b']):
            move = stage_positions.get(direction, None)
            setattr(stage_move, direction, move)
        if relative:
            self.microscope.specimen.stage.relative_move_safe(stage_move)
        else:
            self.microscope.specimen.stage.absolute_move_safe(stage_move)
        print(f"Moving stage by {stage_move}")

    def acquire_image(self, device, **args):
        """Acquire an image from the specified device"""
        if device in self.detectors:
            print(f"Acquiring image from {device}")
            if device == 'flu_camera':
                camera = auto_script.enumerations.CameraType.FLUCAM
            device = self.microscope.detectors.get_camera_detector(camera)
            # device.insert()
            image = self.microscope.acquisition.acquire_camera_image(camera,
                                                             self.detectors['flu_camera']['size'],
                                                             self.detectors['flu_camera']['exposure'])
            return serialize(image.data)
            
        else:
            print(f"Device {device} not found")
            return None

    def acquire_image_stack(self, device):
        """Acquire an image from the specified device"""
        if device in self.detectors:
            print(f"Acquiring image from {device}")
            return self.detectors[device]
        else:
            print(f"Device {device} not found")
            return None

    def acquire_spectrum(self, device, **args):
        """Acquire a spectrum from the specified device"""
        if device in self.detectors:
            print(f"Acquiring spectrum from {device}")
            return np.zeros((2048,), dtype=np.float32)
        else:
            print(f"Device {device} not found")
            return None

    def acquire_spectrum_points(self, device, points, **args):
        """Acquire a spectrum stack from the specified device"""
        if device in self.detectors:
            print(f"Acquiring spectrum stack from {device}")
            spectra = []
            for point in points:
                self.set_beam_position(point[0], point[1])
                spectra.append(self.acquire_spectrum(device, **args))
                print(f"  at point {point}")
            
        else:
            print(f"Device {device} not found")
            return None
    
    def set_beam_position(self, x, y):
        """Set the beam position in nm"""
        print(f"Moving beam to ({x}, {y})")
        return 1
    
    def get_vacuum(self):
        """Get the current vacuum level in Pa"""
        return 1e-5

    def get_microscope_status(self):
        """Get the current microscope status"""
        print("microscope vacumm is:",self.microscope.vacuum.state)
        print("column valve is: ", self.microscope.vacuum.column_valves.state)
        out_dict = {'vaccuum': self.microscope.vacuum.state,
                    'column_valve': self.microscope.vacuum.column_valves.state}
        return out_dict
    
    def aberration_correction(self, order, **args):
        """Perform aberration correction"""
        print(f"Performing aberration correction of order {order}")
        return 1

    def close(self):
        """Close the column valves and the server"""
        self.microscope.vacuum.column_valves.close()
        print("Closing valve")
        return 1
    



def main(host = "10.46.217.241", port = 9093):
    """Main function to start the server"""
    daemon = Pyro5.api.Daemon(host=host, port=port)
    uri = daemon.register(TEMServer, objectId="tem.server")
    print("Server is ready. Object uri =", uri)
    daemon.requestLoop()

if __name__ == "__main__":
    main()
