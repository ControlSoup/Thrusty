from gaslighter import RocketEngineGeometry, RocketEngineCEA, convert, to_file, pretty_dict, imperial_dictionary

chamber_geometry = RocketEngineGeometry(
    chamber_diameter = convert(2.75, 'in', 'm'),
    chamber_length = convert(6,'in','m'),
    chamber_volume = convert(37.38,'in^3', 'm^3'),
    exit_diameter = convert(2.04, 'in', 'm'),
    exit_length = convert(1.603, 'in', 'm'),
    throat_diameter = convert(1.16, 'in', 'm'),
)
geometry_str = pretty_dict(imperial_dictionary(chamber_geometry.dict()))

to_file(
    geometry_str,
    file_path='../results/geometry_report.md',
    file_name="Geometry Report"
)

