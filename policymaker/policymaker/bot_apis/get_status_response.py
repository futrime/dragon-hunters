from typing import Dict

from .response import Response
from .status_data import StatusData


class GetStatusResponse(Response):
    def __init__(self, data: Dict):
        super().__init__(data, _JSON_SCHEMA)

    def data(self) -> StatusData:
        return StatusData(**self._data)


_JSON_SCHEMA = {
    "type": "object",
    "properties": {},
}
