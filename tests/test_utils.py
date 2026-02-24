"""Tests for utility functions and configurations."""

from __future__ import annotations

import pytest

from nuxt_scraper.utils import StealthConfig


class TestStealthConfig:
    """Test StealthConfig dataclass and its functionality."""
    
    def test_default_stealth_config(self) -> None:
        """Test default StealthConfig values."""
        config = StealthConfig()
        
        assert config.enabled is True
        assert config.random_delays is True
        assert config.min_action_delay_ms == 100
        assert config.max_action_delay_ms == 1000
        assert config.human_typing is True
        assert config.typing_speed_wpm == 60
        assert config.typo_chance == 0.02
        assert config.pause_chance == 0.05
        assert config.mouse_movement is True
        assert config.randomize_viewport is True
        assert config.realistic_user_agent is True
    
    def test_custom_stealth_config(self) -> None:
        """Test custom StealthConfig values."""
        config = StealthConfig(
            enabled=False,
            random_delays=False,
            min_action_delay_ms=200,
            max_action_delay_ms=2000,
            human_typing=False,
            typing_speed_wpm=45,
            typo_chance=0.05,
            pause_chance=0.10,
            mouse_movement=False,
            randomize_viewport=False,
            realistic_user_agent=False
        )
        
        assert config.enabled is False
        assert config.random_delays is False
        assert config.min_action_delay_ms == 200
        assert config.max_action_delay_ms == 2000
        assert config.human_typing is False
        assert config.typing_speed_wpm == 45
        assert config.typo_chance == 0.05
        assert config.pause_chance == 0.10
        assert config.mouse_movement is False
        assert config.randomize_viewport is False
        assert config.realistic_user_agent is False
    
    def test_stealth_config_validation(self) -> None:
        """Test StealthConfig validation."""
        # Test valid configurations
        config1 = StealthConfig(typing_speed_wpm=30)
        assert config1.typing_speed_wpm == 30
        
        config2 = StealthConfig(typo_chance=0.0)
        assert config2.typo_chance == 0.0
        
        config3 = StealthConfig(typo_chance=1.0)
        assert config3.typo_chance == 1.0
        
        # Test delay ranges
        config4 = StealthConfig(min_action_delay_ms=500, max_action_delay_ms=1500)
        assert config4.min_action_delay_ms == 500
        assert config4.max_action_delay_ms == 1500
    
    def test_stealth_config_equality(self) -> None:
        """Test StealthConfig equality comparison."""
        config1 = StealthConfig()
        config2 = StealthConfig()
        config3 = StealthConfig(enabled=False)
        
        assert config1 == config2
        assert config1 != config3
    
    def test_stealth_config_repr(self) -> None:
        """Test StealthConfig string representation."""
        config = StealthConfig(enabled=False, random_delays=False)
        repr_str = repr(config)
        
        assert "StealthConfig" in repr_str
        assert "enabled=False" in repr_str
        assert "random_delays=False" in repr_str
    
    def test_stealth_config_partial_override(self) -> None:
        """Test partial override of StealthConfig values."""
        # Start with defaults
        config = StealthConfig()
        
        # Override specific values
        custom_config = StealthConfig(
            typing_speed_wpm=40,
            mouse_movement=False
        )
        
        # Check that only specified values changed
        assert custom_config.typing_speed_wpm == 40
        assert custom_config.mouse_movement is False
        
        # Check that other values remain default
        assert custom_config.enabled is True
        assert custom_config.random_delays is True
        assert custom_config.human_typing is True
        assert custom_config.randomize_viewport is True
    
    def test_stealth_config_performance_vs_stealth_presets(self) -> None:
        """Test common stealth configuration presets."""
        # Fast/minimal stealth
        fast_config = StealthConfig(
            random_delays=False,
            human_typing=False,
            mouse_movement=False,
            randomize_viewport=False,
            realistic_user_agent=False
        )
        
        assert fast_config.random_delays is False
        assert fast_config.human_typing is False
        assert fast_config.mouse_movement is False
        
        # Balanced stealth
        balanced_config = StealthConfig(
            min_action_delay_ms=200,
            max_action_delay_ms=800,
            typing_speed_wpm=80,
            mouse_movement=False
        )
        
        assert balanced_config.min_action_delay_ms == 200
        assert balanced_config.max_action_delay_ms == 800
        assert balanced_config.typing_speed_wpm == 80
        assert balanced_config.mouse_movement is False
        assert balanced_config.human_typing is True  # Still enabled
        
        # Maximum stealth
        max_stealth_config = StealthConfig(
            min_action_delay_ms=1000,
            max_action_delay_ms=3000,
            typing_speed_wpm=35,
            typo_chance=0.08,
            pause_chance=0.15
        )
        
        assert max_stealth_config.min_action_delay_ms == 1000
        assert max_stealth_config.max_action_delay_ms == 3000
        assert max_stealth_config.typing_speed_wpm == 35
        assert max_stealth_config.typo_chance == 0.08
        assert max_stealth_config.pause_chance == 0.15


