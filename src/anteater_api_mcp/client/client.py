import requests
from typing import Optional

# Models
from anteater_api_mcp.client.models import Major

BASE_URL = "https://anteaterapi.com/v2/rest/"

class AnteaterAPIError(Exception):
    pass

class Client:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self._session = requests.Session()

    def _get(self, path:str, params:dict) -> dict:
        params = {k: v for k, v in params.items() if v is not None}

        try:
            resp = self._session.get(self.base_url + path, params=params)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise AnteaterAPIError(f"Request to Anteater API failed: {e}") from e

        response = resp.json()
        if not response.get("ok"):
            raise AnteaterAPIError(response.get("message", "Unknown error from Anteater API"))

        return response["data"]

    def get_courses(
        self,
        department: str = None,
        school: str = None,
        course_level: str = None,
        ge_category: str = None,
        take: int = 10
    ) -> list[dict]:
        return self._get("courses", {
            "department": department,
            "school": school,
            "courseLevel": course_level,
            "geCategory": ge_category,
            "take": take
        })


    def get_majors(self) -> list[Major]:
        return self._get("programs/majors", {})
    

client = Client()