import json
from typing import Any, Dict
from urllib import request, error


class MCPClient:
    def __init__(self, base_url: str, timeout_s: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def run_tool(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/tool/{name}"
        body = json.dumps({"payload": payload}).encode("utf-8")
        req = request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with request.urlopen(req, timeout=self.timeout_s) as resp:
                data = resp.read().decode("utf-8")
                return json.loads(data)
        except error.HTTPError as exc:
            return {
                "status": "error",
                "detail": {"message": "HTTP error from MCP server", "code": exc.code},
            }
        except Exception as exc:  # noqa: BLE001 - keep minimal for MVP
            return {
                "status": "error",
                "detail": {"message": "Failed to call MCP server", "error": str(exc)},
            }
