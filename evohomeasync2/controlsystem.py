#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""Provides handling of a TCC Temperature Control System."""
from __future__ import annotations

from datetime import datetime as dt
import json
import logging
from typing import TYPE_CHECKING

from .const import API_STRFTIME, URL_BASE
from .hotwater import HotWater
from .zone import Zone

if TYPE_CHECKING:
    from . import EvohomeClient, Gateway, Location
    from .typing import _FilePathT, _ModeT, _SystemIdT


_LOGGER = logging.getLogger(__name__)


class ControlSystem:
    """Instance of a gateway's Temperature Control System."""

    systemId: _SystemIdT
    #

    def __init__(
        self,
        client: EvohomeClient,
        location: Location,
        gateway: Gateway,
        config: dict,
    ) -> None:
        self.client = client
        self.location = location
        self.gateway = gateway

        self._zones: list[Zone] = []
        self.zones: dict[str, Zone] = {}  # zone by name
        self.zones_by_id: dict[str, Zone] = {}
        self.hotwater: None | HotWater = None

        self.__dict__.update({k: v for k, v in config.items() if k != "zones"})
        assert self.systemId, "Invalid config dict"

        for zone_config in config["zones"]:
            zone = Zone(client, zone_config)

            self._zones.append(zone)
            self.zones[zone.name] = zone
            self.zones_by_id[zone.zoneId] = zone

        if dhw_config := config.get("dhw"):
            self.hotwater = HotWater(client, dhw_config)

    async def _set_status(self, mode: _ModeT, /, *, until: None | dt = None) -> None:
        """TODO"""

        headers = dict(await self.client._headers())
        headers["Content-Type"] = "application/json"

        if until is None:
            data = {"SystemMode": mode, "TimeUntil": None, "Permanent": True}
        else:
            data = {
                "SystemMode": mode,
                "TimeUntil": until.strftime(API_STRFTIME),
                "Permanent": False,
            }

        url = f"{URL_BASE}/temperatureControlSystem/{self.systemId}/mode"

        async with self.client._session.put(
            url, json=data, headers=await self.client._headers()
        ) as response:
            response.raise_for_status()

    async def set_status(self, mode: _ModeT, /, *, until: None | dt = None) -> None:
        """Set the system to a mode, either indefinitely, or for a set time."""
        await self._set_status(mode, until=until)

    async def set_status_normal(self) -> None:
        """Set the system into normal mode."""
        await self._set_status("Auto")

    async def set_status_reset(self) -> None:
        """Reset the system into normal mode (and all zones to FollowSchedule mode)."""
        await self._set_status("AutoWithReset")

    async def set_status_custom(self, /, *, until: None | dt = None) -> None:
        """Set the system into custom mode."""
        await self._set_status("Custom", until=until)

    async def set_status_eco(self, /, *, until: None | dt = None) -> None:
        """Set the system into eco mode."""
        await self._set_status("AutoWithEco", until=until)

    async def set_status_away(self, /, *, until: None | dt = None) -> None:
        """Set the system into away mode."""
        await self._set_status("Away", until=until)

    async def set_status_dayoff(self, /, *, until: None | dt = None) -> None:
        """Set the system into dayoff mode."""
        await self._set_status("DayOff", until=until)

    async def set_status_heatingoff(self, /, *, until: None | dt = None) -> None:
        """Set the system into heating off mode."""
        await self._set_status("HeatingOff", until=until)

    async def temperatures(self) -> list[dict]:
        """Return the current zone temperatures and setpoints."""

        await self.location.status()

        result = []

        if self.hotwater:
            dhw_status = {
                "thermostat": "DOMESTIC_HOT_WATER",
                "id": self.hotwater.dhwId,
                "name": "",
                "temp": self.hotwater.temperatureStatus["temperature"],
                "setpoint": "",
            }

            result.append(dhw_status)

        for zone in self._zones:
            zone_status = {
                "thermostat": "EMEA_ZONE",
                "id": zone.zoneId,
                "name": zone.name,
                "temp": None,
                "setpoint": zone.setpointStatus["targetHeatTemperature"],
            }

            if zone.temperatureStatus["isAvailable"]:
                zone_status["temp"] = zone.temperatureStatus["temperature"]

            result.append(zone_status)

        return result

    async def zone_schedules_backup(self, filename: _FilePathT) -> None:
        """Backup all zones on control system to the given file."""

        _LOGGER.info(
            f"Backing up schedules from {self.systemId} ({self.location.name})..."
        )

        schedules = {}

        if self.hotwater:
            _LOGGER.info(f"Retrieving DHW schedule: {self.hotwater.zoneId}...")

            schedule = await self.hotwater.schedule()
            schedules[self.hotwater.zoneId] = {
                "name": "Domestic Hot Water",
                "schedule": schedule,
            }

        for zone in self._zones:
            zone_id = zone.zoneId
            name = zone.name

            _LOGGER.info(f"Retrieving Zone schedule: {zone_id} - {name}")

            schedule = await zone.schedule()
            schedules[zone_id] = {"name": name, "schedule": schedule}

        _LOGGER.info(f"Writing to backup file: {filename}...")
        with open(filename, "w") as file_output:
            file_output.write(json.dumps(schedules, indent=4))

        _LOGGER.info("Backup completed.")

    async def zone_schedules_restore(self, filename: _FilePathT) -> None:
        """Restore all zones on control system from the given file."""

        _LOGGER.info(f"Restoring schedules to {self.systemId} ({self.location})...")

        _LOGGER.info(f"Reading from backup file: {filename}...")
        with open(filename, "r") as file_input:
            schedule_db = file_input.read()
            schedules = json.loads(schedule_db)

            for zone_id, zone_schedule in schedules.items():
                name = zone_schedule["name"]
                zone_info = zone_schedule["schedule"]

                _LOGGER.info(f"Restoring schedule for: {zone_id} - {name}...")

                if self.hotwater and self.hotwater.zoneId == zone_id:
                    await self.hotwater.set_schedule(json.dumps(zone_info))
                else:
                    await self.zones_by_id[zone_id].set_schedule(json.dumps(zone_info))

        _LOGGER.info("Restore completed.")
