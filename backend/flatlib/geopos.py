# Mock flatlib GeoPos

class GeoPos:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f"GeoPos({self.lat}, {self.lon})"
