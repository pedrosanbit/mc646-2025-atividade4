import pytest
from datetime import datetime
from src.energy.DeviceSchedule import DeviceSchedule


class TestDeviceSchedule:
    """Test suite for the DeviceSchedule class."""
    
    def test_device_schedule_initialization(self):
        """Test that DeviceSchedule can be initialized with device name and scheduled time."""
        # Arrange
        device_name = "Smart Thermostat"
        scheduled_time = datetime(2025, 10, 2, 14, 30, 0)
        
        # Act
        device_schedule = DeviceSchedule(device_name, scheduled_time)
        
        # Assert
        assert device_schedule.device_name == device_name
        assert device_schedule.scheduled_time == scheduled_time
    
    def test_device_schedule_repr(self):
        """Test the string representation of DeviceSchedule."""
        # Arrange
        device_name = "LED Light"
        scheduled_time = datetime(2025, 10, 2, 18, 0, 0)
        device_schedule = DeviceSchedule(device_name, scheduled_time)
        
        # Act
        repr_string = repr(device_schedule)
        
        # Assert
        expected_repr = f"DeviceSchedule(device_name='LED Light', scheduled_time='{scheduled_time}')"
        assert repr_string == expected_repr
    