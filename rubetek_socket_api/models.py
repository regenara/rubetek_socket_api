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


class DeviceState(BaseModel):
    child_ev1527_lastAction: Optional[int] = Field(None, alias='child:ev1527:lastAction')
    cloud_online: Optional[bool] = Field(None, alias='cloud:online')
    cloud_regUrl: Optional[str] = Field(None, alias='cloud:regUrl')
    cloud_wsUrl: Optional[str] = Field(None, alias='cloud:wsUrl')
    dev_features: Optional[str] = Field(None, alias='dev:features')
    dev_fw_libESP32_version: Optional[int] = Field(None, alias='dev:fw:libESP32:version')
    dev_fw_loglevel: Optional[int] = Field(None, alias='dev:fw:loglevel')
    dev_hostname: Optional[str] = Field(None, alias='dev:hostname')
    dev_id: Optional[str] = Field(None, alias='dev:id')
    dev_mac: Optional[str] = Field(None, alias='dev:mac')
    dev_type: Optional[str] = Field(None, alias='dev:type')
    dev_version: Optional[str] = Field(None, alias='dev:version')
    health_status: Optional[int] = Field(None, alias='health:status')
    homekit_cid: Optional[int] = Field(None, alias='homekit:cid')
    hub_act_free_size: Optional[int] = Field(None, alias='hub:act:free_size')
    protect_power_maxI: Optional[float] = Field(None, alias='protect:power:maxI')
    protect_temper_maxT: Optional[int] = Field(None, alias='protect:temper:maxT')
    pwr_Irms: Optional[float] = Field(None, alias='pwr:Irms')
    pwr_Pact: Optional[float] = Field(None, alias='pwr:Pact')
    pwr_Pact_sum: Optional[float] = Field(None, alias='pwr:Pact_sum')
    pwr_Pact_sum_hourly: Optional[float] = Field(None, alias='pwr:Pact_sum:hourly')
    pwr_Vrms: Optional[float] = Field(None, alias='pwr:Vrms')
    relay_change_src: Optional[int] = Field(None, alias='relay:change_src[0]')
    relay_off_delay_us: Optional[int] = Field(None, alias='relay:off_delay_us[0]')
    relay_on_0: bool = Field(alias='relay:on[0]')
    relay_on_1: bool = Field(alias='relay:on[1]')
    relay_on_2: bool = Field(alias='relay:on[2]')
    relay_on_3: bool = Field(alias='relay:on[3]')
    relay_mode: int = Field(alias='relay:mode[0]')
    relay_on_delay_us: Optional[int] = Field(None, alias='relay:on_delay_us[0]')
    relay_state_restore: Optional[bool] = Field(None, alias='relay:state:restore')
    rf868_fota_dev_type_str: Optional[str] = Field(None, alias='rf868:fota:dev_type_str')
    rf868_hub_key_0: Optional[int] = Field(None, alias='rf868:hub:key[0]')
    rf868_hub_key_1: Optional[int] = Field(None, alias='rf868:hub:key[1]')
    rf868_hub_key_2: Optional[int] = Field(None, alias='rf868:hub:key[2]')
    rf868_hub_key_3: Optional[int] = Field(None, alias='rf868:hub:key[3]')
    rf868_hub_id: Optional[int] = Field(None, alias='rf868:hub_id')
    rgb_level: Optional[int] = Field(None, alias='rgb:level[1]')
    rtc_tz: Optional[int] = Field(None, alias='rtc:tz')
    wifi_ip: Optional[str] = Field(None, alias='wifi:ip')
    wifi_ssid: Optional[str] = Field(None, alias='wifi:ssid')

    @model_validator(mode='before')
    @classmethod
    def get_relay_on(cls, values: dict) -> dict:
        values['relay:on[0]'] = values.get('relay:on[0]', False)
        values['relay:on[1]'] = values.get('relay:on[1]', False)
        values['relay:on[2]'] = values.get('relay:on[2]', False)
        values['relay:on[3]'] = values.get('relay:on[3]', False)
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


class RelayValidation(BaseModel):
    value: conint(ge=0, le=3)
