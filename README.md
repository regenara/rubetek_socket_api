# Rubetek Socket API

### Описание / Description 
[Эта библиотека](https://pypi.org/project/rubetek-socket-api/) предоставляет API-обертку для управления умной розеткой Rubetek RE-3305 и умным сетевым фильтром RE-3310. Возможность работы с другими моделями не проверялась, но, вероятно, поддерживается. Для использования данной библиотеки необходимо быть зарегистрированным пользователем в приложении Rubetek, а также иметь устройство, добавленное в это приложение.

[This library](https://pypi.org/project/rubetek-socket-api/) provides an API wrapper for controlling the Rubetek RE-3305 smart socket and smart power strip RE-3310. While compatibility with other models has not been tested, it is likely supported. To use this library, you must be a registered user in the Rubetek app and have your device added to the this app.


## Установка / Installation
```bash
pip install rubetek-socket-api
```

## Авторизация / Authorization
### Авторизация через код / Authorization via code
Этот метод предназначен только для первичной авторизации. Чрезмерное использование может привести к блокировке или ограничению сервером. Получите refresh token и используйте его для будущих запросов.

This method is intended only for initial authorization. Frequent use may result in server-side blocking or rate limitations. Obtain a refresh token and use it for future requests.
```python
from rubetek_socket_api import RubetekSocketAPI

PHONE = 'your_phone'
EMAIL = 'your_email'

async def sms_auth():
    rubetek_api = RubetekSocketAPI()
    await rubetek_api.send_code(phone=PHONE)
    code = input('Enter the code: ')
    await rubetek_api.change_code_to_access_token(code=code, phone=PHONE)
    print(f'Refresh Token: {rubetek_api.refresh_token}')  # Save refresh token
    user_info = await rubetek_api.get_user()
    print(user_info)

# OR
    
async def email_auth():
    rubetek_api = RubetekSocketAPI()
    await rubetek_api.send_code(email=EMAIL)
    code = input('Enter the code: ')
    await rubetek_api.change_code_to_access_token(code=code, email=EMAIL)
    print(f'Refresh Token: {rubetek_api.refresh_token}')  # Save refresh token
    user_info = await rubetek_api.get_user()
    print(user_info)
```
### Авторизация через refresh token / Authorization via refresh token
```python
from rubetek_socket_api import RubetekSocketAPI

REFRESH_TOKEN = 'your_refresh_token'

async def main():
    rubetek_api = RubetekSocketAPI(refresh_token=REFRESH_TOKEN)
    user_info = await rubetek_api.get_user()
    print(user_info)
```

## Использование / Usage
```python
import asyncio

from rubetek_socket_api import RubetekSocketAPI

REFRESH_TOKEN = 'your_refresh_token'

async def main():
    rubetek_api = RubetekSocketAPI(refresh_token=REFRESH_TOKEN)
    houses = await rubetek_api.get_houses()
    house_id = houses[0].id
    devices = await rubetek_api.get_house_devices(house_id=house_id)
    for d in devices:
        device = await rubetek_api.get_device(house_id=house_id, device_id=d.id)

        # RE-3310
        if 'сетевой фильтр' in device.name:
            print(
                f'Device: {device.name}',
                f'Status socket #0: {device.state.relay_on_0}',
                f'Status socket #1: {device.state.relay_on_1}',
                f'Status socket #2: {device.state.relay_on_2}',
                f'Status USB: {device.state.relay_on_3}',
                f'Online status: {device.online}',
                sep='\n'
            )
            await rubetek_api.set_on_off(house_id=house_id, device_id=device.id, value=not device.state.relay_on_0)  # socket 0
            await rubetek_api.set_on_off(house_id=house_id, device_id=device.id, value=not device.state.relay_on_1, relay=1)  # socket 1
            await rubetek_api.set_on_off(house_id=house_id, device_id=device.id, value=not device.state.relay_on_2, relay=2)  # socket 2
            await rubetek_api.set_on_off(house_id=house_id, device_id=device.id, value=not device.state.relay_on_3, relay=3)  # USB

        # RE-3305
        if 'RE-3305' in device.name:
            print(
                f'Device: {device.name}',
                f'Status (on/off): {device.state.relay_on_0}',
                f'RGB level (percent): {device.state.rgb_level}',
                f'Online status: {device.online}',
                f'Sleep timer (minutes): {device.state.relay_mode}',
                sep='\n'
            )
            await rubetek_api.set_rgb_level(house_id=house_id, device_id=device.id, value=100)
            await rubetek_api.set_on_off(house_id=house_id, device_id=device.id, value=not device.state.relay_on_0)
            await rubetek_api.set_disable_timer(house_id=house_id, device_id=device.id, value=60)

    await rubetek_api.close()

asyncio.run(main())
```

