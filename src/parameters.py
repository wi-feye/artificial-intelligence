class Parameter:
    def __init__(self):
        # sniffers' positions in meters ((0,0) is the point of reference)
        # WARNING!: take care of the sniffers' ordering
        self.sniffers_list = [(0, 7.8), (5.1, 1.5), (9.3, 7.8)]

        # 1 meter rss (zerynth device)
        self.rss0 = -54

        # environment constant in range [2,4] 2 pochi ostacoli, 4 molti ostacoli
        self.n_env= 3.6

        self.size = 500

        self.start = 1