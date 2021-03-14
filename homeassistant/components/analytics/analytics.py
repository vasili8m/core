"""Analytics helper class for the analytics integration."""
import asyncio
from typing import List

import aiohttp
import async_timeout

from homeassistant.components.api import ATTR_INSTALLATION_TYPE
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.system_info import async_get_system_info
from homeassistant.loader import DATA_INTEGRATIONS, Integration

from .const import (
    ANALYTICS_ENPOINT_URL,
    AnalyticsPreference,
    ATTR_AUTOMATION_COUNT,
    ATTR_COMPONENTS,
    ATTR_CUSTOM_INTEGRATIONS,
    ATTR_HUUID,
    ATTR_INTEGRATION_COUNT,
    ATTR_STATE_COUNT,
    ATTR_USER_COUNT,
    ATTR_VERSION,
    LOGGER,
    STORAGE_KEY,
    STORAGE_VERSION,
)


class Analytics:
    """Analytics helper class for the analytics integration."""

    def __init__(self, hass: HomeAssistant, huuid: str) -> None:
        """Initialize the Analytics class."""
        self.hass: HomeAssistant = hass
        self.huuid = huuid
        self.session = async_get_clientsession(hass)
        self.store: Store = hass.helpers.storage.Store(STORAGE_VERSION, STORAGE_KEY)
        self._preferences: List[AnalyticsPreference] = []

    @property
    def preferences(self) -> List[AnalyticsPreference]:
        """Return the current active preferences."""
        return self._preferences

    async def load_preferences(self) -> None:
        """Load preferences."""
        self._preferences = await self.store.async_load() or []
        LOGGER.debug("Loaded preferences: %s", self.preferences)

    async def save_preferences(self, preferences: List[AnalyticsPreference]) -> None:
        """Load preferences."""
        self._preferences = preferences
        await self.store.async_save(self._preferences)

    async def send_analytics(self, _=None) -> None:
        """Send analytics."""

        if AnalyticsPreference.BASE not in self.preferences:
            LOGGER.debug("Nothing to submit %s", self.preferences)
            return

        system_info = await async_get_system_info(self.hass)
        payload: dict = {
            ATTR_HUUID: self.huuid,
            ATTR_VERSION: HA_VERSION,
            ATTR_INSTALLATION_TYPE: system_info[ATTR_INSTALLATION_TYPE],
        }

        if AnalyticsPreference.INTEGRATIONS in self.preferences:
            integrations, custom_integrations = get_integrations(self.hass)
            payload[ATTR_COMPONENTS] = integrations
            payload[ATTR_CUSTOM_INTEGRATIONS] = custom_integrations

        if AnalyticsPreference.STATISTICS in self.preferences:
            integrations, _ = get_integrations(self.hass)
            payload[ATTR_STATE_COUNT] = len(self.hass.states.async_all())
            payload[ATTR_AUTOMATION_COUNT] = len(
                self.hass.states.async_all("automation")
            )
            payload[ATTR_INTEGRATION_COUNT] = len(integrations)
            payload[ATTR_USER_COUNT] = len(
                [
                    user
                    for user in await self.hass.auth.async_get_users()
                    if not user.system_generated
                ]
            )

        try:
            with async_timeout.timeout(30):
                response = await self.session.post(ANALYTICS_ENPOINT_URL, json=payload)
                if response.status == 200:
                    LOGGER.info(
                        (
                            "Submitted analytics to Home Assistant servers. "
                            "Information submitted includes %s"
                        ),
                        payload,
                    )
                else:
                    LOGGER.warning(
                        "Sending analytics failed with statuscode %s", response.status
                    )
        except asyncio.TimeoutError:
            LOGGER.error("Timeout sending analytics to %s", ANALYTICS_ENPOINT_URL)
        except aiohttp.ClientError as err:
            LOGGER.error(
                "Error sending analytics to %s: %r", ANALYTICS_ENPOINT_URL, err
            )


def get_integrations(hass: HomeAssistant) -> List[str]:
    """Return a list of loaded core integrations."""
    custom_integrations = False
    integrations = []

    for entry in hass.data[DATA_INTEGRATIONS]:
        integration = hass.data[DATA_INTEGRATIONS][entry]
        if not isinstance(integration, Integration):
            continue
        if integration.is_built_in:
            integrations.append(integration.domain)
        else:
            custom_integrations = True

    return integrations, custom_integrations
