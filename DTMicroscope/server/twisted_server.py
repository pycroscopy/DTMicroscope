# tem_server_twisted.py
from twisted.internet import reactor, protocol, threads
from twisted.internet.protocol import Factory
import json
import numpy as np
import socket
import sys
import os
from typing import Tuple

# --- Import your autoscript library (adjust path as needed) ---
sys.path.insert(0, r"C:\AE_future\autoscript_1_14\\")
import autoscript_tem_microscope_client as auto_script


# Keep CEOSAcquisitionTCP as-is (used internally by TEMServer)
class CEOSacquisitionTCP:
    def __init__(self, host="127.0.0.1", port=7072):
        self.host = host
        self.port = port
        self._next_id = 1

    def _send_recv(self, message: dict) -> dict:
        json_msg = json.dumps(message, separators=(",", ":"))
        payload = json_msg.encode("utf-8")
        netstring = f"{len(payload)}:".encode("ascii") + payload + b","

        with socket.create_connection((self.host, self.port), timeout=300) as sock:
            sock.sendall(netstring)
            buffer = b""
            while not buffer.endswith(b","):
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk

        try:
            length_str, rest = buffer.split(b":", 1)
            length = int(length_str)
            payload = rest[:length]
            return json.loads(payload.decode("utf-8"))
        except Exception as e:
            print("Malformed netstring or response:", buffer)
            raise

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
        if value is not None:
            params["value"] = list(value)
        if target is not None:
            params["target"] = list(target)
        if select is not None:
            params["select"] = select
        return self._run_rpc("correctAberration", params)

    def measure_c1a1(self):
        return self._run_rpc("measureC1A1", {})


# helpers
def serialize(array: np.ndarray) -> Tuple[list, tuple, str]:
    array_list = array.tolist()
    dtype = str(array.dtype)
    return array_list, array.shape, dtype


def default_flu_camera(detector_dict):
    detector_dict["flu_camera"] = {
        "size": 512,
        "exposure": 0.1,
        "binning": 1,
        "save_to_disc": False,
    }


def default_ceta_camera(detector_dict):
    detector_dict["ceta_camera"] = {
        "data": np.zeros((512, 512), dtype=np.uint16),
        "size": 512,
        "exposure": 0.1,
        "binning": 1,
    }


def default_scan(detector_dict):
    detector_dict["scan"] = {
        "data": np.zeros((512, 512), dtype=np.uint16),
        "size": 512,
        "exposure": 0.1,
        "field_of_view": (1e-6, 1e-6),
        "detectors": ["HAADF"],
    }


def default_eds(detector_dict):
    detector_dict["super_x"] = {
        "data": np.zeros(2048, dtype=np.uint16),
        "size": 512,
        "exposure": 0.1,
        "binning": 2,
        "energy_window": (0, 20000),
    }


# -------------------------
# Your TEMServer class
# -------------------------
class TEMServer(object):
    """Class to handle the microscope operations (same API as before)."""

    def __init__(self):
        print("TEMServer init")
        self.detectors = {}
        default_flu_camera(self.detectors)
        default_ceta_camera(self.detectors)
        default_scan(self.detectors)
        default_eds(self.detectors)

        # instantiate autoscript client
        self.microscope = auto_script.TemMicroscopeClient()
        # connect to autoscript - can block; we do it here at startup (before reactor)
        try:
            self.connect_to_as()
        except Exception as e:
            print("Warning: connect_to_as failed during init:", e)

        self.ab_corrector = None
        try:
            self.connect_to_ceos()
        except Exception as e:
            print("Warning: connect_to_ceos failed during init:", e)

        print("TEMServer initialized")

    # connection helpers
    def connect_to_as(self):
        ip = "127.0.0.1"
        self.microscope.connect(ip, port=9095)

    def connect_to_ceos(self):
        self.ab_corrector = CEOSacquisitionTCP(host="10.46.217.241", port=9092)

    # CEOS wrappers
    def measure_c1a1(self):
        return self.ab_corrector.measure_c1a1()

    def correct_aberration(self, name: str, value=None, target=None, select=None):
        return self.ab_corrector.correct_aberration(
            name=name, value=value, target=target, select=select
        )

    def run_tableau(self, tab_type="Standard", angle=18):
        return self.ab_corrector.run_tableau(tab_type=tab_type, angle=angle)

    # basic API methods (mirror your Pyro version)
    def get_detectors(self):
        return list(self.detectors.keys())

    def activate_device(self, device):
        if device in self.detectors:
            print(f"{device} activated")
            return 1
        else:
            print(f"Device {device} not found")
            return 0

    def device_settings(self, device, **args):
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
        positions = self.microscope.specimen.stage.position
        if self.microscope.specimen.stage.get_holder_type() == "SingleTilt":
            return [
                float(positions[0]),
                float(positions[1]),
                float(positions[2]),
                float(positions[3]),
                0,
            ]
        else:
            return [
                float(positions[0]),
                float(positions[1]),
                float(positions[2]),
                float(positions[3]),
                float(positions[4]),
            ]

    def set_stage(self, stage_positions, relative=True):
        stage_move = auto_script.structures.StagePosition()
        for index, direction in enumerate(["x", "y", "z", "a", "b"]):
            move = stage_positions.get(direction, None) if isinstance(stage_positions, dict) else None
            # also allow list input in same order
            if move is None and isinstance(stage_positions, (list, tuple)) and len(stage_positions) > index:
                move = stage_positions[index]
            setattr(stage_move, direction, move)
        if relative:
            self.microscope.specimen.stage.relative_move_safe(stage_move)
        else:
            self.microscope.specimen.stage.absolute_move_safe(stage_move)
        print(f"Moving stage by {stage_move}")
        return {"new_stage": [stage_move.x, stage_move.y, stage_move.z, stage_move.a, stage_move.b]}

    def acquire_image(self, device, **args):
        if device in self.detectors:
            print(f"Acquiring image from {device}")
            if device == "flu_camera":
                camera = auto_script.enumerations.CameraType.FLUCAM
            else:
                camera = auto_script.enumerations.CameraType.FLUCAM
            cam_detector = self.microscope.detectors.get_camera_detector(camera)
            image = self.microscope.acquisition.acquire_camera_image(
                camera, self.detectors["flu_camera"]["size"], self.detectors["flu_camera"]["exposure"]
            )
            # return (list, shape, dtype) same as before
            return serialize(image.data)
        else:
            print(f"Device {device} not found")
            return None

    def acquire_image_stack(self, device):
        if device in self.detectors:
            print(f"Acquiring image stack from {device}")
            return self.detectors[device]
        else:
            print(f"Device {device} not found")
            return None

    def acquire_spectrum(self, device, **args):
        if device in self.detectors:
            print(f"Acquiring spectrum from {device}")
            return np.zeros((2048,), dtype=np.float32)
        else:
            print(f"Device {device} not found")
            return None

    def acquire_spectrum_points(self, device, points, **args):
        if device in self.detectors:
            print("Acquiring spectra at points")
            spectra = []
            for point in points:
                self.set_beam_position(point[0], point[1])
                spectra.append(self.acquire_spectrum(device, **args))
                print(f"  at point {point}")
            return spectra
        else:
            print(f"Device {device} not found")
            return None

    def set_beam_position(self, x, y):
        print(f"Moving beam to ({x}, {y})")
        return 1

    def get_vacuum(self):
        return 1e-5

    def get_microscope_status(self):
        return "Idle"

    def aberration_correction(self, order, **args):
        print(f"Performing aberration correction of order {order}")
        return 1

    def close(self):
        print("Closing server resources")
        return 1


