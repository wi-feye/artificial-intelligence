class Building:
    def __init__(self):
        # list of vertices' positions for each room in meters ((0,0) is the point of reference)
        self.dictionary = {
            'space': ['X3', 'X2', 'hallway'],
            'usage': ['study room', 'study room', 'hallway'],
            'geometry': [[(-1,-0.5),(5,-0.5),(5,8.3),(-1,8.3)],
                [(5,-0.5),(9.8,-0.5),(9.8,8.3),(5,8.3)],
                [(-1,-3),(9.8,-3),(9.8,-0.5),(-1,-0.5)]]
        }