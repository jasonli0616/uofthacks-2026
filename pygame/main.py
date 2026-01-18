import game

if __name__ == "__main__":
	# Create a simple config object with default values
	class Config:
		def __init__(self):
			self.bpm = 120
			self.scale = "G"
			self.instrument = "Shredding Guitar"
			self.genre = "Classic Rock"
			self.mood = "Crunchy Distortion"

	config = Config()
	game.main(config)