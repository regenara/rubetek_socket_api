# Rubetek Socket API

### Описание / Description 
Эта библиотека предоставляет API-обертку для управления умной розеткой Rubetek RE-3305. Возможность работы с другими моделями не проверялась, но, вероятно, поддерживается.
<br>This library provides an API wrapper for controlling the Rubetek RE-3305 smart socket. Compatibility with other models has not been tested but is likely supported.

## Установка / Installation
```bash
pip install rubetek-socket-api
```

## Авторизация / Authorization

### Получение refresh token, client id и client secret / Obtaining refresh token, client id and client secret
Чтобы получить `refresh_token`, `client_id` и `client_secret`, перехватите запросы из мобильного приложения Rubetek. В примере используется Android-устройство и [HTTP Toolkit](https://httptoolkit.com/). Запросы следует перехватывать во время попытки авторизации в приложении Rubetek.
<br>To obtain the `refresh_token`, `client_id`, and `client_secret`, intercept the requests from the Rubetek mobile app. The example uses an Android device and [HTTP Toolkit](https://httptoolkit.com/). The requests should be intercepted during the authentication attempt in the Rubetek app.
<details>
  <summary>Примеры / Examples</summary>

![refresh_token](https://raw.githubusercontent.com/regenara/rubetek_socket_api/master/images/refresh_token.jpg)
*Refresh Token*

![client_id & client_secret](https://raw.githubusercontent.com/regenara/rubetek_socket_api/master/images/client.jpg)
*Client ID & Client Secret*
</details>

### Авторизация через refresh token (рекомендуется) / Authorization via refresh token (recommended)
```python
import asyncio

from rubetek_socket_api import RubetekSocketAPI

REFRESH_TOKEN = 'your_refresh_token'

async def main():
    rubetek_api = RubetekSocketAPI(refresh_token=REFRESH_TOKEN)
    user_info = await rubetek_api.get_user()
    print(user_info)
```

### Авторизация через код (не рекомендуется) / Authorization via code (not recommended)
```python
import asyncio

from rubetek_socket_api import RubetekSocketAPI

CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
PHONE = 'your_phone'
EMAIL = 'your_email'

async def sms_auth():
    rubetek_api = RubetekSocketAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    await rubetek_api.send_code(phone=PHONE)
    code = input('Enter the code: ')
    await rubetek_api.change_code_to_access_token(code=code, phone=PHONE)
    print(f'Refresh Token: {rubetek_api.refresh_token}')  # Save refresh token
    user_info = await rubetek_api.get_user()
    print(user_info)

async def email_auth():
    rubetek_api = RubetekSocketAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    await rubetek_api.send_code(email=EMAIL)
    code = input('Enter the code: ')
    await rubetek_api.change_code_to_access_token(code=code, email=EMAIL)
    print(f'Refresh Token: {rubetek_api.refresh_token}')  # Save refresh token
    user_info = await rubetek_api.get_user()
    print(user_info)
```

## Использование / Usage
```python
import asyncio

from rubetek_socket_api import RubetekSocketAPI

async def main():
    rubetek_api = RubetekSocketAPI(...)  # Выберите подходящий метод авторизации / Choose the appropriate authentication method
    houses = await rubetek_api.get_houses()
    house_id = houses[0].id
    devices = await rubetek_api.get_house_devices(house_id=house_id)
    device_id = devices[0].id
    device = await rubetek_api.get_device(house_id=house_id, device_id=device_id)
    
    print(
        f'Status (on/off): {device.state.relay_on}',
        f'RGB level: {device.state.rgb_level}',
        f'Online status: {device.online}',
        f'Sleep timer (minutes): {device.state.relay_mode}',
        sep='\n'
    )
    
    await rubetek_api.set_rgb_level(house_id=house_id, device_id=device_id, value=100)
    await rubetek_api.set_on_off(house_id=house_id, device_id=device_id, value=not device.state.relay_on)
    await rubetek_api.set_disable_timer(house_id=house_id, device_id=device_id, value=60)

    await rubetek_api.close()

asyncio.run(main())
```

