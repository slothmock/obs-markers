import time
import obsws_python as obs
from enum import Enum, auto
import logging


class OBSConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    AUTH_ERROR = auto()


class OBSClient:
    def __init__(self, logger: logging.Logger, host="localhost", port=4455, password=None):
        self.logger = logger
        self.host = host
        self.port = port
        self.password = password

        self.client = None
        self.state = OBSConnectionState.DISCONNECTED
        self.last_error = None

        self.retry_attempts = 0
        self.next_retry_at = 0

        # Attempt initial connection
        self.connect()

    # ---------------- Connection ----------------
    def connect(self) -> bool:
        """Attempt to connect to OBS, respecting backoff timing."""
        now = time.time()

        if self.state == OBSConnectionState.CONNECTED:
            return True

        if now < self.next_retry_at:
            # Still in backoff period
            return False

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
            self.retry_attempts = 0
            self.next_retry_at = 0

            self.logger.info("OBS connected")
            return True

        except ConnectionRefusedError as e:
            self._handle_connection_failure(e, "Connection refused")
            return False

        except obs.reqs.OBSSDKError as e:
            msg = str(e).lower()
            if "identify" in msg or "authentication" in msg:
                self.logger.error(
                    "OBS authentication error: check your password.",
                    exc_info=e
                )
                self.client = None
                self.state = OBSConnectionState.AUTH_ERROR
                self.last_error = str(e)
                # Allow reconnect after reset/update_settings
                self.retry_attempts = 0
                self.next_retry_at = 0
                return False
            else:
                self._handle_connection_failure(e, "OBS SDK error")
                return False

        except Exception as e:
            self._handle_connection_failure(e, "Unknown error")
            return False

    def _handle_connection_failure(self, e: Exception, context: str):
        """Increment retry attempts and set next retry time with backoff."""
        self.client = None
        self.state = OBSConnectionState.DISCONNECTED
        self.last_error = str(e)
        self.retry_attempts += 1

        if self.retry_attempts <= 1:
            delay = 0
            self.logger.warning(
                f"{context}: retrying immediately ({self.retry_attempts}/3)",
                exc_info=e
            )
        elif self.retry_attempts <= 3:
            delay = 5
            self.logger.warning(
                f"{context}: backing off {delay}s ({self.retry_attempts}/3)",
                exc_info=e
            )
        else:
            delay = 30
            self.logger.error(
                f"{context}: repeated failures, backing off {delay}s",
                exc_info=e
            )

        self.next_retry_at = time.time() + delay

    # ---------------- Disconnect / Reset ----------------
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

    def reset(self):
        """Clear state and attempt reconnect immediately."""
        self.logger.info("Resetting OBS connection state")
        self.client = None
        self.state = OBSConnectionState.DISCONNECTED
        self.last_error = None
        self.retry_attempts = 0
        self.next_retry_at = 0

        self.connect()

    # ---------------- Utility ----------------
    def is_connected(self) -> bool:
        return self.state == OBSConnectionState.CONNECTED

    def call(self, fn, *args, **kwargs):
        """
        Safely call an OBS function.
        Handles reconnects and marks disconnected if OBS is unavailable.
        """
        if self.state == OBSConnectionState.AUTH_ERROR:
            # Cannot call OBS functions until password is corrected
            return None

        if not self.is_connected():
            self.connect()
            return None

        try:
            return fn(*args, **kwargs)
        except obs.reqs.OBSSDKRequestError as e:
            if e.code == 207:
                # OBS is not ready yet
                self.logger.debug("OBS not ready (207)")
                self.state = OBSConnectionState.CONNECTING
                return None
        except Exception as e:
            self.logger.warning("Lost OBS connection", exc_info=e)
            self.client = None
            self.state = OBSConnectionState.DISCONNECTED
            self.last_error = str(e)
            return None

    # ---------------- Update Settings ----------------
    def update_settings(self, host, port, password):
        """Apply new OBS connection settings and reconnect."""
        self.logger.info("Updating OBS client settings")
        self.host = host
        self.port = port
        self.password = password
        self.reset()
