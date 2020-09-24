import threading
import logging
import asyncio
import collections
import functools
from typing import (
    Callable,
    Any,
    List,
    Optional,
    Hashable,
)
# Static type checker aliases
EventHandler = Callable[[Any], None]
SignalFunc = Callable[[str], None]
StartFunc = Callable[[SignalFunc], None]

# Module level logger
logger = logging.getLogger(__name__)

class RoverEvent:

    def __init__(self,
            start: StartFunc,
            lock: Optional[asyncio.Lock] = None,
            loop:Optional[asyncio.AbstractEventLoop] = None
    )->None:
        loop = asyncio.get_event_loop() if loop is None else loop
        lock = asyncio.Lock() if lock is None else lock
        self._name = start.__name__
        self._loop = loop
        self._lock = lock
        self._cond = collections.defaultdict(lambda: asyncio.Condition(lock))
        self._args = collections.defaultdict(lambda: None)
        self._dispatchers = {}
        self._handlers = collections.defaultdict(list)
        
        # Synchronize access to the underlying condition between all events
        # registered to this event.
        signal_lock = asyncio.Lock()
        async def signal(key, args=None):
            async with signal_lock:
                self._args[key] = args
                async with self._cond[key]:            
                    # Wake up handlers
                    self._cond[key].notify()

        # The thread worker must accept at least one argument: A function that 
        # when called notifies the handlers associated with [key] and an argument
        # that will be passed to the event handler.
        self._thread = threading.Thread(
            target=start,
            args=(
                lambda key, args: asyncio.run_coroutine_threadsafe(signal(key,args), loop), 
        ))

    def add_event_handler(self, 
            event: Hashable,
            handler: Callable[[Any], None]
    ) -> Callable[[], None]:
        """Add a handler for event."""

        def handler_wrapper():
            # Calls handler with the 2nd argument of 'signal()'
            handler(self._args[event])

        if event not in self._dispatchers:
            # Create the task object if it doesn't exist
            task = self._loop.create_task(self._event_dispatcher(event))
            self._dispatchers[event] = task

            # If the handler raises an exception we want to know about it.
            task.add_done_callback(on_handler_exception)
        
        # Add the wrapper to list of handlers we want to call when the event is
        # broadcast.
        self._handlers[event].append(handler_wrapper)
        
        # Use this value to remove handler
        return handler_wrapper


    def get_event_dispatcher(self,
            event: Hashable,
    )-> asyncio.Task:
        """Get the asyncio.Task object associated with the event."""
        return self._dispatchers[event]


    def remove_event_handler(self, 
            event: Hashable,
            handler: Callable[[], None]
    ) -> None:
        """Remove the [handler] associated with [event]. The handler argument
        must be the same as the return value of add_event_handler()."""
        self._handlers[event].remove(handler)


    async def _event_dispatcher(self, key):
        while True:
            async with self._cond[key]:
                await self._cond[key].wait()
                logger.debug(f"Handling event '{key}'")
                for handler in self._handlers[key]:
                    handler()


    def start(self):
        logger.info(f"Start {self._thread}: {self._name}")
        self._thread.start()
    

    def __str__(self):
        return f"{type(self).__name__}:{self._name}"


    @classmethod
    def Thread(cls, *args, **kwargs) -> Callable:
        """Returns a decorator that wraps a threaded event emitter."""
        def wrapper(worker: StartFunc) -> cls:
            return cls(worker, *args, **kwargs)
        return wrapper
        

def on_handler_exception(self, task: asyncio.Task) -> None:
    # asyncio tasks do not propagate exceptions. A handler must be registered
    # to handle an exception.
    if task.exception() is not None:
        logger.exception(task.exception())