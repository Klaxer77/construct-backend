from shapely.geometry import MultiPolygon, Polygon


def create_geom_from_coords(coords_list):
    if all(isinstance(c, list) and len(c) > 0 and isinstance(c[0], list | tuple) for c in coords_list):
        polygons = [Polygon(c) for c in coords_list]
        if len(polygons) == 1:
            geom = polygons[0]
        else:
            geom = MultiPolygon(polygons)
    else:
        geom = Polygon(coords_list)
    
    return geom.wkt
