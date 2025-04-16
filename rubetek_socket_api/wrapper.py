import asyncio
import logging
import ssl
from contextlib import suppress
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import (Any,
                    Dict,
                    List,
                    Optional,
                    Union)
from urllib.parse import urljoin
from uuid import uuid4

import certifi
from aiohttp import (ClientSession,
                     ClientTimeout,
                     TCPConnector)
from aiohttp.client_exceptions import (ClientConnectorError,
                                       ContentTypeError)

from .exceptions import (AuthorizationRequiredRubetekSocketAPIError,
                         ClientConnectorRubetekSocketAPIError,
                         TimeoutRubetekSocketAPIError,
                         UnauthorizedRubetekSocketAPIError,
                         UnknownRubetekSocketAPIError)
from .models import (INT_MAX,
                     INT_MIN,
                     TIMER_VALUE,
                     Device,
                     House,
                     RelayValidation,
                     RGBLevelValidation,
                     TimerValidation,
                     Token,
                     User)


class RubetekSocketAPI:
    def __init__(self, refresh_token: Optional[str] = None,
                 refresh_token_path: Optional[Path] = Path('./rubetek_refresh_token'),
                 timeout: int = 30, level: logging = logging.INFO):
        self.refresh_token: Optional[str] = refresh_token
        self.refresh_token_path: Optional[Path] = refresh_token_path
        self._client_id: str = 'ckvfvkClm2IdPrkSlvWSe3KiEWJOAbyKOQR5giCYYAo'
        self._client_secret: str = '_TiXiy8xkVmVEpTBoYndqvyYbldXFs00wBtgLNmSOCE'
        self._access_token: Optional[str] = None
        self._base_url: str = 'https://ccc.rubetek.com/'
        self._iot_url: str = 'https://iot.rubetek.com/'
        self._logger: logging = logging.getLogger('RubetekSocketAPI')
        self._logger.setLevel(level)

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.session: ClientSession = ClientSession(connector=TCPConnector(ssl=ssl_context),
                                                    timeout=ClientTimeout(total=timeout))

    async def _send_request(self, url: str, method: str = 'GET', params: Dict[str, Any] = None,
                            json: Dict[str, Any] = None, headers: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        while True:
            headers_ = headers or {
                'Authorization': f'Bearer {self._access_token}',
                'Content-Type': 'application/json; charset=UTF-8'
            }
            request_id = uuid4().hex
            self._logger.info('Request=%s method=%s url=%s params=%s json=%s',
                              request_id, method, url, params, json)
            try:
                async with self.session.request(method, url, params=params, json=json, headers=headers_) as response:
                    json_response = await response.json() if response.status == 200 else {}
                    if response.status == 401:
                        raise UnauthorizedRubetekSocketAPIError
                    if response.status not in (200, 201, 204):
                        self._logger.error('Response=%s unsuccessful request json_response=%s status=%s reason=%s',
                                           request_id, json_response, response.status, response.reason)
                        raise UnknownRubetekSocketAPIError(json_response.get('error_description') or
                                                           json_response.get('error') or json_response)
                    self._logger.info('Response=%s json_response=%s', request_id, json_response)
                    return json_response

            except (JSONDecodeError, ContentTypeError) as e:
                self._logger.error('Response=%s unsuccessful request status=%s reason=%s error=%s',
                                   request_id, response.status, response.reason, e)
                raise UnknownRubetekSocketAPIError(f'Unknown error: {response.status} {response.reason}')

            except asyncio.exceptions.TimeoutError:
                self._logger.error('Response=%s TimeoutRubetekSocketAPIError', request_id)
                raise TimeoutRubetekSocketAPIError('Timeout error')

            except ClientConnectorError:
                self._logger.error('Response=%s ClientConnectorRubetekSocketAPIError', request_id)
                raise ClientConnectorRubetekSocketAPIError('Client connector error')

            except UnauthorizedRubetekSocketAPIError:
                self._logger.error('Response=%s UnauthorizedRubetekSocketAPIError, trying get access_token', request_id)
                self._check_refresh_token(request_id=request_id)
                await self._set_access_token()

    @staticmethod
    def _overflow_value(value: int):
        if value > INT_MAX:
            value -= 2 ** 32
        elif value < INT_MIN:
            value += 2 ** 32
        return value

    def _check_refresh_token(self, request_id: str):
        if not self.refresh_token and self.refresh_token_path:
            with suppress(FileNotFoundError):
                with open(self.refresh_token_path) as f:
                    self.refresh_token = f.read()
        if not self.refresh_token:
            self._logger.error('Response=%s AuthorizationRequiredRubetekSocketAPIError', request_id)
            raise AuthorizationRequiredRubetekSocketAPIError

    def _save_refresh_token(self, refresh_token: str):
        if self.refresh_token_path:
            with open(self.refresh_token_path, 'w') as f:
                f.write(refresh_token)
            self._logger.info('New refresh token saved to file %s', self.refresh_token_path)

    async def _set_access_token(self):
        url = urljoin(self._base_url, 'v5/oauth/access_token')
        json = {
            'client_id': 'rubetek_android',
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        response = await self._send_request(url=url, method='POST', json=json)
        token = Token(**response)
        self._access_token = token.access_token

    async def _set_state(self, house_id: str, device_id: str, state: Dict[str, Any]):
        url = urljoin(self._base_url, f'v5/houses/{house_id}/devices/{device_id}/state')
        json = {
            'state': state
        }
        await self._send_request(url=url, method='PATCH', json=json)

    async def send_code(self, email: Optional[str] = None, phone: Optional[str] = None):
        """
        :param email: The email address to receive the verification code
        :param phone: The phone number to receive the verification code.
                      Must start with '+' followed by the country code and number
        """
        if not ((email is not None) ^ (phone is not None)):
            raise ValueError('Either "email" or "phone" must be provided.')

        url = urljoin(self._iot_url, 'api/v1/code_requests')
        json = {
            'code_request': {
                'length': 6
            }
        }
        if email is not None:
            json['code_request'].update({'email': email, 'method': 'email'})
        else:
            json['code_request'].update({'phone': phone, 'method': 'sms'})
        headers = {
            'Host': 'iot.rubetek.com',
            'User-Agent': 'okhttp/4.12.0',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': '_iot_rubetek_com_session=IRsv98v2DswIJJ1i2VKdWcVzOyv8%2BVlPAldUGbFqUe3eKwLT8VK%2BfuWvHFo1JJKa'
                      'pEAqoQOfMTBhfuQ14xgkV7TBQy2hllQTtu2R8J2oo8sgCtPQWRO9aInCxeJB4wQ7UX%2F%2FXiZafoIAjT%2BKrHWAueo'
                      '6HaH232cje1h2vT4HX0vQarHhLk75SQipMrOuIhefdOQW7fzKamFavxtyquxtrBV9uEhOdQULVbbxQt3AjqGAbAY%2BsH'
                      'zjgI%2FEIfw0qI8XJcjry1aD3yFex316kDABTGU4PCDJdOm1telhF8rAjpCKe2CMISv3g8okyvx9oc3ELAlbvREG%2BxV'
                      'onOH2--4WBiJmIgZZT825rb--45HBPHoCrH8aa9ly%2B6cVyA%3D%3D; locale=ru'
        }
        await self._send_request(url=url, method='POST', json=json, headers=headers)

    async def change_code_to_access_token(self, code: Union[int, str], email: Optional[str] = None,
                                          phone: Optional[str] = None) -> Token:
        """
        :param code: The code received via email or phone
        :param email: The email address to receive the verification code
        :param phone: The phone number to receive the verification code.
                      Must start with '+' followed by the country code and number
        """
        if not ((email is not None) ^ (phone is not None)):
            raise ValueError('Either "email" or "phone" must be provided.')

        url = urljoin(self._iot_url, 'oauth/token')
        params = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'password',
            'code': str(code),
        }
        if email is not None:
            params['email'] = email
        else:
            params['phone'] = phone
        response = await self._send_request(url=url, method='POST', params=params)
        iot_token = Token(**response)
        url = urljoin(self._base_url, 'v5/oauth/iot')
        json = {
            'client_id': 'rubetek_android',
            'token': f'Bearer {iot_token.access_token}'
        }
        response = await self._send_request(url=url, method='POST', json=json)
        token = Token(**response)
        self._access_token = token.access_token
        self.refresh_token = token.refresh_token
        self._save_refresh_token(refresh_token=token.refresh_token)
        return token

    async def get_houses(self) -> List[House]:
        url = urljoin(self._base_url, '/v6/houses')
        params = {'per_page': 1000, 'include_deleted': 'true'}
        response = await self._send_request(url=url, params=params)
        return [House(**h) for h in response]

    async def get_house_devices(self, house_id: str) -> List[Device]:
        """
        :param house_id: The house ID, can be obtained using the get_houses method
        """
        url = urljoin(self._base_url, f'v6/houses/{house_id}/devices')
        params = {'per_page': 500, 'include_deleted': 'true'}
        response = await self._send_request(url=url, params=params)
        return [Device(**d) for d in response['devices']]

    async def get_device(self, house_id: str, device_id: str) -> Optional[Device]:
        """
        :param house_id: The house ID, can be obtained using the get_houses method
        :param device_id: The device ID, can be obtained using the get_house_devices method
        """
        devices = await self.get_house_devices(house_id=house_id)
        device = next((d for d in devices if d.id == device_id), None)
        return device

    async def get_user(self) -> User:
        url = urljoin(self._base_url, 'v5/user')
        response = await self._send_request(url=url)
        return User(**response)

    async def set_on_off(self, house_id: str, device_id: str, value: bool, relay: int = 0):
        """
        :param house_id: The house ID, can be obtained using the get_houses method
        :param device_id: The device ID, can be obtained using the get_house_devices method
        :param value: True - on, False - off
        :param relay: Relay index
        """
        RelayValidation(value=value)
        state = {
            f'relay:on[{relay}]': value
        }
        await self._set_state(house_id=house_id, device_id=device_id, state=state)

    async def set_rgb_level(self, house_id: str, device_id: str, value: int):
        """
        :param house_id: The house ID, can be obtained using the get_houses method
        :param device_id: The device ID, can be obtained using the get_house_devices method
        :param value: Level, min 0, max 100
        """
        RGBLevelValidation(value=value)
        state = {
            'rgb:level[1]': value
        }
        await self._set_state(house_id=house_id, device_id=device_id, state=state)

    async def set_disable_timer(self, house_id: str, device_id: str, value: int):
        """
        :param house_id: The house ID, can be obtained using the get_houses method
        :param device_id: The device ID, can be obtained using the get_house_devices method
        :param value: Minutes, min 0, max 109
        """
        TimerValidation(value=value)
        value = value * TIMER_VALUE
        if value:
            value += 1
        state = {
            'relay:mode[0]': self._overflow_value(value=value)
        }
        await self._set_state(house_id=house_id, device_id=device_id, state=state)

    async def close(self):
        await self.session.close()
