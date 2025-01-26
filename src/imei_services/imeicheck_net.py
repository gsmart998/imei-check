from enum import Enum
import requests
import json
from requests.exceptions import RequestException

from logger_config import get_logger

log = get_logger(__name__)  # get configured logger


class ImeiStatus(Enum):
    SUCCESSFUL = "successful"
    FAILED = "failed"
    UNSUCCESSFUL = "unsuccessful"


class ImeiChecker():
    ERROR_STATUSES = {
        ImeiStatus.FAILED.value: "Internal error occurred during checking. Please, try again later.",
        ImeiStatus.UNSUCCESSFUL.value: "System did not find information for deviceId using the provided service.",
    }

    def __init__(self, token: str):
        self._service_name: str = "imeicheck.net"
        self._base_url: str = "https://api.imeicheck.net/v1/"
        self._headers: dict = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, data=None) -> dict:
        """Helper method for making HTTP requests."""
        url = self._base_url + endpoint
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._headers,
                data=data,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 422:
                log.error(f"Error during request to {url}: {response.text}")
                raise RuntimeError(response.text)

        except RequestException as e:
            log.error(f"HTTP error during request to {url}: {e}")
            raise RuntimeError(f"HTTP error during request to {url}: {e}")

        except json.JSONDecodeError as e:
            log.error(f"Error decoding JSON response: {e}")
            raise RuntimeError(f"Error decoding JSON response: {e}")

    def _process_imei_status(self, data: dict) -> dict:
        """Process the response status for the IMEI check."""
        status = data.get("status")
        if status == ImeiStatus.SUCCESSFUL.value:
            log.info("IMEI check successful.")
            return data["properties"]

        if status in self.ERROR_STATUSES:
            log.warning(f"IMEI check failed: {status}")
            raise RuntimeError(self.ERROR_STATUSES[status])

        log.error(f"Unknown status received from API: {status}")
        raise RuntimeError(f"Unknown status received from API.")

    def get_service_name(self) -> str:
        """Get the current list of services from the API"""
        return self._service_name

    def get_balance(self) -> float:
        data = self._make_request(method="GET", endpoint="account")
        return float(data.get("balance", 0.0))

    def get_services(self) -> list[dict]:
        return self._make_request(method="GET", endpoint="services")

    def get_imei_info(self, imei: str, service_id: int) -> dict:
        body = json.dumps({
            "deviceId": imei,
            "serviceId": service_id
        })
        data = self._make_request(method="POST", endpoint="checks", data=body)
        return self._process_imei_status(data=data)
