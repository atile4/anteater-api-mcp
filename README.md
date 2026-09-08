# Anteater API MCP

An MCP wrapper for Anteater API. Currently in development.

## Local Setup

### Prerequisites

- Python 3.12+
- uv package manager
- Node.js 18+

### Running Locally

Git clone into your local machine

```
git clone https://github.com/atile4/anteater-api-mcp.git
```

Paste into `claude_desktop_config.json`

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

To start the server, run:

```
uv run python -m anteater_api_mcp
```

## Disclaimer

All data is sourced from ICSSC's [Anteater API](https://github.com/icssc/anteater-api). Data retrieved from may not be 100% accurate, make sure to double-check for important information.

This project has no affiliation with Anteater API.
