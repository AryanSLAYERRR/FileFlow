import threading
import queue
from typing import Callable, Iterable, Any, Optional

class Cancelled(Exception):
    pass

class StreamWorker:
    def __init__(self, target: Callable[[], Iterable[Any]], out_q: queue.Queue, cancel_event: threading.Event):
        self._target = target
        self._out_q = out_q
        self._cancel = cancel_event
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        try:
            for item in self._target():
                if self._cancel.is_set():
                    raise Cancelled()
                while True:
                    if self._cancel.is_set():
                        raise Cancelled()
                    try:
                        self._out_q.put(item, timeout=0.1)
                        break
                    except queue.Full:
                        continue
        except Cancelled:
            pass
        except Exception as e:
            try:
                self._out_q.put(("__ERROR__", str(e)))
            except Exception:
                pass
        finally:
            try:
                self._out_q.put(None)
            except Exception:
                pass

class ApplyWorker:
    def __init__(self, preview_iter_fn: Callable[[], Iterable[Any]], apply_fn: Callable[[Iterable[Any]], None],
                 cancel_event: threading.Event, progress_cb: Optional[Callable[[str], None]] = None):
        self._iter_fn = preview_iter_fn
        self._apply_fn = apply_fn
        self._cancel = cancel_event
        self._progress_cb = progress_cb
        self._thread: Optional[threading.Thread] = None
        self.done_event = threading.Event()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        try:
            def cancellable_iter():
                for item in self._iter_fn():
                    if self._cancel.is_set():
                        break
                    yield item
            if self._progress_cb:
                self._progress_cb("[Worker] Apply started")
            self._apply_fn(cancellable_iter())
            if self._progress_cb:
                self._progress_cb("[Worker] Apply finished")
        except Exception as e:
            if self._progress_cb:
                self._progress_cb(f"[Worker ERROR] {e}")
        finally:
            self.done_event.set()
