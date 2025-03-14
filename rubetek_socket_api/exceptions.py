class RubetekSocketAPIError(Exception):
    """"""


class AuthorizationRequiredRubetekSocketAPIError(RubetekSocketAPIError):
    def __init__(self):
        super().__init__("\n--------------------------------------------------------------------------\n"
                         "rubetek_api = RubetekSocketAPI()\n"
                         "await rubetek_api.send_code(phone=PHONE)\n"
                         "code = input('Enter the code: ')\n"
                         "await rubetek_api.change_code_to_access_token(code=code, phone=PHONE)\n"
                         "print(f'Refresh Token: {rubetek_api.refresh_token}')  # Save refresh token"
                         "\n\nOR\n\n"
                         "rubetek_api = RubetekSocketAPI(refresh_token=REFRESH_TOKEN)"
                         "\n--------------------------------------------------------------------------\n")


class ClientConnectorRubetekSocketAPIError(RubetekSocketAPIError):
    """"""


class UnauthorizedRubetekSocketAPIError(RubetekSocketAPIError):
    """"""


class TimeoutRubetekSocketAPIError(RubetekSocketAPIError):
    """"""


class UnknownRubetekSocketAPIError(RubetekSocketAPIError):
    """"""
