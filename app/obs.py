import obsws_python as obs

class OBSClient:
    def __init__(self):
        self.client = obs.ReqClient()
        self._assert_alive()

    def _assert_alive(self):
        self.client.get_stats()

    def is_recording(self) -> bool:
        return self.client.get_record_status().output_active
