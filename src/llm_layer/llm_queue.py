"""
LLM Call Queue: Rate-limit-aware FIFO queue for LLM API calls.
Failed items are re-queued to the back, giving natural backoff as other items
process first. Caps total attempts per item to avoid infinite loops.
"""

import time
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Tuple


class LLMQueue:
    """
    A FIFO queue that processes LLM calls with controlled pacing.
    Failed items go to the back of the queue instead of blocking with retries.
    """

    def __init__(
        self,
        delay_between_calls: float = 0.5,
        max_attempts: int = 3,
    ):
        self.delay = delay_between_calls
        self.max_attempts = max_attempts
        self._queue: deque = deque()
        self._results: Dict[str, Any] = {}
        self._attempts: Dict[str, int] = {}

    def enqueue(self, item_id: str, call_fn: Callable[[], Optional[Any]], item_data: Any = None):
        """Add a work item. call_fn should return a result on success or None on failure."""
        self._queue.append((item_id, call_fn, item_data))
        self._attempts.setdefault(item_id, 0)

    def process_all(
        self,
        on_success: Optional[Callable[[str, Any, Any], None]] = None,
        on_failure: Optional[Callable[[str, Any], None]] = None,
    ) -> Dict[str, Any]:
        """
        Process the queue until empty or all items have exhausted attempts.
        on_success(item_id, result, item_data) — called on successful LLM response.
        on_failure(item_id, item_data) — called when max attempts exhausted.
        Returns dict of {item_id: result} for successful items.
        """
        total = len(self._queue)
        completed = 0

        while self._queue:
            item_id, call_fn, item_data = self._queue.popleft()
            self._attempts[item_id] += 1
            attempt = self._attempts[item_id]

            print(f"    [Queue] Processing {item_id} (attempt {attempt}/{self.max_attempts})...")

            try:
                result = call_fn()
            except Exception as e:
                print(f"    [Queue] {item_id} raised exception: {e}")
                result = None

            if result is not None:
                self._results[item_id] = result
                completed += 1
                if on_success:
                    on_success(item_id, result, item_data)
            elif attempt < self.max_attempts:
                # Re-queue to back — other items process first (natural backoff)
                print(f"    [Queue] {item_id} failed, re-queuing ({attempt}/{self.max_attempts}).")
                self._queue.append((item_id, call_fn, item_data))
            else:
                print(f"    [Queue] {item_id} exhausted all {self.max_attempts} attempts.")
                if on_failure:
                    on_failure(item_id, item_data)

            # Pace calls to avoid rate limits
            if self._queue:
                time.sleep(self.delay)

        print(f"    [Queue] Complete: {completed}/{total} items succeeded.")
        return self._results
