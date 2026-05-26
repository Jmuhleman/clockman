from app.config.settings import DEFAULT_SESSION_TIMES, TIME_INTERVAL_MINUTES
from app.utils.time_options import generate_time_options


def test_generate_time_options_interval() -> None:
    options = generate_time_options(TIME_INTERVAL_MINUTES)
    assert options[0] == "00:00"
    assert options[1] == "00:15"
    assert "23:45" in options


def test_default_times_in_options() -> None:
    options = generate_time_options(TIME_INTERVAL_MINUTES)
    for session in DEFAULT_SESSION_TIMES.values():
        assert session["check_in"] in options
        assert session["check_out"] in options
