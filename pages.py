from PIL import Image

class Pages():
	def __init__(self, hc):
		self.hc = hc
		self.pages = [
			#    name       	filename			     left top width height
			Page('timeout',		'images/timeout.png',	(270, 140, 450, 300)),
			Page('maintenance',	'images/maintenance.png',	(270, 120, 450, 300)),
			Page('loading',		'images/loading.png', 	(160, 10,  800, 100)),
			Page('chat',		'images/chat.png', 		(0,   0,   200, 200), confidence=0.9),
			Page('main', 		'images/main.png',		(20,  400, 100, 150)),
			Page('map', 		'images/map.png',		(20,  400, 100, 150)),
			Page('a_tickets',	'images/a_tickets.png',	(170, 120, 300, 60)),
			Page('a_food',		'images/a_food.png',	(160, 120, 320, 60)),
			Page('a_nofood',	'images/a_nofood.png',	(290, 150, 400, 150)),
			Page('a_team',		'images/a_team.png',	(400, 25,  200, 50)),
			Page('a_looking',	'images/a_looking.png',	(170, 310, 300, 50)),
			Page('a_cancel',	'images/a_cancel.png',	(270, 130, 450, 300), confidence=0.9),
			Page('a_asleep',	'images/a_asleep.png',	(440, 150, 300, 250), confidence=0.9),
			Page('a_next',		'images/a_next.png',	(620, 0,   250, 50), confidence=0.9),
			Page('a_wait',		'images/a_wait.png',	(620, 0,   150, 50), confidence=0.9),
			Page('a_wait2',		'images/a_wait2.png',	(620, 0,   250, 50), confidence=0.9),
			Page('a_enemy',		'images/a_enemy.png',	(640, 430, 150, 50)),
			Page('a_enemy2',	'images/a_enemy2.png',	(640, 430, 150, 50)),
			Page('a_combat',	'images/a_combat.png',	(450, 10,  100, 50)),
			Page('a_defeat',	'images/a_defeat.png',	(420, 95,  150, 50)),
			Page('a_victory',	'images/a_victory.png',	(420, 95,  150, 50), confidence=0.9),
			Page('a_end',		'images/a_end.png',		(840, 70,  100, 50)),
			Page('a_end2',		'images/a_end2.png',	(790, 65,  150, 70)),
			Page('a_store',		'images/a_store.png',	(230, 40,  250, 60)),
			Page('i_invasion',	'images/i_invasion.png',(400, 50,  150, 50)),
			Page('i_map',		'images/i_map.png',		(10,  430, 150, 150)),
			Page('i_victory',	'images/i_victory.png',	(500, 150, 300, 300)),
		]
		# TODO - timeout and loading may be confused!!
		self.pages_by_name = {page.name:page for page in self.pages}

	def get_page(self, name):
		return self.pages_by_name.get(name)

	def active_page(self):
		# Benchmark:
		# 10x full undetected  is_active->verify_image : 18.6 sec
		# 10x is_active->verify_image if stopping at man: 3.6 sec
		# 10x full undetected  w. screenshot : 2.1 sec
		screenshot = self.hc.window.capture_as_image()
		for page in self.pages:
			if page.is_active(self.hc, screenshot=screenshot):
				return page, screenshot
		return None, screenshot


class Page():
	def __init__(self, name, verification_image, verification_region = None, confidence = 1):
		self.name = name
		self.verification_image_name = verification_image
		self.verification_image = Image.open(verification_image)
		self.verification_region = verification_region
		self.confidence = confidence

	def __str__(self):
		return f'Page({self.name})'

	def is_active(self, hc, must_succeed=False, screenshot=None):
		return hc.verify_image(self.verification_image, self.verification_region, must_succeed, self.name, screenshot, self.confidence)
