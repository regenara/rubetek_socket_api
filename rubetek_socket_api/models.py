from datetime import datetime
from typing import (Any,
                    List,
                    Optional)

from pydantic import (BaseModel,
                      Field,
                      conint,
                      model_validator)


INT_MAX = 2 ** 31 - 1
INT_MIN = -2 ** 31
TIMER_VALUE = 39321600


class Token(BaseModel):
    token_type: str
    expires_in: int
    access_token: str
    refresh_token: str
    created_at: int = None


class House(BaseModel):
    created_at: datetime
    updated_at: datetime
    id: str
    name: str
    alarmed: bool
    iot_locked_id: Optional[str]
    scripts_count: int
    devices_count: int
    devices_groups_count: int
    favorites_count: int
    timezone: str
    show_hidden: bool
    devices_auto_update: bool
    access: str


class CustomData(BaseModel):
    global_position: int
    ip_address: str
    key: str
    moduleName: str
    timersOff: str
    timersOn: str
    timers_migrated: bool


class DeviceState(BaseModel):
    child_ev1527_lastAction: int = Field(alias='child:ev1527:lastAction')
    cloud_online: bool = Field(alias='cloud:online')
    cloud_regUrl: str = Field(alias='cloud:regUrl')
    cloud_wsUrl: str = Field(alias='cloud:wsUrl')
    dev_features: str = Field(alias='dev:features')
    dev_fw_libESP32_version: int = Field(alias='dev:fw:libESP32:version')
    dev_fw_loglevel: int = Field(alias='dev:fw:loglevel')
    dev_hostname: str = Field(alias='dev:hostname')
    dev_id: str = Field(alias='dev:id')
    dev_mac: str = Field(alias='dev:mac')
    dev_type: str = Field(alias='dev:type')
    dev_version: str = Field(alias='dev:version')
    health_status: int = Field(alias='health:status')
    homekit_cid: int = Field(alias='homekit:cid')
    hub_act_free_size: int = Field(alias='hub:act:free_size')
    protect_power_maxI: float = Field(alias='protect:power:maxI')
    protect_temper_maxT: int = Field(alias='protect:temper:maxT')
    pwr_Irms: float = Field(alias='pwr:Irms')
    pwr_Pact: float = Field(alias='pwr:Pact')
    pwr_Pact_sum: float = Field(alias='pwr:Pact_sum')
    pwr_Pact_sum_hourly: float = Field(alias='pwr:Pact_sum:hourly')
    pwr_Vrms: float = Field(alias='pwr:Vrms')
    relay_change_src: int = Field(alias='relay:change_src[0]')
    relay_off_delay_us: int = Field(alias='relay:off_delay_us[0]')
    relay_on: bool = Field(alias='relay:on[0]')
    relay_mode: int = Field(alias='relay:mode[0]')
    relay_on_delay_us: int = Field(alias='relay:on_delay_us[0]')
    relay_state_restore: bool = Field(alias='relay:state:restore')
    rf868_fota_dev_type_str: str = Field(alias='rf868:fota:dev_type_str')
    rf868_hub_key_0: int = Field(alias='rf868:hub:key[0]')
    rf868_hub_key_1: int = Field(alias='rf868:hub:key[1]')
    rf868_hub_key_2: int = Field(alias='rf868:hub:key[2]')
    rf868_hub_key_3: int = Field(alias='rf868:hub:key[3]')
    rf868_hub_id: int = Field(alias='rf868:hub_id')
    rgb_level: int = Field(alias='rgb:level[1]')
    rtc_tz: int = Field(alias='rtc:tz')
    wifi_ip: str = Field(alias='wifi:ip')
    wifi_ssid: str = Field(alias='wifi:ssid')

    @model_validator(mode='before')
    @classmethod
    def get_relay_on(cls, values: dict) -> dict:
        values['relay:on[0]'] = values.get('relay:on[0]', False)
        relay_mode_value = values.get('relay:mode[0]', 0)
        if relay_mode_value < 0:
            relay_mode_value += 2 ** 32
        values['relay:mode[0]'] = int(relay_mode_value / TIMER_VALUE)
        return values


class Device(BaseModel):
    created_at: datetime
    updated_at: datetime
    id: str
    class_: str = Field(alias='class')
    type: str
    natural_id: str
    child_mode: str
    icon: str
    name: str
    room: str
    hidden: bool
    favorite: bool
    disabled: bool
    custom_data: CustomData
    online: bool
    state: DeviceState


class DeviceData(BaseModel):
    devices: List[Device]
    groups: List[Any]


class User(BaseModel):
    created_at: datetime
    updated_at: datetime
    id: str
    _id: int
    phone: Optional[str] = None
    email: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None


class RGBLevelValidation(BaseModel):
    value: conint(ge=0, le=100)


class TimerValidation(BaseModel):
    value: conint(ge=0, le=109)