class TestConfigurationIntegration:
    """Test integration between different configuration components."""
    
    def test_stealth_config_with_extractor_options(self) -> None:
        """Test StealthConfig integration with extractor options."""
        from nuxt_scraper.extractor import NuxtDataExtractor
        
        stealth_config = StealthConfig(
            random_delays=True,
            human_typing=True,
            mouse_movement=False
        )
        
        # Test that extractor accepts the config
        extractor = NuxtDataExtractor(
            headless=True,
            timeout=30000,
            stealth_config=stealth_config
        )
        
        assert extractor.stealth_config == stealth_config
        assert extractor.stealth_config.random_delays is True
        assert extractor.stealth_config.human_typing is True
        assert extractor.stealth_config.mouse_movement is False
    
    def test_default_stealth_config_with_extractor(self) -> None:
        """Test default StealthConfig with extractor."""
        from nuxt_scraper.extractor import NuxtDataExtractor
        
        extractor = NuxtDataExtractor()
        
        # Should have default stealth config
        assert isinstance(extractor.stealth_config, StealthConfig)
        assert extractor.stealth_config.enabled is True
        assert extractor.stealth_config.random_delays is True
        assert extractor.stealth_config.human_typing is True
    
    def test_disabled_stealth_config(self) -> None:
        """Test completely disabled stealth configuration."""
        from nuxt_scraper.extractor import NuxtDataExtractor
        
        disabled_config = StealthConfig(enabled=False)
        extractor = NuxtDataExtractor(stealth_config=disabled_config)
        
        assert extractor.stealth_config.enabled is False
        # Other settings should still be available for selective enabling
        assert extractor.stealth_config.random_delays is True  # Default value
        assert extractor.stealth_config.human_typing is True   # Default value


class TestConfigurationValidation:
    """Test configuration validation and error handling."""
    
    def test_stealth_config_boundary_values(self) -> None:
        """Test StealthConfig with boundary values."""
        # Test minimum values
        config_min = StealthConfig(
            min_action_delay_ms=0,
            max_action_delay_ms=1,
            typing_speed_wpm=1,
            typo_chance=0.0,
            pause_chance=0.0
        )
        
        assert config_min.min_action_delay_ms == 0
        assert config_min.max_action_delay_ms == 1
        assert config_min.typing_speed_wpm == 1
        assert config_min.typo_chance == 0.0
        assert config_min.pause_chance == 0.0
        
        # Test maximum reasonable values
        config_max = StealthConfig(
            min_action_delay_ms=5000,
            max_action_delay_ms=10000,
            typing_speed_wpm=200,
            typo_chance=1.0,
            pause_chance=1.0
        )
        
        assert config_max.min_action_delay_ms == 5000
        assert config_max.max_action_delay_ms == 10000
        assert config_max.typing_speed_wpm == 200
        assert config_max.typo_chance == 1.0
        assert config_max.pause_chance == 1.0
    
    def test_stealth_config_logical_consistency(self) -> None:
        """Test logical consistency of StealthConfig values."""
        # Test that min_delay <= max_delay is not enforced at creation
        # (This is handled at runtime in the delay functions)
        config = StealthConfig(
            min_action_delay_ms=1000,
            max_action_delay_ms=500  # Intentionally backwards
        )
        
        # Should still create the config (validation happens at usage time)
        assert config.min_action_delay_ms == 1000
        assert config.max_action_delay_ms == 500
    
    def test_stealth_config_immutability(self) -> None:
        """Test that StealthConfig behaves as expected with dataclass."""
        config1 = StealthConfig(typing_speed_wpm=50)
        config2 = StealthConfig(typing_speed_wpm=50)
        
        # Should be equal but not the same object
        assert config1 == config2
        assert config1 is not config2
        
        # Should be able to create new instances with modifications
        config3 = StealthConfig(
            enabled=config1.enabled,
            random_delays=config1.random_delays,
            typing_speed_wpm=100  # Different value
        )
        
        assert config3.typing_speed_wpm == 100
        assert config1.typing_speed_wpm == 50  # Original unchanged


