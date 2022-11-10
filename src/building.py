class Building:
    def __init__(self):
        # list of vertices' positions for each room in meters ((0,0) is the point of reference)
        self.building_dictionary = {
            'space': ['X3', 'X2'],
            'geometry': [[(-1,-0.5),(5,-0.5),(5,8.3),(-1,8.3)],
                [(5,-0.5),(9.8,-0.5),(9.8,8.3),(5,8.3)]]
        }