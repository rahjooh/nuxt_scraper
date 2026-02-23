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
)
from nuxtflow.extractor import NuxtDataExtractor, extract_nuxt_data
from nuxtflow.parser import parse_nuxt_json
from nuxtflow.steps import NavigationStep, StepType, execute_step, execute_steps

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
]

__version__ = "0.1.0"
