# file: objwatch/tracer.py:442-460
# asked: {"lines": [442, 449, 450, 452, 453, 454, 455, 456, 457, 458, 459, 460], "branches": [[449, 0], [449, 450], [452, 0], [452, 453], [454, 455], [454, 456], [456, 457], [456, 458], [458, 0], [458, 459], [459, 458], [459, 460]]}
# gained: {"lines": [442, 449, 450, 452, 453, 454, 455, 456, 457, 458, 459, 460], "branches": [[449, 0], [449, 450], [452, 0], [452, 453], [454, 455], [454, 456], [456, 457], [456, 458], [458, 0], [458, 459], [459, 458], [459, 460]]}

import pytest
from unittest.mock import Mock
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestObject:
    def __init__(self):
        self.list_attr = [1, 2, 3]
        self.dict_attr = {'a': 1, 'b': 2}
        self.tuple_attr = (1, 2, 3)
        self.set_attr = {1, 2, 3}
        self.non_sequence_attr = "string"
        self.callable_attr = lambda x: x + 1


class TestObjectNoDict:
    """Test object without __dict__ attribute"""

    __slots__ = ['attr1', 'attr2']


class TestObjectNoWeakref:
    """Test object without __weakref__ in class"""

    pass


# Remove __weakref__ from TestObjectNoWeakref class
if hasattr(TestObjectNoWeakref, '__weakref__'):
    delattr(TestObjectNoWeakref, '__weakref__')


def create_mock_frame(locals_dict):
    """Create a mock frame object for testing"""
    frame = Mock()
    frame.f_locals = locals_dict
    return frame


def test_update_objects_lens_with_sequence_types():
    """Test _update_objects_lens with object containing sequence types"""
    config = ObjWatchConfig(targets=['__main__'], with_locals=True, with_globals=True)
    tracer = Tracer(config)

    test_obj = TestObject()
    frame = create_mock_frame({'self': test_obj})

    # Call the method
    tracer._update_objects_lens(frame)

    # Verify object is tracked
    assert test_obj in tracer.tracked_objects
    assert test_obj in tracer.tracked_objects_lens

    # Verify attributes are stored correctly
    tracked_attrs = tracer.tracked_objects[test_obj]
    assert 'list_attr' in tracked_attrs
    assert 'dict_attr' in tracked_attrs
    assert 'tuple_attr' in tracked_attrs
    assert 'set_attr' in tracked_attrs
    assert 'non_sequence_attr' in tracked_attrs
    assert 'callable_attr' not in tracked_attrs  # Callables should be filtered out

    # Verify sequence lengths are tracked
    lens_dict = tracer.tracked_objects_lens[test_obj]
    assert lens_dict['list_attr'] == 3
    assert lens_dict['dict_attr'] == 2
    assert lens_dict['tuple_attr'] == 3
    assert lens_dict['set_attr'] == 3
    assert 'non_sequence_attr' not in lens_dict  # Non-sequence should not have length tracked


def test_update_objects_lens_no_self_in_locals():
    """Test _update_objects_lens when 'self' is not in frame locals"""
    config = ObjWatchConfig(targets=['__main__'], with_locals=True, with_globals=True)
    tracer = Tracer(config)

    frame = create_mock_frame({})  # No 'self' in locals

    # Call the method - should not raise any exceptions
    tracer._update_objects_lens(frame)

    # Verify no objects were tracked
    assert len(tracer.tracked_objects) == 0
    assert len(tracer.tracked_objects_lens) == 0


def test_update_objects_lens_object_no_dict():
    """Test _update_objects_lens with object that has no __dict__ attribute"""
    config = ObjWatchConfig(targets=['__main__'], with_locals=True, with_globals=True)
    tracer = Tracer(config)

    test_obj = TestObjectNoDict()
    test_obj.attr1 = "value1"
    test_obj.attr2 = "value2"

    frame = create_mock_frame({'self': test_obj})

    # Call the method
    tracer._update_objects_lens(frame)

    # Verify object is not tracked (no __dict__)
    assert test_obj not in tracer.tracked_objects
    assert test_obj not in tracer.tracked_objects_lens


def test_update_objects_lens_object_no_weakref():
    """Test _update_objects_lens with object whose class has no __weakref__"""
    config = ObjWatchConfig(targets=['__main__'], with_locals=True, with_globals=True)
    tracer = Tracer(config)

    test_obj = TestObjectNoWeakref()
    test_obj.some_attr = [1, 2, 3]

    frame = create_mock_frame({'self': test_obj})

    # Call the method
    tracer._update_objects_lens(frame)

    # Verify object is not tracked (no __weakref__ in class)
    assert test_obj not in tracer.tracked_objects
    assert test_obj not in tracer.tracked_objects_lens


def test_update_objects_lens_multiple_calls_same_object():
    """Test _update_objects_lens called multiple times on same object"""
    config = ObjWatchConfig(targets=['__main__'], with_locals=True, with_globals=True)
    tracer = Tracer(config)

    test_obj = TestObject()
    frame = create_mock_frame({'self': test_obj})

    # First call
    tracer._update_objects_lens(frame)

    # Modify sequence attributes
    test_obj.list_attr.append(4)
    test_obj.dict_attr['c'] = 3

    # Second call
    tracer._update_objects_lens(frame)

    # Verify lengths are updated
    lens_dict = tracer.tracked_objects_lens[test_obj]
    assert lens_dict['list_attr'] == 4
    assert lens_dict['dict_attr'] == 3


def test_update_objects_lens_empty_sequences():
    """Test _update_objects_lens with empty sequence types"""
    config = ObjWatchConfig(targets=['__main__'], with_locals=True, with_globals=True)
    tracer = Tracer(config)

    class EmptySequences:
        def __init__(self):
            self.empty_list = []
            self.empty_dict = {}
            self.empty_tuple = ()
            self.empty_set = set()

    test_obj = EmptySequences()
    frame = create_mock_frame({'self': test_obj})

    tracer._update_objects_lens(frame)

    # Verify empty sequences are tracked with length 0
    lens_dict = tracer.tracked_objects_lens[test_obj]
    assert lens_dict['empty_list'] == 0
    assert lens_dict['empty_dict'] == 0
    assert lens_dict['empty_tuple'] == 0
    assert lens_dict['empty_set'] == 0
