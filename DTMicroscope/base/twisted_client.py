# tem_client.py
import socket
import json
import numpy as np
from typing import Tuple, Any


class TEMClient:
    def __init__(self, host="10.46.217.241", port=9093, timeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._next_id = 1

    def _to_netstring(self, obj: dict) -> bytes:
        payload = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        return f"{len(payload)}:".encode("ascii") + payload + b","

    def _recv_netstring(self, sock: socket.socket) -> dict:
        buffer = b""
        while not buffer.endswith(b","):
            chunk = sock.recv(4096)
            if not chunk:
                break
            buffer += chunk
        if not buffer:
            raise ConnectionError("No response from server")
        try:
            length_str, rest = buffer.split(b":", 1)
            length = int(length_str)
            payload = rest[:length]
            return json.loads(payload.decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"Malformed response: {buffer}") from e

    def _call(self, method: str, params=None) -> Any:
        if params is None:
            params = {}
        msg = {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params}
        self._next_id += 1
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.sendall(self._to_netstring(msg))
            reply = self._recv_netstring(sock)
        if "error" in reply:
            raise RuntimeError(f"Server error: {reply['error']}")
        return reply.get("result", None)

    # convenience wrappers to mirror TEMServer API
    def get_detectors(self):
        return self._call("get_detectors")

    def activate_device(self, device):
        return self._call("activate_device", {"device": device})

    def device_settings(self, device, **kwargs):
        return self._call("device_settings", {"device": device, **kwargs})

    def get_stage(self):
        return self._call("get_stage")

    def set_stage(self, stage_positions, relative=True):
        # allow dict or list
        params = {"stage_positions": stage_positions, "relative": relative}
        return self._call("set_stage", params)

    def acquire_image(self, device, **kwargs):
        result = self._call("acquire_image", {"device": device, **kwargs})
        # If the server returned serialized numpy (list, shape, dtype), reconstruct it
        if isinstance(result, (list, tuple)) and len(result) == 3:
            array_list, shape, dtype = result
            arr = np.array(array_list, dtype=dtype)
            arr = arr.reshape(shape)
            return arr
        return result

    def acquire_image_stack(self, device):
        return self._call("acquire_image_stack", {"device": device})

    def acquire_spectrum(self, device, **kwargs):
        return self._call("acquire_spectrum", {"device": device, **kwargs})

    def acquire_spectrum_points(self, device, points, **kwargs):
        return self._call("acquire_spectrum_points", {"device": device, "points": points, **kwargs})

    def set_beam_position(self, x, y):
        return self._call("set_beam_position", {"x": x, "y": y})

    def get_vacuum(self):
        return self._call("get_vacuum")

    def get_microscope_status(self):
        return self._call("get_microscope_status")

    def aberration_correction(self, order, **kwargs):
        return self._call("aberration_correction", {"order": order, **kwargs})

    def close(self):
        return self._call("close")