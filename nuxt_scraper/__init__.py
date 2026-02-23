"""
Nuxt Scraper - Extract __NUXT_DATA__ from Nuxt.js applications using Playwright.

Simple usage:

    from nuxt_scraper import extract_nuxt_data
    data = extract_nuxt_data("https://example-nuxt-app.com")

With navigation steps:

    from nuxt_scraper import NuxtDataExtractor, NavigationStep
    async with NuxtDataExtractor() as extractor:
        steps = [
            NavigationStep.click("button[data-tab='products']"),
            NavigationStep.wait("div.products-loaded"),
        ]
        data = await extractor.extract("https://shop.example.com", steps=steps)
"""

from nuxt_scraper.exceptions import (
    BrowserError,
    DataParsingError,
    DateNotFoundInCalendarError,
    ExtractionTimeout,
    NavigationStepFailed,
    NuxtDataNotFound,
    NuxtFlowException,
    ProxyError,
)
from nuxt_scraper.extractor import NuxtDataExtractor, extract_nuxt_data
from nuxt_scraper.parser import parse_nuxt_json
from nuxt_scraper.steps import NavigationStep, StepType, execute_step, execute_steps
from nuxt_scraper.utils import StealthConfig
from nuxt_scraper.anti_detection.delays import human_delay
from nuxt_scraper.anti_detection.mouse_movement import simulate_mouse_movement
from nuxt_scraper.anti_detection.typing import human_type
from nuxt_scraper.anti_detection.user_agents import (
    get_realistic_user_agent,
    REALISTIC_USER_AGENTS,
)
from nuxt_scraper.anti_detection.viewports import (
    get_random_viewport,
    REALISTIC_VIEWPORTS,
)
from nuxt_scraper.anti_detection.stealth_scripts import STEALTH_SCRIPTS

__all__ = [
    "NuxtDataExtractor",
    "extract_nuxt_data",
    "NavigationStep",
    "StepType",
    "execute_step",
    "execute_steps",
    "parse_nuxt_json",
    "NuxtFlowException",
    "NuxtDataNotFound",
    "NavigationStepFailed",
    "ExtractionTimeout",
    "DataParsingError",
    "BrowserError",
    "ProxyError",
    "DateNotFoundInCalendarError",
    "StealthConfig",
    "human_delay",
    "simulate_mouse_movement",
    "human_type",
    "get_realistic_user_agent",
    "REALISTIC_USER_AGENTS",
    "get_random_viewport",
    "REALISTIC_VIEWPORTS",
    "STEALTH_SCRIPTS",
]

__version__ = "0.2.2"
