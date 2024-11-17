import pytest
from unittest import mock
from datetime import datetime, timedelta
from your_module import check_availability, schedule_meeting_event, check_group_availability

# Helper function to mock the calendar service API
def mock_calendar_service():
    service_mock = mock.Mock()
    
    # Mock the 'events().list()' method of the calendar service
    events_mock = mock.Mock()
    
    # Simulate when there are no events for availability check (free time)
    events_mock.execute.return_value = {'items': []}
    
    # Simulate when there are events for availability check (busy time)
    busy_events_mock = mock.Mock()
    busy_events_mock.execute.return_value = {'items': [{'summary': 'Existing Meeting'}]}
    
    service_mock.events.return_value.list.return_value = events_mock  # Free time
    service_mock.events.return_value.list.return_value = busy_events_mock  # Busy time

    return service_mock

# Test for check_availability
def test_check_availability_free_time():
    # Arrange
    calendar_service = mock_calendar_service()
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=1)
    
    # Act
    result = check_availability("test@domain.com", start_time, end_time)
    
    # Assert
    assert result is True  # No events, should be available

def test_check_availability_busy_time():
    # Arrange
    calendar_service = mock_calendar_service()
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=1)
    
    # Act
    result = check_availability("test@domain.com", start_time, end_time)
    
    # Assert
    assert result is False  # There is an existing meeting, should be unavailable

# Test for schedule_meeting_event
def test_schedule_meeting_event():
    # Arrange
    calendar_service = mock_calendar_service()
    calendar_ids = ["user1@domain.com", "user2@domain.com"]
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=1)
    
    event_mock = mock.Mock()
    event_mock.execute.return_value = {"id": "event1234", "status": "confirmed"}
    
    calendar_service.events.return_value.insert.return_value = event_mock

    # Act
    created_event = schedule_meeting_event(calendar_ids, start_time, end_time)
    
    # Assert
    assert created_event['status'] == 'confirmed'
    assert created_event['id'] == 'event1234'

# Test for check_group_availability
def test_check_group_availability_all_available():
    # Arrange
    calendar_service = mock_calendar_service()
    group_members = ["user1@domain.com", "user2@domain.com"]
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=1)
    
    # Act
    result = check_group_availability(group_members, start_time, end_time)
    
    # Assert
    assert result is True  # All members are available

def test_check_group_availability_one_unavailable():
    # Arrange
    calendar_service = mock_calendar_service()
    group_members = ["user1@domain.com", "user2@domain.com"]
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=1)
    
    # Mock the second user as unavailable
    calendar_service.events.return_value.list.return_value.execute.return_value = {'items': [{'summary': 'Existing Meeting'}]}  # Simulating a busy calendar for user2
    
    # Act
    result = check_group_availability(group_members, start_time, end_time)
    
    # Assert
    assert result is False  # Not all members are available
