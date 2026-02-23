"""Tests for NuxtFlow navigation steps."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from nuxtflow.exceptions import NavigationStepFailed
from nuxtflow.steps import (
    NavigationStep,
    StepType,
    execute_step,
    execute_steps,
)
from nuxtflow.utils import StealthConfig

# Mock anti-detection functions globally for these tests unless specifically testing them
@pytest.fixture(autouse=True)
def mock_anti_detection_functions():
    with (
        patch('nuxtflow.anti_detection.delays.human_delay', new_callable=AsyncMock) as mock_delay,
        patch('nuxtflow.anti_detection.mouse_movement.simulate_mouse_movement', new_callable=AsyncMock) as mock_mouse_move,
        patch('nuxtflow.anti_detection.typing.human_type', new_callable=AsyncMock) as mock_human_type,
    ):
        yield mock_delay, mock_mouse_move, mock_human_type


class TestNavigationStepFactoryMethods:
    def test_click_creates_correct_step(self) -> None:
        step = NavigationStep.click("button#ok", timeout=2000)
        assert step.type == StepType.CLICK
        assert step.selector == "button#ok"
        assert step.timeout == 2000
        assert step.value is None

    def test_fill_creates_correct_step(self) -> None:
        step = NavigationStep.fill("input[name=q]", "hello")
        assert step.type == StepType.FILL
        assert step.selector == "input[name=q]"
        assert step.value == "hello"

    def test_select_creates_correct_step(self) -> None:
        step = NavigationStep.select("select#country", "US")
        assert step.type == StepType.SELECT
        assert step.value == "US"

    def test_wait_creates_correct_step(self) -> None:
        step = NavigationStep.wait("div.loaded", timeout=15000)
        assert step.type == StepType.WAIT
        assert step.timeout == 15000

    def test_scroll_creates_correct_step(self) -> None:
        step = NavigationStep.scroll("footer")
        assert step.type == StepType.SCROLL

    def test_hover_creates_correct_step(self) -> None:
        step = NavigationStep.hover("nav .menu")
        assert step.type == StepType.HOVER


@pytest.mark.asyncio
class TestExecuteStep:
    async def test_click_step_calls_page_click_with_default_stealth(
        self, mock_page: object, mock_anti_detection_functions
    ) -> None:
        mock_delay, mock_mouse_move, _ = mock_anti_detection_functions
        step = NavigationStep.click("button.go")
        await execute_step(mock_page, step, StealthConfig(mouse_movement=True))
        mock_page.wait_for_selector.assert_called_once_with("button.go", timeout=5000)
        mock_page.click.assert_called_once_with("button.go", timeout=5000)
        mock_delay.assert_called()
        mock_mouse_move.assert_called_once()

    async def test_click_step_calls_page_click_without_stealth(
        self, mock_page: object, mock_anti_detection_functions
    ) -> None:
        mock_delay, mock_mouse_move, _ = mock_anti_detection_functions
        step = NavigationStep.click("button.go")
        await execute_step(mock_page, step, StealthConfig(enabled=False))
        mock_page.wait_for_selector.assert_called_once_with("button.go", timeout=5000)
        mock_page.click.assert_called_once_with("button.go", timeout=5000)
        mock_delay.assert_not_called()
        mock_mouse_move.assert_not_called()

    async def test_fill_step_calls_human_type_with_stealth(
        self, mock_page: object, mock_anti_detection_functions
    ) -> None:
        mock_delay, _, mock_human_type = mock_anti_detection_functions
        step = NavigationStep.fill("input#q", "test")
        await execute_step(mock_page, step, StealthConfig(human_typing=True))
        mock_page.wait_for_selector.assert_called_once_with("input#q", timeout=5000)
        mock_human_type.assert_called_once()
        mock_delay.assert_called()

    async def test_fill_step_calls_page_fill_without_human_typing(
        self, mock_page: object, mock_anti_detection_functions
    ) -> None:
        mock_delay, _, mock_human_type = mock_anti_detection_functions
        step = NavigationStep.fill("input#q", "test")
        await execute_step(mock_page, step, StealthConfig(human_typing=False))
        mock_page.wait_for_selector.assert_called_once_with("input#q", timeout=5000)
        mock_page.fill.assert_called_once_with("input#q", "test", timeout=5000)
        mock_human_type.assert_not_called()
        mock_delay.assert_called() # Delays are still active if stealth_config.enabled is True

    async def test_wait_step_only_waits_for_selector(self, mock_page: object, mock_anti_detection_functions) -> None:
        mock_delay, mock_mouse_move, mock_human_type = mock_anti_detection_functions
        step = NavigationStep.wait("div.ready", timeout=8000)
        await execute_step(mock_page, step, StealthConfig())
        mock_page.wait_for_selector.assert_called_once_with("div.ready", timeout=8000)
        mock_delay.assert_called()
        mock_mouse_move.assert_not_called()
        mock_human_type.assert_not_called()

    async def test_step_failure_raises_navigation_step_failed(
        self, mock_page: object, mock_anti_detection_functions
    ) -> None:
        mock_page.wait_for_selector.side_effect = TimeoutError("Element not found")
        step = NavigationStep.click("button.missing")
        with pytest.raises(NavigationStepFailed) as exc_info:
            await execute_step(mock_page, step, StealthConfig())
        assert exc_info.value.step == step
        assert isinstance(exc_info.value.original_error, TimeoutError)


@pytest.mark.asyncio
async def test_execute_steps_runs_all_steps_with_stealth(
    self, mock_page: object, mock_anti_detection_functions
) -> None:
    mock_delay, mock_mouse_move, mock_human_type = mock_anti_detection_functions
    steps = [
        NavigationStep.click("button.a"),
        NavigationStep.fill("input.b", "value"),
    ]
    await execute_steps(mock_page, steps, StealthConfig(mouse_movement=True, human_typing=True))
    assert mock_page.wait_for_selector.call_count >= 2
    mock_page.click.assert_called_once()
    mock_human_type.assert_called_once()
    assert mock_delay.call_count >= 4 # 2 before, 2 after actions for 2 steps
    mock_mouse_move.assert_called_once()


@pytest.mark.asyncio
async def test_execute_steps_runs_all_steps_without_stealth(
    self, mock_page: object, mock_anti_detection_functions
) -> None:
    mock_delay, mock_mouse_move, mock_human_type = mock_anti_detection_functions
    steps = [
        NavigationStep.click("button.a"),
        NavigationStep.fill("input.b", "value"),
    ]
    await execute_steps(mock_page, steps, StealthConfig(enabled=False))
    assert mock_page.wait_for_selector.call_count >= 2
    mock_page.click.assert_called_once()
    mock_page.fill.assert_called_once()
    mock_delay.assert_not_called()
    mock_mouse_move.assert_not_called()
    mock_human_type.assert_not_called()
