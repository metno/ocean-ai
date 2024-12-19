# Used to transform fields from infer output into same metadata as input+++


def one_field(ds, slc, field):
    """Get a field which does not need transformation."""
    t_idx = ds.variables.index(field)
    return ds[slc][:,t_idx,0] 

def water_speed_magnitude(ds, slc, field):
    """Convert sea water velocity in x- and y-dirs to
    sea water speed magnitude"""
    u_idx = ds.variables.index('u_eastward_1')
    v_idx = ds.variables.index('v_northward_1')
    u1 = ds[slc][:,u_idx,0]
    v1 = ds[slc][:,v_idx,0]
    speed1 = (u1**2+v1**2)**0.5
    return speed1

map_keys = {
    'temperature_1': {
        'norkyst': ['temperature_1'],
        'units': 'C',
        'transform': one_field,
        'thresholds': [-4, -2, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26],
        'long_name': 'Sea water potential temperature 1m',
    },
    'water_speed_1m': {
        'norkyst': ['u_eastward_1', 'v_northward_1'], 
        'units': 'm/s', 
        'transform': water_speed_magnitude,
        'thresholds': [10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.6], ##?? - left over from wind speed, not used?
        'long_name': 'Sea water speed 1m',
    },
    'u_water_speed_1m': {
        'norkyst': ['u_eastward_1'], 
        'units': 'm/s', 
        'transform': one_field,
        'long_name': 'Sea water eastward velocity',
    },
    'v_water_speed_1m': {
        'norkyst': ['v_northward_1'], 
        'units': 'm/s', 
        'transform': one_field,
        'long_name': 'Sea water northward velocity',
    },
    'w_water_speed_1m': {
        'norkyst': ['w_1'], 
        'units': 'm/s', 
        'transform': one_field,
        'long_name': 'Sea water northward velocity',
    },
    'zeta': {
        'norkyst': ['zeta_1'],
        'units': 'meter',
        'transform': one_field,
        #'thresholds': [970, 980, 990, 1000, 1010, 1020, 1030],
        'long_name': 'Sea surface height above geoid',
    },
    'salinity': {
        'norkyst': ['salinity_1'],
        'units': '1e-3',
        'transform': one_field,
        #'thresholds': [970, 980, 990, 1000, 1010, 1020, 1030],
        'long_name': 'Sea water salinity',
    },
}
