"""Client wrapper for the heitzfit4 integration."""

### Hotfix for python 3.13 https://github.com/bain3/heitzfit4py/pull/317#issuecomment-2523257656
import autoslot
from itertools import tee
import dis


def assignments_to_self(method) -> set:
    instance_var = next(iter(method.__code__.co_varnames), "self")
    instructions = dis.Bytecode(method)
    i0, i1 = tee(instructions)
    next(i1, None)
    names = set()
    for a, b in zip(i0, i1):
        accessing_self = (
            a.opname in ("LOAD_FAST", "LOAD_DEREF") and a.argval == instance_var
        ) or (a.opname == "LOAD_FAST_LOAD_FAST" and a.argval[1] == instance_var)
        storing_attribute = b.opname == "STORE_ATTR"
        if accessing_self and storing_attribute:
            names.add(b.argval)
    return names


autoslot.assignments_to_self = assignments_to_self
### End Hotfix

import heitzfit4py
import json
import logging
import re

_LOGGER = logging.getLogger(__name__)


def get_heitzfit4_client(data) -> heitzfit4py.Client | None:
    _LOGGER.debug(f"Club: {data['club']}")
    return get_client_from_username_password(data)


def get_client_from_username_password(
    data,
) -> heitzfit4py.Client | None:
    # url = data["url"]
    # url = re.sub(r"/[^/]+\.html$", "/", url)
    # if not url.endswith("/"):
    #     url += "/"
    # url = url + ("parent" if data["account_type"] == "parent" else "eleve") + ".html"

    # ent = None
    # if "ent" in data:
    #     ent = getattr(heitzfit4py.ent, data["ent"])

    # if not ent:
    #     url += "?login=true"
    url="https://app.heitzfit.com/c/3649/ws/api/planning/browse?startDate=2024-12-26&numberOfDays=6&idActivities=&idEmployees=&idRooms=&idGroups=&hourStart=&hourEnd=&stackBy=date&caloriesMin=&caloriesMax=&idCenter=3649"
    try:
        client = (
            heitzfit4py.Client
        )(
            heitzfit4_url=url,
            # username=data["username"],
            # password=data["password"],
            # account_pin=data.get("account_pin", None),
            # device_name=data.get("device_name", None),
            client_identifier=data.get("clientId", None),
            # ent=ent,
        )
        # del ent
        # del client.account_pin
        _LOGGER.info(client.info.name)
    except Exception as err:
        _LOGGER.critical(err)
        return None

    return client


# def get_client_from_qr_code(data) -> heitzfit4py.Client | heitzfit4py.ParentClient | None:
#     qr_code_username = data["qr_code_username"]
#     qr_code_password = data["qr_code_password"]
#     qr_code_uuid = data["qr_code_uuid"]
#     qr_code_account_pin = data.get("account_pin", None)
#     qr_code_device_name = data.get("device_name", None)
#     qr_code_client_identifier = data.get("client_identifier", None)

#     _LOGGER.info(f"Coordinator uses qr_code_username: {qr_code_username}")
#     _LOGGER.info(f"Coordinator uses qr_code_pwd: {qr_code_password}")

#     return (
#         heitzfit4py.ParentClient if data["account_type"] == "parent" else heitzfit4py.Client
#     ).token_login(
#         heitzfit4_url=qr_code_url,
#         username=qr_code_username,
#         password=qr_code_password,
#         uuid=qr_code_uuid,
#         account_pin=qr_code_account_pin,
#         device_name=qr_code_device_name,
#         client_identifier=qr_code_client_identifier,
#     )


def get_day_start_at(activitys):
    day_start_at = None

    if activitys is not None:
        for activity in activitys:
            if not activity.canceled:
                day_start_at = activity.start
                break

    return day_start_at


# def get_heitzfit4_client(data) -> heitzfit4py.Client | heitzfit4py.ParentClient | None:
#     _LOGGER.debug(f"Coordinator uses connection: {data['connection_type']}")

