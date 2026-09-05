# Anteater API MCP

An MCP wrapper for Anteater API

## Running Locally

Paste this into `claude_desktop_config.json` mcpServers

```
  "mcpServers": {
    "anteater-api-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\attic\\gitrepos\\anteater-api-mcp",
        "run",
        "anteater-api-mcp"
      ]
    }
  }
```

`uv run python -m anteater_api_mcp`

## Disclaimer

All data is sourced from ICSSC's [Anteater API](https://github.com/icssc/anteater-api), which states that data retrieved from official sources may not be accurate.

This project has no affiliation with Anteater API.
