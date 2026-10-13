from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from weather_logic import make_recommendation


def sample_weather(**overrides):
    weather = {
        "temperature": 12.0, "feels_like": 11.0, "wind": 8.0, "gusts": 15.0,
        "precipitation": 0.0, "rain": 0.0, "showers": 0.0, "snowfall": 0.0,
        "code": 1, "time": "2026-10-13T07:00",
    }
    weather.update(overrides)
    return weather


def test_comfortable_weather():
    verdict, clothing = make_recommendation(sample_weather())
    assert "комфортні" in verdict
    assert clothing


def test_heavy_precipitation_recommends_indoor():
    verdict, _ = make_recommendation(sample_weather(precipitation=3.0))
    assert "приміщенні" in verdict


def test_extreme_heat_recommends_caution():
    verdict, _ = make_recommendation(sample_weather(temperature=32.0))
    assert "обережністю" in verdict or "приміщенні" in verdict


def test_windy_weather_adds_windproof_layer():
    _, clothing = make_recommendation(sample_weather(wind=22.0, gusts=35.0))
    assert "вітрозахисний" in clothing
