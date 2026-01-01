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
        if self.state == OBSConnectionState.CONNECTED:
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

    def disconnect(self, reason: str | None = None):
        if self.client is None:
            self.state = OBSConnectionState.DISCONNECTED
            return

        self.logger.info(
            "Disconnecting from OBS%s",
            f": {reason}" if reason else ""
        )

        self.client = None
        self.state = OBSConnectionState.DISCONNECTED
        self.last_error = reason


    def is_connected(self) -> bool:
        return self.state == OBSConnectionState.CONNECTED
    
    def call(self, fn, *args, **kwargs):
        if not self.is_connected():
            self.connect()
            return None
        
        try:
            return fn(*args, **kwargs)
        except obs.reqs.OBSSDKRequestError as e:
            if e.code == 207:
                self.logger.debug("OBS not ready (207)")
                self.state = OBSConnectionState.CONNECTING
                return None
        except Exception as e:
            self.logger.warning("Lost OBS connection", exc_info=e)
            self.client = None
            self.state = OBSConnectionState.DISCONNECTED
            self.last_error = str(e)
            return None
        
    def update_settings(self, host, port, password):
        self.logger.info("Updating OBS client settings")

        self.host = host
        self.port = port
        self.password = password

        self.disconnect("Connection settings changed")
            

