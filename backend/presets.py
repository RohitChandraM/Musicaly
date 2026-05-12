"""
Preset configurations for the Vocal Humanizer AI.
"""

PRESETS = {
    "natural": {
        "hp_freq": 100, "hp_order": 2,
        "body_freq": 200, "body_gain_db": 1.5, "body_q": 0.8,
        "mud_freq": 450, "mud_gain_db": -2.0, "mud_q": 1.2,
        "nasal_freq": 1000, "nasal_gain_db": -1.5, "nasal_q": 1.5,
        "presence_freq": 3500, "presence_gain_db": -1.0, "presence_q": 1.0,
        "harsh_freq": 3500, "harsh_q": 1.2, "harsh_threshold_db": -18.0, "harsh_reduction_db": 3.0,
        "dess_freq": 6500, "dess_q": 1.5, "dess_threshold_db": -20.0, "dess_reduction_db": 2.5,
        "sat_drive": 1.1, "sat_mix": 0.05,
        "reverb_room_size": 0.10, "reverb_damping": 0.8, "reverb_wet_level": 0.03, "reverb_dry_level": 1.0,
        "air_freq": 10000, "air_gain_db": 0.0,
    },
    "warm": {
        "hp_freq": 80, "hp_order": 2,
        "body_freq": 220, "body_gain_db": 3.5, "body_q": 0.7,
        "mud_freq": 400, "mud_gain_db": -3.5, "mud_q": 1.0,
        "nasal_freq": 900, "nasal_gain_db": -2.5, "nasal_q": 1.2,
        "presence_freq": 3000, "presence_gain_db": -2.0, "presence_q": 0.9,
        "harsh_freq": 3200, "harsh_q": 1.0, "harsh_threshold_db": -20.0, "harsh_reduction_db": 5.0,
        "dess_freq": 6000, "dess_q": 1.4, "dess_threshold_db": -22.0, "dess_reduction_db": 4.0,
        "sat_drive": 1.3, "sat_mix": 0.12,
        "reverb_room_size": 0.20, "reverb_damping": 0.7, "reverb_wet_level": 0.07, "reverb_dry_level": 1.0,
        "air_freq": 9000, "air_gain_db": -2.0,
    },
    "rap_punchy": {
        "hp_freq": 120, "hp_order": 4,
        "body_freq": 180, "body_gain_db": 2.0, "body_q": 1.0,
        "mud_freq": 500, "mud_gain_db": -4.0, "mud_q": 1.4,
        "nasal_freq": 1200, "nasal_gain_db": -2.0, "nasal_q": 1.8,
        "presence_freq": 4000, "presence_gain_db": -2.5, "presence_q": 1.2,
        "harsh_freq": 4000, "harsh_q": 1.3, "harsh_threshold_db": -16.0, "harsh_reduction_db": 6.0,
        "dess_freq": 7000, "dess_q": 1.6, "dess_threshold_db": -18.0, "dess_reduction_db": 6.0,
        "sat_drive": 1.2, "sat_mix": 0.08,
        "reverb_room_size": 0.05, "reverb_damping": 0.95, "reverb_wet_level": 0.02, "reverb_dry_level": 1.0,
        "air_freq": 12000, "air_gain_db": 1.5,
    },
}


def get_preset(name: str) -> dict:
    return PRESETS.get(name, PRESETS["natural"])


def scale_preset(preset: dict, strength: float) -> dict:
    scaled = dict(preset)
    for key in ("body_gain_db", "mud_gain_db", "nasal_gain_db", "presence_gain_db",
                "harsh_reduction_db", "dess_reduction_db", "air_gain_db"):
        scaled[key] = preset[key] * strength
    drive_delta = preset["sat_drive"] - 1.0
    scaled["sat_drive"] = 1.0 + drive_delta * strength
    scaled["sat_mix"] = preset["sat_mix"] * strength
    scaled["reverb_wet_level"] = preset["reverb_wet_level"] * strength
    return scaled
