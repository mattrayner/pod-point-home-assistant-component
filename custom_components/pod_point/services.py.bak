"""Services for the Pod Point integration."""
from __future__ import annotations

from typing import cast

# from python_picnic_api import PicnicAPI
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .const import (
    # ATTR_AMOUNT,
    # ATTR_CONFIG_ENTRY_ID,
    # ATTR_PRODUCT_ID,
    # ATTR_PRODUCT_IDENTIFIERS,
    # ATTR_PRODUCT_NAME,
    # CONF_API,
    DOMAIN,
    SERVICE_SET_CHARGE_MODE,
)


class PodPointServiceException(Exception):
    """Exception for Picnic services."""


async def async_register_services(hass: HomeAssistant) -> None:
    """Register services for the Pod Point integration, if not registered yet."""

    if hass.services.has_service(DOMAIN, SERVICE_SET_CHARGE_MODE):
        return

    async def async_add_product_service(call: ServiceCall):
        api_client = await get_api_client(hass, call.data["foo"])
        await handle_add_product(hass, api_client, call)

        coordinator = hass.data[DOMAIN][call.data["entry_id"]]



    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_CHARGE_MODE,
        async_add_product_service,
        schema=vol.Schema(
            {
                vol.Required("config_entry_id"): cv.string_with_no_html
            }
        ),
    )


async def get_api_client(hass: HomeAssistant, config_entry_id: str) -> PicnicAPI:
    """Get the right Picnic API client based on the device id, else get the default one."""
    if config_entry_id not in hass.data[DOMAIN]:
        raise ValueError(f"Config entry with id {config_entry_id} not found!")
    return hass.data[DOMAIN][config_entry_id][CONF_API]


async def handle_add_product(
    hass: HomeAssistant, api_client: PicnicAPI, call: ServiceCall
) -> None:
    """Handle the call for the add_product service."""
    product_id = call.data.get("product_id")
    if not product_id:
        product_id = await hass.async_add_executor_job(
            _product_search, api_client, cast(str, call.data["product_name"])
        )

    if not product_id:
        raise PicnicServiceException("No product found or no product ID given!")

    await hass.async_add_executor_job(
        api_client.add_product, str(product_id), call.data.get("amount", 1)
    )


def _product_search(api_client: PicnicAPI, product_name: str) -> None | str:
    """Query the api client for the product name."""
    search_result = api_client.search(product_name)

    if not search_result or "items" not in search_result[0]:
        return None

    # Return the first valid result
    for item in search_result[0]["items"]:
        if "name" in item:
            return str(item["id"])

    return None