#     if data["connection_type"] == "qrcode":
#         return get_client_from_qr_code(data)
#     else:
#         return get_client_from_username_password(data)


# def get_client_from_username_password(
#     data,
# ) -> heitzfit4py.Client | heitzfit4py.ParentClient | None:
#     # url = data["url"]
#     # url = re.sub(r"/[^/]+\.html$", "/", url)
#     # if not url.endswith("/"):
#     #     url += "/"
#     # url = url + ("parent" if data["account_type"] == "parent" else "eleve") + ".html"

#     # ent = None
#     # if "ent" in data:
#     #     ent = getattr(heitzfit4py.ent, data["ent"])

#     # if not ent:
#     #     url += "?login=true"
#     url="https://app.heitzfit.com/c/3649/ws/api/planning/browse?startDate=2024-12-20&numberOfDays=6&idActivities=&idEmployees=&idRooms=&idGroups=&hourStart=&hourEnd=&stackBy=date&caloriesMin=&caloriesMax=&idCenter=3649"
#     try:
#         client = (
#             heitzfit4py.ParentClient
#             if data["account_type"] == "parent"
#             else heitzfit4py.Client
#         )(
#             heitzfit4_url=url,
#             username=data["username"],
#             password=data["password"],
#             account_pin=data.get("account_pin", None),
#             device_name=data.get("device_name", None),
#             client_identifier=data.get("client_identifier", None),
#             ent=ent,
#         )
#         del ent
#         del client.account_pin
#         _LOGGER.info(client.info.name)
#     except Exception as err:
#         _LOGGER.critical(err)
#         return None

#     return client


# def get_client_from_qr_code(data) -> heitzfit4py.Client | heitzfit4py.ParentClient | None:

#     if "qr_code_json" in data:  # first login from QR Code JSON

#         # login with qrcode json
#         qr_code_json = json.loads(data["qr_code_json"])
#         qr_code_pin = data["qr_code_pin"]
#         uuid = data["qr_code_uuid"]

#         # get the initial client using qr_code
#         client = (
#             heitzfit4py.ParentClient
#             if data["account_type"] == "parent"
#             else heitzfit4py.Client
#         ).qrcode_login(
#             qr_code=qr_code_json,
#             pin=qr_code_pin,
#             uuid=uuid,
#             account_pin=data.get("account_pin", None),
#             client_identifier=data.get("client_identifier", None),
#             device_name=data.get("device_name", None),
#         )

#         qr_code_url = client.heitzfit4_url
#         qr_code_username = client.username
#         qr_code_password = client.password
#         qr_code_uuid = client.uuid
#         qr_code_account_pin = client.account_pin
#         qr_code_device_name = client.device_name
#         qr_code_client_identifier = client.client_identifier
#     else:
#         qr_code_url = data["qr_code_url"]
#         qr_code_username = data["qr_code_username"]
#         qr_code_password = data["qr_code_password"]
#         qr_code_uuid = data["qr_code_uuid"]
#         qr_code_account_pin = data.get("account_pin", None)
#         qr_code_device_name = data.get("device_name", None)
#         qr_code_client_identifier = data.get("client_identifier", None)

#     _LOGGER.info(f"Coordinator uses qr_code_username: {qr_code_username}")
#     _LOGGER.info(f"Coordinator uses qr_code_pwd: {qr_code_password}")

#     return (
#         heitzfit4py.ParentClient if data["account_type"] == "parent" else heitzfit4py.Client
#     ).token_login(
#         heitzfit4_url=qr_code_url,
#         username=qr_code_username,
#         password=qr_code_password,
#         uuid=qr_code_uuid,
#         account_pin=qr_code_account_pin,
#         device_name=qr_code_device_name,
#         client_identifier=qr_code_client_identifier,
#     )


# def get_day_start_at(activitys):
#     day_start_at = None

#     if activitys is not None:
#         for activity in activitys:
#             if not activity.canceled:
#                 day_start_at = activity.start
#                 break

#     return day_start_at
