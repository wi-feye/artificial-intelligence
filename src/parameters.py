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
        # 0: 'X rooms', 1: 'Fibonacci'
        self.select_building = 1

        # 1 meter rss (zerynth device)
        self.rss0 = -52

        # environment constant in range [2,4] 2 pochi ostacoli (aumenta sparsità), 4 molti ostacoli (diminuisce sparsità)
        self.n_env = 3
        # y-m-d
        self.start_time = datetime.datetime(2022, 11, 21)
        
        self.end_time = None

        self.size = 10000

        self.start = 1