class TestValidateMeetingDate:
    """Test validate_meeting_date utility function."""
    
    def test_validate_meeting_date_iso_format(self) -> None:
        """Test validation with ISO datetime format (YYYY-MM-DDTHH:MM:SS.000Z)."""
        from nuxt_scraper.utils import validate_meeting_date
        
        # API response format with ISO datetime
        api_data = {
            "data": {
                "meetingsGrouped": [
                    {
                        "meetings": [
                            {
                                "meetingDateLocal": "2025-02-20T00:00:00.000Z",
                                "name": "Test Meeting"
                            }
                        ]
                    }
                ]
            }
        }
        
        # Should match despite time component
        assert validate_meeting_date(api_data, "2025-02-20") is True
        
        # Should not match different date
        assert validate_meeting_date(api_data, "2025-02-21") is False
    
    def test_validate_meeting_date_simple_format(self) -> None:
        """Test validation with simple date format (YYYY-MM-DD)."""
        from nuxt_scraper.utils import validate_meeting_date
        
        # API response format with simple date
        api_data = {
            "data": {
                "meetingsGrouped": [
                    {
                        "meetings": [
                            {
                                "meetingDateLocal": "2025-02-20",
                                "name": "Test Meeting"
                            }
                        ]
                    }
                ]
            }
        }
        
        assert validate_meeting_date(api_data, "2025-02-20") is True
        assert validate_meeting_date(api_data, "2025-02-21") is False
    
    def test_validate_meeting_date_nuxt_format(self) -> None:
        """Test validation with __NUXT__ data structure."""
        from nuxt_scraper.utils import validate_meeting_date
        
        # __NUXT__ format
        nuxt_data = {
            "data": [
                {
                    "meetings": [
                        {
                            "meetings": [
                                {
                                    "meetingDateLocal": "2025-02-20",
                                    "name": "Test Meeting"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        assert validate_meeting_date(nuxt_data, "2025-02-20") is True
        assert validate_meeting_date(nuxt_data, "2025-02-21") is False
    
    def test_validate_meeting_date_custom_field(self) -> None:
        """Test validation with custom date field name."""
        from nuxt_scraper.utils import validate_meeting_date
        
        # API response with custom date field
        api_data = {
            "data": {
                "meetingsGrouped": [
                    {
                        "meetings": [
                            {
                                "customDateField": "2025-02-20T00:00:00.000Z",
                                "name": "Test Meeting"
                            }
                        ]
                    }
                ]
            }
        }
        
        # Should fail with default field name
        assert validate_meeting_date(api_data, "2025-02-20") is False
        
        # Should succeed with custom field name
        assert validate_meeting_date(api_data, "2025-02-20", date_field="customDateField") is True
    
    def test_validate_meeting_date_empty_data(self) -> None:
        """Test validation with empty or invalid data."""
        from nuxt_scraper.utils import validate_meeting_date
        
        # Empty dict
        assert validate_meeting_date({}, "2025-02-20") is False
        
        # Missing data key
        assert validate_meeting_date({"other": "value"}, "2025-02-20") is False
        
        # Empty meetings
        empty_api_data = {
            "data": {
                "meetingsGrouped": []
            }
        }
        assert validate_meeting_date(empty_api_data, "2025-02-20") is False
        
        # Empty __NUXT__ data
        empty_nuxt_data = {
            "data": []
        }
        assert validate_meeting_date(empty_nuxt_data, "2025-02-20") is False
    
    def test_validate_meeting_date_malformed_data(self) -> None:
        """Test validation with malformed data structures."""
        from nuxt_scraper.utils import validate_meeting_date
        
        # Malformed API data
        malformed_api = {
            "data": {
                "meetingsGrouped": [
                    {
                        "meetings": "not a list"  # Should be a list
                    }
                ]
            }
        }
        assert validate_meeting_date(malformed_api, "2025-02-20") is False
        
        # Malformed __NUXT__ data
        malformed_nuxt = {
            "data": "not a list"  # Should be a list
        }
        assert validate_meeting_date(malformed_nuxt, "2025-02-20") is False
    
    def test_validate_meeting_date_multiple_meetings(self) -> None:
        """Test validation with multiple meetings (should check first)."""
        from nuxt_scraper.utils import validate_meeting_date
        
        # Multiple meetings, first one matches
        api_data = {
            "data": {
                "meetingsGrouped": [
                    {
                        "meetings": [
                            {"meetingDateLocal": "2025-02-20", "name": "Meeting 1"},
                            {"meetingDateLocal": "2025-02-21", "name": "Meeting 2"},
                        ]
                    }
                ]
            }
        }
        
        # Should validate against first meeting
        assert validate_meeting_date(api_data, "2025-02-20") is True
        assert validate_meeting_date(api_data, "2025-02-21") is False
    
    def test_validate_meeting_date_different_iso_formats(self) -> None:
        """Test validation with different ISO datetime variations."""
        from nuxt_scraper.utils import validate_meeting_date
        
        # Test various ISO formats
        iso_formats = [
            "2025-02-20T00:00:00.000Z",
            "2025-02-20T12:30:45.123Z",
            "2025-02-20T23:59:59.999Z",
        ]
        
        for iso_date in iso_formats:
            api_data = {
                "data": {
                    "meetingsGrouped": [
                        {
                            "meetings": [
                                {"meetingDateLocal": iso_date, "name": "Test"}
                            ]
                        }
                    ]
                }
            }
            
            # All should match the date part
            assert validate_meeting_date(api_data, "2025-02-20") is True
    
    def test_validate_meeting_date_exception_handling(self) -> None:
        """Test that validation handles exceptions gracefully."""
        from nuxt_scraper.utils import validate_meeting_date
        
        # None input
        assert validate_meeting_date(None, "2025-02-20") is False
        
        # Non-dict input
        assert validate_meeting_date("not a dict", "2025-02-20") is False
        assert validate_meeting_date(123, "2025-02-20") is False
        assert validate_meeting_date([], "2025-02-20") is False