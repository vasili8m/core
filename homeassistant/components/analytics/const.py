"""Constants for the analytics integration."""
import logging
from enum import Enum
from datetime import timedelta

ANALYTICS_ENPOINT_URL = "https://updater.home-assistant.io/"
DOMAIN = "analytics"
INTERVAL = timedelta(days=1)
STORAGE_KEY = "core.analytics"
STORAGE_VERSION = 1


LOGGER: logging.Logger = logging.getLogger(__package__)


ATTR_AUTOMATION_COUNT = "automation_count"
ATTR_COMPONENTS = "components"
ATTR_CUSTOM_INTEGRATIONS = "custom_integrations"
ATTR_HUUID = "huuid"
ATTR_INSTALLATION_TYPE = "installation_type"
ATTR_INTEGRATION_COUNT = "integration_count"
ATTR_PREFERENCES = "preferences"
ATTR_STATE_COUNT = "state_count"
ATTR_USER_COUNT = "user_count"
ATTR_VERSION = "version"


class AnalyticsPreference(str, Enum):
    """Analytics prefrences."""

    BASE = "base"
    INTEGRATIONS = "integrations"
    STATISTICS = "statistics"
