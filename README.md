# here_transit

Asynchronous Python client for the HERE Transit V8 API

[![GitHub Actions](https://github.com/eifinger/here_transit/workflows/CI/badge.svg)](https://github.com/eifinger/here_transit/actions?workflow=CI)
[![PyPi](https://img.shields.io/pypi/v/here_transit.svg)](https://pypi.python.org/pypi/here_transit)
[![PyPi](https://img.shields.io/pypi/l/here_transit.svg)](https://github.com/eifinger/here_transit/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/eifinger/here_transit/branch/master/graph/badge.svg)](https://codecov.io/gh/eifinger/here_transit)
[![Downloads](https://pepy.tech/badge/here_transit)](https://pepy.tech/project/here_transit)

## Installation

```bash
pip install here_transit
```

## Usage

```python
import asyncio

from here_transit import HERETransitApi, Place, Return

API_KEY = "<YOUR_API_KEY>"


async def main() -> None:
    """Show example how to get location of your tracker."""
    async with HERETransitApi(api_key=API_KEY) as here_transit:
        response = await here_transit.route(
            origin=Place(latitude=50.12778680095556, longitude=8.582081794738771),
            destination=Place(latitude=50.060940891421765, longitude=8.336477279663088),
            return_values=[Return.TRAVEL_SUMMARY],
        )
        print(
            f"Duration is: {response['routes'][0]['sections'][0]['travelSummary']['duration']}"
        )


if __name__ == "__main__":
    asyncio.run(main())
```
