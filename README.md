### Rubetek Smart Socket API wrapper
Для модели RE-3305<br>С другими моделями не проверял

#### Перед началом работы
Необходимо отловить запросы из приложения Rubetek и достать оттуда `refresh_token`, `house_id` и `device_id`. Я использовал Android и [HTTP Toolkit](https://httptoolkit.com/). Отлавливать запросы нужно в только установленном или предварительно разлогиненном приложении.
