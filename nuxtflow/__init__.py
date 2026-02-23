"""
NuxtFlow - Extract __NUXT_DATA__ from Nuxt.js applications using Playwright.

Simple usage:

    from nuxtflow import extract_nuxt_data
    data = extract_nuxt_data("https://example-nuxt-app.com")

With navigation steps:

    from nuxtflow import NuxtDataExtractor, NavigationStep
    async with NuxtDataExtractor() as extractor:
        steps = [
            NavigationStep.click("button[data-tab='products']"),
            NavigationStep.wait("div.products-loaded"),
        ]
        data = await extractor.extract("https://shop.example.com", steps=steps)
"""

from nuxtflow.exceptions import (
    BrowserError,
    DataParsingError,
    ExtractionTimeout,
    NavigationStepFailed,
    NuxtDataNotFound,
    NuxtFlowException,
    ProxyError,
)
from nuxtflow.extractor import NuxtDataExtractor, extract_nuxt_data
from nuxtflow.parser import parse_nuxt_json
from nuxtflow.steps import NavigationStep, StepType, execute_step, execute_steps
from nuxtflow.utils import StealthConfig
from nuxtflow.anti_detection.delays import human_delay
from nuxtflow.anti_detection.mouse_movement import simulate_mouse_movement
from nuxtflow.anti_detection.typing import human_type
from nuxtflow.anti_detection.user_agents import get_realistic_user_agent, REALISTIC_USER_AGENTS
from nuxtflow.anti_detection.viewports import get_random_viewport, REALISTIC_VIEWPORTS
from nuxtflow.anti_detection.stealth_scripts import STEALTH_SCRIPTS

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

__version__ = "0.2.0"
