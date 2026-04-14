# Python Logging

Source: https://sciwiki.fredhutch.org/compdemos/python_logging/

## Overview

Python's built-in `logging` module for structured log management in applications, batch processes, and remote services.

## Log Levels

DEBUG (10), INFO (20), WARNING (30), ERROR (40), CRITICAL (50)

## Basic Pattern

```python
import logging

logger = logging.getLogger('new_logger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info('Hello world!')
```

## Components

- **Logger**: `logging.getLogger('name')`, manages messages at specified severity
- **Handlers**: StreamHandler (console), FileHandler (files)
- **Formatters**: Structure output with `%(asctime)s`, `%(lineno)s`, `%(funcName)s`
- **Filters**: Control message propagation through logger hierarchies

## AWS Integration

Logs auto-route to CloudWatch in Lambda, EC2, ECS, and Batch. WatchTower library consolidates multi-service logs.

## Best Practice

Log early and log often, particularly for remote API calls, request data, and state checkpoints.
