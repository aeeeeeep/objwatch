# file: objwatch/utils/weak.py:18-40
# asked: {"lines": [18, 24, 26, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40], "branches": [[30, 31], [30, 32], [36, 0], [36, 37], [39, 0], [39, 40]]}
# gained: {"lines": [18, 24, 26, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40], "branches": [[30, 31], [30, 32], [36, 0], [36, 37], [39, 0], [39, 40]]}

import pytest
from weakref import ref
from objwatch.utils.weak import _IterationGuard


class MockWeakContainer:
    def __init__(self):
        self._iterating = set()
        self._commit_removals_called = False

    def _commit_removals(self):
        self._commit_removals_called = True


def test_iteration_guard_context_manager():
    """Test _IterationGuard context manager functionality."""
    container = MockWeakContainer()
    guard = _IterationGuard(container)

    # Test __enter__ adds self to container's _iterating set
    with guard:
        assert guard in container._iterating

    # Test __exit__ removes self from container's _iterating set
    assert guard not in container._iterating
    # _commit_removals should be called when set becomes empty
    assert container._commit_removals_called


def test_iteration_guard_multiple_guards():
    """Test _IterationGuard with multiple guards in container."""
    container = MockWeakContainer()
    guard1 = _IterationGuard(container)
    guard2 = _IterationGuard(container)

    # Enter first guard
    with guard1:
        assert guard1 in container._iterating
        assert len(container._iterating) == 1
        assert not container._commit_removals_called

        # Enter second guard
        with guard2:
            assert guard2 in container._iterating
            assert len(container._iterating) == 2
            assert not container._commit_removals_called

        # After exiting second guard, first guard should still be there
        assert guard1 in container._iterating
        assert guard2 not in container._iterating
        assert len(container._iterating) == 1
        assert not container._commit_removals_called

    # After exiting first guard, set should be empty and _commit_removals called
    assert len(container._iterating) == 0
    assert container._commit_removals_called


def test_iteration_guard_with_none_container():
    """Test _IterationGuard when weakcontainer becomes None."""
    container = MockWeakContainer()
    guard = _IterationGuard(container)

    # Simulate container being garbage collected
    weak_ref = guard.weakcontainer
    del container

    # Context manager should handle None container gracefully
    with guard:
        # __enter__ should handle None container
        pass

    # __exit__ should handle None container
    assert not hasattr(guard, '_iterating') or guard not in getattr(guard, '_iterating', set())
