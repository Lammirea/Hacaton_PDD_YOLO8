def find_indexes_carHumansCross(list1, list2):
    """Находит индексы элементов list1 в list2"""
    indexes = {}
    for item in list1:
        indexes[item] = [i for i, x in enumerate(list2) if x == item]
    return indexes

def get_coordinates_carHumansCross(indexes, list3):
    """Получает координаты элементов по их индексам в list3"""
    coordinates = {}
    for item, item_indexes in indexes.items():
        coordinates[item] = [list3[i] for i in item_indexes]
    return coordinates

def check_intersection_carHumansCross(coords1, coords2, coords3):
    """Проверяет пересечение координат всех трех элементов"""
    for coord1 in coords1:
        for coord2 in coords2:
            for coord3 in coords3:
                if check_overlap_carHumansCross(coord1, coord2, coord3):
                    return True
    return False

def check_overlap_carHumansCross(coord1, coord2, coord3):
    """Проверяет пересечение трех прямоугольников по их координатам"""
    x1, y1, x2, y2 = coord1
    x3, y3, x4, y4 = coord2
    x5, y5, x6, y6 = coord3
    
    return not (x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1 or
                x2 < x5 or x6 < x1 or y2 < y5 or y6 < y1)
