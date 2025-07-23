from typing import Any

from fastmcp import FastMCP

from insights_mcp_core.client import InsightsClient


class InsightsMCP(FastMCP):
    def __init__(
        self,
        name: str = "Red Hat Insights",
        refresh_token: str | None = None,
        instructions: str | None = None,
        **settings: Any,
    ):
        super().__init__(name=name, instructions=instructions, **settings)
        self.refresh_token = refresh_token
        self.insights_client = None

    def init_insights_client(self, refresh_token: str | None = None):
        refresh_token = refresh_token or self.refresh_token
        if refresh_token is None:
            raise ValueError(
                "refresh_token is required, get token from https://access.redhat.com/management/api"
            )
        self.insights_client = InsightsClient(refresh_token)
