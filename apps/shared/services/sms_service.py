from json import JSONDecodeError
import logging

from decouple import config
from django_autoutils.exceptions import RequestException
import requests

from utils.general.singleton import Singleton

logger = logging.getLogger("sms")


class SMSService(metaclass=Singleton):
    @staticmethod
    def send_sms(message, recipient):
        pass

    @staticmethod
    def send_otp(otp, recipient):
        data = {"bodyId": 317892, "to": recipient, "args": [f"{otp}"]}
        try:
            response = requests.post(config("MELIPAYAMAK_API"), json=data)
            response.raise_for_status()
        except RequestException as e:
            logger.exception(f"Failed to send OTP to {recipient}: {e}")
            return None
        try:
            json_response = response.json()
        except JSONDecodeError:
            logger.error(f"Non-JSON response received from SMS API: {response.text}")
            return None

        if "recId" in json_response:
            logger.info(f"SMS OTP sent to {recipient} - Response: {json_response}")
        else:
            logger.error(f"SMS OTP sent to {recipient} - Response: {json_response}")
        return response
