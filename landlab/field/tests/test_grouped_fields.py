#! /usr/bin/env python

from nose.tools import assert_true, assert_false, assert_raises
try:
    from nose.tools import assert_is_not, assert_is, assert_set_equal, assert_dict_equal
except ImportError:
    from landlab.testing.tools import (assert_is_not, assert_is, assert_set_equal,
                                       assert_dict_equal)
import numpy as np
from numpy.testing import assert_array_equal

from landlab.field import ModelDataFields, GroupError, FieldError


def test_init():
    fields = ModelDataFields()
    assert_set_equal(set(), fields.groups)


def test_new_field_location():
    fields = ModelDataFields()
    fields.new_field_location('node', 12)
    assert_set_equal(set(['node']), fields.groups)


def test_add_existing_group():
    fields = ModelDataFields()
    fields.new_field_location('node', size=12)
    assert_raises(ValueError, fields.new_field_location, 'node', size=24)


def test_add_multiple_groups():
    fields = ModelDataFields()
    fields.new_field_location('node', 12)
    fields.new_field_location('cell', 2)
    fields.new_field_location('face', 7)
    fields.new_field_location('link', 7)
    assert_set_equal(set(['node', 'cell', 'face', 'link']), fields.groups)


def test_ones():
    fields = ModelDataFields()
    fields.new_field_location('node', 12)
    fields.new_field_location('cell', 2)

    value_array = fields.ones('node')
    assert_array_equal(np.ones(12), value_array)

    value_array = fields.ones('cell')
    assert_array_equal(np.ones(2), value_array)


def test_add_ones():
    fields = ModelDataFields()
    fields.new_field_location('node', 12)
    fields.new_field_location('cell', 2)

    fields.add_ones('node', 'z')
    assert_array_equal(np.ones(12), fields['node']['z'])
    assert_array_equal(np.ones(12), fields.field_values('node', 'z'))

    fields.add_ones('cell', 'z')
    assert_array_equal(np.ones(2), fields['cell']['z'])
    assert_array_equal(np.ones(2), fields.field_values('cell', 'z'))


def test_add_ones_return_value():
    fields = ModelDataFields()
    fields.new_field_location('node', 12)
    fields.new_field_location('cell', 2)

    rtn_value = fields.add_ones('node', 'z')
    assert_array_equal(rtn_value, np.ones(12))
    assert_is(rtn_value, fields['node']['z'])
    assert_is(rtn_value, fields.field_values('node', 'z'))

    rtn_value = fields.add_ones('cell', 'z')
    assert_array_equal(rtn_value, np.ones(2))
    assert_is(rtn_value, fields['cell']['z'])
    assert_is(rtn_value, fields.field_values('cell', 'z'))


def test_add_existing_field_default():
    """Test default is to replace existing field."""
    fields = ModelDataFields()
    fields.new_field_location('node', 12)

    assert_is_not(fields.add_empty('node', 'z'), fields.add_empty('node', 'z'))
    assert_is_not(fields.add_ones('node', 'z'), fields.add_ones('node', 'z'))
    assert_is_not(fields.add_zeros('node', 'z'), fields.add_zeros('node', 'z'))


def test_add_existing_field_with_noclobber():
    """Test noclobber raises an error with an existing field."""
    fields = ModelDataFields()
    fields.new_field_location('node', 12)
    fields.add_empty('node', 'z')

    assert_raises(FieldError, fields.add_empty, 'node', 'z', noclobber=True)
    assert_raises(FieldError, fields.add_ones, 'node', 'z', noclobber=True)
    assert_raises(FieldError, fields.add_zeros, 'node', 'z', noclobber=True)


def test_add_field_with_noclobber():
    """Test noclobber does not raise an error with an new field."""
    fields = ModelDataFields()
    fields.new_field_location('node', 12)

    fields.add_empty('node', 'a', noclobber=True)
    assert_true('a' in fields['node'])

    fields.add_ones('node', 'b', noclobber=True)
    assert_true('b' in fields['node'])

    fields.add_zeros('node', 'c', noclobber=True)
    assert_true('c' in fields['node'])


def test_getitem():
    fields = ModelDataFields()
    fields.new_field_location('node', 12)

    assert_dict_equal(dict(), fields['node'])
    assert_raises(GroupError, lambda k: fields[k], 'cell')
    assert_raises(KeyError, lambda k: fields[k], 'cell')


def test_at_attribute():
    fields = ModelDataFields()
    fields.new_field_location('node', 12)

    assert_dict_equal(dict(), fields.at_node)
    assert_raises(AttributeError, lambda: fields.at_cell)

    fields.add_ones('node', 'z')
    assert_array_equal(np.ones(12), fields.at_node['z'])


def test_has_group():
    fields = ModelDataFields()
    fields.new_field_location('node', 12)

    assert_true(fields.has_group('node'))
    assert_false(fields.has_group('cell'))


def test_delete_field():
    fields = ModelDataFields()
    fields.new_field_location('link', 17)

    assert_dict_equal(dict(), fields.at_link)
    assert_raises(AttributeError, lambda: fields.at_node)

    fields.add_zeros('link', 'vals')
    assert_array_equal(np.zeros(17), fields.at_link['vals'])

    assert_raises(KeyError, lambda: fields.delete_field('node', 'vals'))
    fields.delete_field('link', 'vals')
    assert_raises(KeyError, lambda: fields.field_units('link', 'vals'))
    assert_raises(KeyError, lambda: fields.at_link['vals'])
