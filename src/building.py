class Building:
    def __init__(self):
        # list of vertices' positions for each room in meters ((0,0) is the point of reference)
        self.name = ['X rooms', 'Fibonacci']

        # sniffers' positions in meters ((0,0) is the point of reference)
        # WARNING!: take care of the sniffers' ordering
        self.sniffers_list = [[(0, 7.8), (5.1, 1.5), (9.3, 7.8)], [(9, 8), (17, 24), (0.5, 39)]]

        self.dictionary = [
            {'space': ['X3', 'X2', 'hallway'],
            'usage': ['study room', 'study room', 'hallway'],
            'geometry': [[(-1,-0.5),(5,-0.5),(5,8.3),(-1,8.3)],
                [(5,-0.5),(9.8,-0.5),(9.8,8.3),(5,8.3)],
                [(-1,-3),(9.8,-3),(9.8,-0.5),(-1,-0.5)]]},

            {'space': ['room E', 'room 1A', 'hall', 'hallway'],
            'usage': ['study room', 'study room', 'break', 'hallway'],
            'geometry': [[(11,0),(0,0),(0,23),(11,23)],
                [(0,28),(11,28),(11,47),(0,47)],
                [(-11,47),(0,47),(0,0),(-11,0)],
                [(0,28),(42,28),(42,23),(0,23)]]}
        ]