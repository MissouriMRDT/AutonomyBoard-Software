# logging

<b>A quick tutorial</b>

Correct usage
```python3
import logging
# Initialize at module scope for easy use
logger = logging.getLogger(__name__)

def func():
    logger.info()
```

Incorrect usage
```python3
import logging

# Pollutes namespace. 
logger = logging.getLogger("whatever_name_you_want")

# Causes duplicate messages
logger.addHandler(logging.StreamHandler())

# Not the right logger
logging.info("message")
```
Using the `__name__` variable guarantees that every module (ie. any file with a .py extension) gets its own unique logger. Choosing your own name pollutes the logger namespace. If another module calls `logging.getLogger("whatever_name_you_want")` The same logger object will be returned.

Unless you have a really good reason to do so, do not attach any handlers to module loggers. All log records will be propagated back up to the root logger. Adding your own handlers may cause duplicate logs. In `run.py` we've attached the appropriate handlers. The logging level can be specified like so...
```
$ python3 run.py --level=DEBUG
```
If you wish to call the file directly, setup the root logger by attaching handlers. Optionally you can specify a formatter.
```
import logging

# Module logger
logger = logging.getLogger(__name__)

# Module code
...
...

if __name__ == "__main__":
    # Get the root logger
    rootlog = logging.getLogger()
    
    # Set the level
    rootlog.setLevel(logging.INFO)
    
    # Add a handler that prints to stdout
    rootlog.addHandler(logging.StreamHandler())

    # Call main function or do whatever
    main()
```