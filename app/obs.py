import obsws_python as obs
from enum import Enum, auto


class OBSConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()


class OBSClient:
    def __init__(self, logger, host="localhost", port=4455, password=None):
        self.logger = logger
        self.host = host
        self.port = port
        self.password = password

        self.client = None
        self.state = OBSConnectionState.DISCONNECTED
        self.last_error = None


    def connect(self):
        if self.state in (OBSConnectionState.CONNECTED, OBSConnectionState.CONNECTING):
            return

        self.logger.info("Attempting OBS connection")
        self.state = OBSConnectionState.CONNECTING

        try:
            self.client = obs.ReqClient(
                host=self.host,
                port=self.port,
                password=self.password
            )
            self.client.get_stats()
            self.state = OBSConnectionState.CONNECTED
            self.last_error = None
            self.logger.info("OBS connected")
        except Exception as e:
            self.client = None
            self.state = OBSConnectionState.DISCONNECTED
            self.last_error = str(e)
            self.logger.warning("OBS connection failed", exc_info=e)


    def is_connected(self) -> bool:
        return self.state == OBSConnectionState.CONNECTED
    
    
    def call(self, fn, *args, **kwargs):
        if not self.is_connected():
            self.connect()
            return None

        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self.logger.warning("Lost OBS connection", exc_info=e)
            self.client = None
            self.state = OBSConnectionState.DISCONNECTED
            self.last_error = str(e)
            return None

