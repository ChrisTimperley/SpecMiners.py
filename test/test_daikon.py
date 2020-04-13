# -*- coding: utf-8 -*-
import pytest

import contextlib
import os
import tempfile

import specminers


DIR_HERE = os.path.dirname(__file__)
DIR_EXAMPLES = os.path.join(DIR_HERE, 'examples')


def test_daikon():
    daikon = specminers.Daikon()
    filenames = [os.path.join(DIR_EXAMPLES, 'ardu.decls'),
                 os.path.join(DIR_EXAMPLES, 'ardu.dtrace')]
    out = daikon(*filenames)


def test_parse_decls():
    filename = os.path.join(DIR_EXAMPLES, 'ardu.decls')
    declarations = specminers.daikon.Declarations.load(filename)
    expected_decl_names = [
        'factory.MAV_CMD_NAV_WAYPOINT:::ENTER',
        'factory.MAV_CMD_NAV_WAYPOINT:::EXIT0',
        'factory.MAV_CMD_NAV_TAKEOFF:::ENTER',
        'factory.MAV_CMD_NAV_TAKEOFF:::EXIT0',
        'factory.MAV_CMD_NAV_LOITER_TURNS:::ENTER',
        'factory.MAV_CMD_NAV_LOITER_TURNS:::EXIT0',
        'factory.MAV_CMD_NAV_LOITER_TIME:::ENTER',
        'factory.MAV_CMD_NAV_LOITER_TIME:::EXIT0',
        'factory.MAV_CMD_NAV_RETURN_TO_LAUNCH:::ENTER',
        'factory.MAV_CMD_NAV_RETURN_TO_LAUNCH:::EXIT0',
        'factory.MAV_CMD_NAV_LAND:::ENTER',
        'factory.MAV_CMD_NAV_LAND:::EXIT0',
        'factory.MAV_CMD_NAV_SPLINE_WAYPOINT:::ENTER',
        'factory.MAV_CMD_NAV_SPLINE_WAYPOINT:::EXIT0',
        'factory.MAV_CMD_DO_CHANGE_SPEED:::ENTER',
        'factory.MAV_CMD_DO_CHANGE_SPEED:::EXIT0',
        'factory.MAV_CMD_DO_SET_HOME:::ENTER',
        'factory.MAV_CMD_DO_SET_HOME:::EXIT0',
        'factory.MAV_CMD_DO_PARACHUTE:::ENTER',
        'factory.MAV_CMD_DO_PARACHUTE:::EXIT0',
    ]

    assert len(declarations) == len(expected_decl_names)
    for name in expected_decl_names:
        assert name in declarations


def test_parse_trace():
    decls_filename = os.path.join(DIR_EXAMPLES, 'ardu.decls')
    trace_filename = os.path.join(DIR_EXAMPLES, 'ardu.dtrace')
    declarations = specminers.daikon.Declarations.load(decls_filename)
    reader = specminers.daikon.TraceFileReader(declarations)
    num_records = sum(1 for record in reader.read(trace_filename))
    assert num_records == 16384

    records = reader.read(trace_filename)
    first_record = next(records)
    assert first_record.ppt == declarations['factory.MAV_CMD_NAV_TAKEOFF:::ENTER']
    assert first_record.nonce == 1
    assert first_record['latitude'].value == -35.3629389
    assert first_record['latitude'].modified == 1


def test_write_trace():
    # keep track of modified values!
    decls_filename = os.path.join(DIR_EXAMPLES, 'ardu.decls')
    decls = specminers.daikon.Declarations.load(decls_filename)

    with contextlib.ExitStack() as stack:
        _, trace_filename = tempfile.mkstemp()
        stack.callback(os.remove, trace_filename)
        with specminers.daikon.TraceWriter.for_file(decls, trace_filename) as writer:
            writer.write('factory.MAV_CMD_NAV_TAKEOFF:::ENTER',
                         p_alt=11.89013788794762,
                         home_latitude=-35.3629389,
                         home_longitude=149.1650801,
                         altitude=0.01,
                         latitude=-35.3629389,
                         longitude=149.16508,
                         armable=1,
                         armed=1,
                         mode="GUIDED",
                         vx=-0.16,
                         vy=-0.14,
                         vz=0.0,
                         pitch=-0.009264621883630753,
                         yaw=-1.6489005088806152,
                         roll=-0.009207483381032944,
                         heading=265,
                         airspeed=0.0,
                         groundspeed=0.22160862386226654,
                         ekf_ok=1)

        # FIXME this!
        # let's try to read the record!
        reader = specminers.daikon.TraceFileReader(decls)
        records = reader.read(trace_filename)
        first_record = next(records)
        assert first_record.ppt.name == 'factory.MAV_CMD_NAV_TAKEOFF:::ENTER'
        assert first_record.nonce == 1
        assert first_record['latitude'].value == -35.3629389
