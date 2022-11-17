import datetime

# Costants
WORKSPACE_ATZENI_SNIFFERS = 'wks-6sdnjgqfpv98'
WORKSPACE_NOSTRI_SNIFFERS = 'wks-7e2yv6y5ijmc'
WORKSPACE = WORKSPACE_NOSTRI_SNIFFERS # selection of workspace to use by default
HEADERS = {
        'X-API-KEY': 'G9froN8D4R.cF1znVzGvCejjc5BrzCsSqcqMaANPgRmFXMglCAWhkYttQFTymThnrf1ta7OQVP4'
    }

class Parameter:
    def __init__(self):
        # sniffers' positions in meters ((0,0) is the point of reference)
        # WARNING!: take care of the sniffers' ordering
        self.sniffers_list = [(0, 7.8), (5.1, 1.5), (9.3, 7.8)]

        # 1 meter rss (zerynth device)
        self.rss0 = -54

        # environment constant in range [2,4] 2 pochi ostacoli (aumenta sparsità), 4 molti ostacoli (diminuisce sparsità)
        self.n_env = 3.333
        
        self.start_time = datetime.datetime(2022, 11, 9)
        
        self.end_time = None

        self.size = 1000

        self.start = 1