# -------------------------
# Twisted protocol that accepts netstring-encoded JSON-RPC requests
# -------------------------
class NetstringJSONProtocol(protocol.Protocol):
    def __init__(self, server_instance: TEMServer):
        self.buffer = b""
        self.server_instance = server_instance

    def dataReceived(self, data: bytes):
        # accumulate
        self.buffer += data
        # We support multiple netstrings in the buffer
        while b"," in self.buffer:
            try:
                # parse length up to colon
                length_str, rest = self.buffer.split(b":", 1)
                length = int(length_str)
                if len(rest) < length + 1:  # need more data (payload + trailing comma)
                    break
                payload = rest[:length]
                trailing = rest[length: length + 1]
                if trailing != b",":
                    # malformed; drop till next comma
                    # attempt robust recovery: find next comma
                    idx = self.buffer.find(b",", 1)
                    self.buffer = self.buffer[idx + 1 :] if idx >= 0 else b""
                    continue
                # advance buffer
                self.buffer = rest[length + 1 :]
                # process payload
                self._handle_payload(payload)
            except ValueError:
                # not enough data for length parsing yet
                break

    def _handle_payload(self, payload_bytes: bytes):
        try:
            request = json.loads(payload_bytes.decode("utf-8"))
            method = request.get("method")
            params = request.get("params", {})
            req_id = request.get("id", None)
            # dispatch in a thread to avoid blocking reactor
            d = threads.deferToThread(self._dispatch_method, method, params)
            d.addCallback(lambda result: self._send_success(req_id, result))
            d.addErrback(lambda f: self._send_error(req_id, str(f)))
        except Exception as e:
            self._send_error(None, f"Invalid JSON payload: {e}")

    def _dispatch_method(self, method: str, params: dict):
        if not hasattr(self.server_instance, method):
            raise AttributeError(f"Method {method} not implemented on server.")
        func = getattr(self.server_instance, method)
        # Allow params to be either dict or list
        if isinstance(params, dict):
            return func(**params)
        elif isinstance(params, (list, tuple)):
            return func(*params)
        else:
            return func(params)

    def _send_success(self, req_id, result):
        reply = {"jsonrpc": "2.0", "id": req_id, "result": result}
        self._write_netstring(reply)

    def _send_error(self, req_id, message):
        reply = {"jsonrpc": "2.0", "id": req_id, "error": str(message)}
        self._write_netstring(reply)

    def _write_netstring(self, obj):
        payload = json.dumps(obj, default=self._json_default, separators=(",", ":")).encode("utf-8")
        netstring = f"{len(payload)}:".encode("ascii") + payload + b","
        self.transport.write(netstring)

    @staticmethod
    def _json_default(o):
        # fallback for numpy types if ever present directly
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.integer, np.floating)):
            return o.item()
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


class NetstringFactory(Factory):
    def __init__(self, server_instance):
        self.server_instance = server_instance

    def buildProtocol(self, addr):
        return NetstringJSONProtocol(self.server_instance)


# -------------------------
# main
# -------------------------
def main(host="0.0.0.0", port=9093):
    server_inst = TEMServer()
    factory = NetstringFactory(server_inst)
    reactor.listenTCP(port, factory, interface=host)
    print(f"TEM Twisted server listening on {host}:{port}")
    reactor.run()


if __name__ == "__main__":
    main()