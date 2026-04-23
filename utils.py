COUNTRY_ID_TO_NAME = {
    "NG": "Nigeria", "AO": "Angola", "KE": "Kenya",
    "BJ": "Benin", "GH": "Ghana", "ZA": "South Africa",
    "US": "United States", "GB": "United Kingdom"
}

COUNTRY_NAME_TO_ID = {v.lower(): k for k, v in COUNTRY_ID_TO_NAME.items()}
COUNTRY_NAME_TO_ID.update({
    "nigeria": "NG", "usa": "US", "uk": "GB"
})

VALID_SORT_COLS = {"age", "created_at", "gender_probability"}
VALID_AGE_GROUPS = {"child", "teenager", "adult", "senior"}
VALID_GENDERS = {"male", "female"}


def age_to_group(age: int) -> str:
    if age <= 12: return "child"
    if age <= 19: return "teenager"
    if age <= 59: return "adult"
    return "senior"