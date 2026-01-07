EMERGENCY_NUMBERS = [
    x.strip() for x in os.getenv("EMERGENCY_NUMBERS", "").split(",") if x.strip()
]
