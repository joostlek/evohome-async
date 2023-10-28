#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""evohomeasync2 - Schema for RESTful API Account JSON."""
from __future__ import annotations

import voluptuous as vol  # type: ignore[import]

from .const import (
    SZ_DAILY_SCHEDULES,
    SZ_DAY_OF_WEEK,
    SZ_DHW_STATE,
    SZ_HEAT_SETPOINT,
    SZ_OFF,
    SZ_ON,
    SZ_SWITCHPOINTS,
    SZ_TIME_OF_DAY,
)
from .const import (
    SZ_MONDAY,
    SZ_TUESDAY,
    SZ_WEDNESDAY,
    SZ_THURSDAY,
    SZ_FRIDAY,
    SZ_SATURDAY,
    SZ_SUNDAY,
)

#
# This is as returned from vendor's API (GET)
DAYS_OF_WEEK = (
    SZ_MONDAY,
    SZ_TUESDAY,
    SZ_WEDNESDAY,
    SZ_THURSDAY,
    SZ_FRIDAY,
    SZ_SATURDAY,
    SZ_SUNDAY,
)

SCH_GET_SWITCHPOINT_DHW = vol.Schema(  # TODO: checkme
    {
        vol.Required(SZ_DHW_STATE): vol.Any(SZ_ON, SZ_OFF),
        vol.Required(SZ_TIME_OF_DAY): vol.Datetime(format="%H:%M:00"),
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_GET_SWITCHPOINT_ZONE = vol.Schema(
    {
        vol.Required(SZ_HEAT_SETPOINT): vol.All(float, vol.Range(min=5, max=35)),
        vol.Required(SZ_TIME_OF_DAY): vol.Datetime(format="%H:%M:00"),
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_GET_DAY_OF_WEEK_DHW = vol.Schema(
    {
        vol.Required(SZ_DAY_OF_WEEK): vol.Any(list(DAYS_OF_WEEK)),
        vol.Required(SZ_SWITCHPOINTS): [SCH_GET_SWITCHPOINT_DHW],
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_GET_DAY_OF_WEEK_ZONE = vol.Schema(
    {
        vol.Required(SZ_DAY_OF_WEEK): vol.Any(list(DAYS_OF_WEEK)),
        vol.Required(SZ_SWITCHPOINTS): [SCH_GET_SWITCHPOINT_ZONE],
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_GET_SCHEDULE_DHW = vol.Schema(
    {
        vol.Required(SZ_DAILY_SCHEDULES): [SCH_GET_DAY_OF_WEEK_DHW],
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_GET_SCHEDULE_ZONE = vol.Schema(
    {
        vol.Required(SZ_DAILY_SCHEDULES): [SCH_GET_DAY_OF_WEEK_ZONE],
    },
    extra=vol.PREVENT_EXTRA,
)

# This is as returned from vendor's API (GET)
SCH_GET_SCHEDULE = vol.Schema(  # PUT /{self._type}/{self._id}/schedule
    vol.Any(SCH_GET_SCHEDULE_DHW, SCH_GET_SCHEDULE_ZONE),
    extra=vol.PREVENT_EXTRA,
)


#
# This is after modified by evohome-client (PUT), an evohome-client anachronism?
SCH_PUT_SWITCHPOINT_DHW = vol.Schema(  # TODO: checkme
    {
        vol.Required(SZ_DHW_STATE.capitalize()): vol.Any(SZ_ON, SZ_OFF),
        vol.Required(SZ_TIME_OF_DAY.capitalize()): vol.Datetime(format="%H:%M:00"),
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_PUT_SWITCHPOINT_ZONE = vol.Schema(
    {  # NOTE: SZ_HEAT_SETPOINT is not .capitalized()
        vol.Required(SZ_HEAT_SETPOINT): vol.All(float, vol.Range(min=5, max=35)),
        vol.Required(SZ_TIME_OF_DAY.capitalize()): vol.Datetime(format="%H:%M:00"),
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_PUT_DAY_OF_WEEK_DHW = vol.Schema(
    {
        vol.Required(SZ_DAY_OF_WEEK.capitalize()): vol.Any(
            vol.All(int, vol.Range(min=0, max=6)),  # 0 is Monday
        ),
        vol.Required(SZ_SWITCHPOINTS.capitalize()): [SCH_PUT_SWITCHPOINT_DHW],
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_PUT_DAY_OF_WEEK_ZONE = vol.Schema(
    {
        vol.Required(SZ_DAY_OF_WEEK.capitalize()): vol.Any(
            vol.All(int, vol.Range(min=0, max=6)),  # 0 is Monday
        ),
        vol.Required(SZ_SWITCHPOINTS.capitalize()): [SCH_PUT_SWITCHPOINT_ZONE],
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_PUT_SCHEDULE_DHW = vol.Schema(
    {
        vol.Required(SZ_DAILY_SCHEDULES.capitalize()): [SCH_PUT_DAY_OF_WEEK_DHW],
    },
    extra=vol.PREVENT_EXTRA,
)

SCH_PUT_SCHEDULE_ZONE = vol.Schema(
    {
        vol.Required(SZ_DAILY_SCHEDULES.capitalize()): [SCH_PUT_DAY_OF_WEEK_ZONE],
    },
    extra=vol.PREVENT_EXTRA,
)

# This is as provided to the vendor's API (PUT)
SCH_PUT_SCHEDULE = vol.Schema(  # PUT /{self._type}/{self._id}/schedule
    vol.Any(SCH_PUT_SCHEDULE_DHW, SCH_PUT_SCHEDULE_ZONE),
    extra=vol.PREVENT_EXTRA,
)


# # NOTE: this helper is not tested, and is not working
# def convert_schedule_dict(old_schedule: dict) -> dict:
#     """Convert a schedule to the format returned by evohome-client's get_schedule()."""
#     result: dict[str, list] = {}
#     result[SZ_DAILY_SCHEDULES.capitalize()] = []
#     for day_of_week, schedule in enumerate(old_schedule):
#         new_schedule = {SZ_DAY_OF_WEEK.capitalize(): day_of_week}
#         for switchpoint in schedule:
#             if SZ_HEAT_SETPOINT in schedule:
#                 new_switchpoint = {SZ_HEAT_SETPOINT: switchpoint[SZ_HEAT_SETPOINT]}
#             else:
#                 new_switchpoint = {SZ_DHW_STATE.capitalize(): switchpoint[SZ_DHW_STATE]}
#             new_switchpoint[SZ_TIME_OF_DAY.capitalize()] = switchpoint[SZ_TIME_OF_DAY]
#             new_schedule[SZ_SWITCHPOINTS.capitalize()].append(new_switchpoint)
#         result[SZ_DAILY_SCHEDULES.capitalize()].append(new_schedule)
#     return result
