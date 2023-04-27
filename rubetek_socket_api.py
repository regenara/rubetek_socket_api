import asyncio
import logging
import ssl
from typing import Any
from urllib.parse import urljoin

import certifi
from aiohttp import (ClientSession,
                     ClientTimeout,
                     TCPConnector)
from aiohttp.client_exceptions import ClientConnectorError


class RubetekSocketAPIError(Exception):
    """"""


class TimeoutRubetekSocketAPIError(RubetekSocketAPIError):
    """"""


class UnknownRubetekSocketAPIError(RubetekSocketAPIError):
    """"""


class RubetekSocketAPI:
    def __init__(self, refresh_token: str, house_id: str, device_id: str):
        self._refresh_token: str = refresh_token
        self._access_token: str | None = None
        self._house_id: str = house_id
        self._device_id: str = device_id
        self._base_url: str = 'https://ccc.rubetek.com/'
        self._device_url: str = urljoin(self._base_url, f'v5/houses/{house_id}/devices/{device_id}/state')
        self._logger: logging = logging.getLogger('RubetekSocketAPI')
        self._logger.setLevel(logging.INFO)

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.session: ClientSession = ClientSession(connector=TCPConnector(ssl=ssl_context),
                                                    timeout=ClientTimeout(total=60))

    async def _send_request(self, url: str, method: str = 'GET', data: dict[str, Any] = None) -> dict[str, Any] | None:
        while True:
            try:
                headers = {
                    'Authorization': f'Bearer {self._access_token}',
                    'Content-Type': 'application/json; charset=UTF-8'
                }
                async with self.session.request(method, url, json=data, headers=headers) as response:
                    json = await response.json() if response.status != 204 else None
                    if response.status == 401:
                        self._logger.error('Unauthorized, trying get access_token request=%s response=%s', data, json)
                        await self._set_access_token()
                        continue
                    if response.status not in (200, 204):
                        self._logger.error('Unsuccessful request=%s response=%s', data, json)
                        raise RubetekSocketAPIError(json.get('error_description') or json.get('error') or str(json))
                    self._logger.info('Successful request=%s response=%s', data, json)
                    return json

            except asyncio.exceptions.TimeoutError:
                self._logger.error('TimeoutRubetekSocketAPIError request=%s', data)
                raise TimeoutRubetekSocketAPIError('Timeout error')

            except ClientConnectorError:
                self._logger.error('UnknownRubetekSocketAPIError request=%s', data)
                raise UnknownRubetekSocketAPIError('Unknown error')

    async def _set_access_token(self):
        url = urljoin(self._base_url, 'v5/oauth/access_token')
        data = {
            'client_id': 'rubetek_android',
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        }
        response = await self._send_request(url=url, method='POST', data=data)
        self._access_token = response['access_token']

    async def set_on_off(self, value: bool):
        """
        :param value: True - on, False - off
        """
        data = {'state': {'relay:on[0]': value}}
        await self._send_request(url=self._device_url, method='PATCH', data=data)

    async def set_rgb_level(self, value: int):
        """
        :param value: min 0, max 100
        """
        data = {'state': {'rgb:level[1]': value}}
        await self._send_request(url=self._device_url, method='PATCH', data=data)

    async def get_status(self) -> dict[str, Any]:
        url = urljoin(self._base_url, f'/v6/houses/{self._house_id}/devices?per_page=500')
        response = await self._send_request(url=url)
        result = [data for data in response['devices'] if data['id'] == self._device_id][0]
        return {
            'enabled': result['state'].get('relay:on[0]', False),
            'rgb_level': result['state'].get('rgb:level[1]'),
            'online': result['online']
        }
