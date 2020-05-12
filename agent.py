import random
import datetime
import pyscreeze

STARTING = 1
SCANNING = 2
FIGHTING = 3

slots15 = [
(395, 12),
(303, 118),
(487, 118),
(210, 223),
(395, 223),
(579, 223),
(118, 329),
(303, 329),
(487, 329),
(672, 329),
( 26, 434),
(210, 434),
(395, 434),
(579, 434),
(764, 434),
]

class ArenaAgent():
	def __init__(self, hc):
		self.hc = hc
		self.state = STARTING
		# self.expected_pages=['main']

	def act(self):
		active_page, screenshot = self.hc.pages.active_page()
		self.hc.log_event(active_page)
		delay = 0.3
		if not active_page:
			self.hc.log_error("I don't know where I am ..")
			delay = 2
		elif active_page.name == 'timeout':
			self.hc.human_click(425, 325, 536, 376) # 'Update' button
		elif active_page.name == 'main':
			self.hc.human_click(19, 431, 100, 517) # Bottom left corner 'Map'
		elif active_page.name == 'map':
			# self.hc.human_click(19, 431, 100, 517)
			self.hc.human_click(330, 400, 460, 490) # Arena
		elif active_page.name == 'a_tickets':
			self.hc.human_click(170, 130, 300, 160) # for food
		elif active_page.name == 'a_food':
			# TODO - check if enough apples
			self.hc.human_click(230, 440, 400, 480) # Participate
		elif active_page.name == 'a_team':
			self.hc.human_click(320, 440, 460, 490) # Confirm
		elif active_page.name in ['loading', 'a_looking', 'a_wait', 'a_wait2', 'a_combat']:
			delay = 2
		elif active_page.name == 'a_next':
			if self.state == STARTING:
				self.initialize_scan(screenshot)
			if self.state == SCANNING:
				self.scan_enemies(screenshot)
			if self.state == FIGHTING:
				self.hc.log_error("Nezinu kam sist")
				self.hc.stop_agents()	
				delay = 2
		elif active_page.name in ['a_enemy', 'a_enemy2']:
			if self.state == SCANNING:
				strength_pic = screenshot.crop( (520, 230, 700, 255) )
				i_location = pyscreeze.locate('images/a_i.png', strength_pic)
				if not i_location:
					i_location = pyscreeze.locate('images/a_i2.png', strength_pic)
				if not i_location:
					self.hc.log_error('Could not find i')
					self.hc.screenshot('i_not_found')
				else:
					strength_pic = strength_pic.crop( (0, 0, i_location[0]-8, 25) )

				now = datetime.datetime.now()
				strength_pic.save(f'temp/strength_{self.scanning_enemy}_{now:%Y%m%d_%H%M%S}.png')
				if self.scanning_enemy:
					self.enemies[self.scanning_enemy]['strength'] = strength_pic

				self.scanning_enemy = None
				where = random.choices(['left', 'right', 'x'], [0.2, 0.6, 0.2])[0]
				if where == 'left':
					self.hc.human_click(45, 75, 170, 430) 
				elif where == 'right':
					self.hc.human_click(800, 145, 930, 500) 
				else:
					self.hc.human_click(760, 55, 790, 80)

			if self.state == FIGHTING:
				if active_page.name == 'a_enemy':
					self.hc.human_click(635, 430, 770, 475) # To battle!
					delay = 2
				else:
					self.hc.log_error('Attacking passive enemy..')
					self.hc.human_click(760, 55, 790, 80) # X to close
		elif active_page.name in ['a_defeat', 'a_victory']:
			self.hc.log_event(active_page.name)
			self.hc.human_click(415, 465, 545, 525) # Home
			delay = 1
		elif active_page.name == 'a_end':
			self.hc.log_event('Arena ending')
			self.hc.stop_agents()
			self.hc.human_click(805,  65, 940, 130) # Home

			# Page('as_enemy',		'images/a_enemy.png',	(640, 430, 150, 50)),
		else:
			self.hc.log_error("I just don't know what to do with myself...")
			self.hc.log_event(str(self.state))
			self.hc.screenshot('confused_ArenaAgent')
			self.hc.stop_agents()
			delay = 2

		return delay


	def initialize_scan(self, screenshot):
		self.state = SCANNING
		self.enemies = {nr:None for nr in range(1, 15)}
		self.scanning_enemy = None
		for nr, slot in enumerate(slots15, 1):
			x, y = slot
			rgb = screenshot.getpixel( (x-1, y-1) )
			# print(f'#{nr} : {rgb}')
			if rgb[0]==255 and rgb[1]==243 and rgb[2]==89:
				self.enemies[nr] = 'ME!'
				print(f"I'm #{nr}")



	def scan_enemies(self, screenshot):
		self.scanning_enemy = None
		for nr in range(1, 15):
			if not self.enemies.get(nr):
				self.scanning_enemy = nr
				break

		if not self.scanning_enemy:
			self.state = FIGHTING
			return

		x, y = slots15[self.scanning_enemy-1]		
		self.enemies[self.scanning_enemy]={}
		name_pic = screenshot.crop( (x+40, y+10, x+140, y+35) )
		now = datetime.datetime.now()
		name_pic.save(f'temp/name_{self.scanning_enemy}_{now:%Y%m%d_%H%M%S}.png')
		self.enemies[self.scanning_enemy]['name'] = name_pic
		self.hc.human_click(x, y, x+165, y+85)
