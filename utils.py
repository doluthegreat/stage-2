COUNTRY_ID_TO_NAME = {
    "NG": "Nigeria",        "AO": "Angola",          "KE": "Kenya",
    "BJ": "Benin",          "GH": "Ghana",           "ZA": "South Africa",
    "EG": "Egypt",          "ET": "Ethiopia",        "TZ": "Tanzania",
    "UG": "Uganda",         "SN": "Senegal",         "CM": "Cameroon",
    "CI": "Côte d'Ivoire",  "ML": "Mali",            "BF": "Burkina Faso",
    "NE": "Niger",          "TD": "Chad",            "SD": "Sudan",
    "SO": "Somalia",        "MZ": "Mozambique",      "MG": "Madagascar",
    "ZM": "Zambia",         "ZW": "Zimbabwe",        "MW": "Malawi",
    "RW": "Rwanda",         "BI": "Burundi",         "TG": "Togo",
    "SL": "Sierra Leone",   "LR": "Liberia",         "GN": "Guinea",
    "GW": "Guinea-Bissau",  "GM": "Gambia",          "MR": "Mauritania",
    "MA": "Morocco",        "DZ": "Algeria",         "TN": "Tunisia",
    "LY": "Libya",          "CG": "Republic of the Congo", "CD": "DR Congo",
    "GA": "Gabon",          "GQ": "Equatorial Guinea","CF": "Central African Republic",
    "SS": "South Sudan",    "ER": "Eritrea",         "DJ": "Djibouti",
    "KM": "Comoros",        "CV": "Cabo Verde",      "ST": "São Tomé and Príncipe",
    "SC": "Seychelles",     "MU": "Mauritius",       "BW": "Botswana",
    "NA": "Namibia",        "LS": "Lesotho",         "SZ": "Eswatini",
    "EH": "Western Sahara", "US": "United States",   "GB": "United Kingdom",
    "FR": "France",         "DE": "Germany",         "IT": "Italy",
    "ES": "Spain",          "PT": "Portugal",        "BR": "Brazil",
    "IN": "India",          "CN": "China",           "JP": "Japan",
    "RU": "Russia",         "CA": "Canada",          "AU": "Australia",
    "MX": "Mexico",         "AR": "Argentina",       "CO": "Colombia",
    "VE": "Venezuela",      "PE": "Peru",            "CL": "Chile",
    "ID": "Indonesia",      "PK": "Pakistan",        "BD": "Bangladesh",
    "PH": "Philippines",    "VN": "Vietnam",         "TH": "Thailand",
    "MY": "Malaysia",       "SG": "Singapore",       "TR": "Turkey",
    "IR": "Iran",           "IQ": "Iraq",            "SA": "Saudi Arabia",
    "AE": "United Arab Emirates", "IL": "Israel",    "KR": "South Korea",
    "SE": "Sweden",         "NO": "Norway",          "DK": "Denmark",
    "FI": "Finland",        "NL": "Netherlands",     "BE": "Belgium",
    "CH": "Switzerland",    "AT": "Austria",         "PL": "Poland",
    "UA": "Ukraine",        "RO": "Romania",         "GR": "Greece",
    "NZ": "New Zealand",
}

COUNTRY_NAME_TO_ID = {name.lower(): code for code, name in COUNTRY_ID_TO_NAME.items()}
# Extra aliases
COUNTRY_NAME_TO_ID.update({
    "nigeria": "NG", "angola": "AO", "kenya": "KE", "benin": "BJ",
    "ghana": "GH", "south africa": "ZA", "egypt": "EG", "ethiopia": "ET",
    "ivory coast": "CI", "cote d'ivoire": "CI", "drc": "CD",
    "democratic republic of congo": "CD", "republic of the congo": "CG",
    "usa": "US", "america": "US", "uk": "GB", "england": "GB",
    "uae": "AE", "united arab emirates": "AE",
    "united states": "US", "united kingdom": "GB",
    "cape verde": "CV", "korea": "KR", "south korea": "KR",
    "swaziland": "SZ", "western sahara": "EH",
    "sao tome and principe": "ST", "equatorial guinea": "GQ",
    "central african republic": "CF", "south sudan": "SS",
    "sierra leone": "SL", "guinea-bissau": "GW", "burkina faso": "BF",
    "dr congo": "CD", "congo": "CG",
})

VALID_GENDERS   = {"male", "female"}
VALID_AGE_GROUPS = {"child", "teenager", "adult", "senior"}
VALID_SORT_COLS  = {"age", "created_at", "gender_probability"}


def age_to_group(age: int) -> str:
    if age <= 12:  return "child"
    if age <= 19:  return "teenager"
    if age <= 59:  return "adult"
    return "senior"