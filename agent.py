import random
import datetime
import pyscreeze
from ocr import recognize
from PIL import ImageDraw
from timeit import default_timer as timer

STARTING = 1
SCANNING = 2
FIGHTING = 3

slots_15 = [
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


slots_10 = [
(395, 65),
(303, 170),
(487, 170),
(210, 275),
(395, 275),
(579, 275),
(118, 381),
(303, 381),
(487, 381),
(672, 381),
]


class ArenaAgent():
	def __init__(self, hc, beatable_strength, use_tickets, high_level):
		self.hc = hc
		self.state = STARTING
		self.first_arena_after_waiting = False
		self.just_was_in_combat = False
		self.in_combatend = False
		self.scanning_enemy = None
		self.attacking_enemy = None
		self.round = 1
		self.victories = 0
		self.start = timer()
		self.match_start = None

		self.beatable_strength = beatable_strength
		self.use_tickets = use_tickets
		if high_level:
			self.slots = slots_10
		else:
			self.slots = slots_15

	def act(self):
		active_page, screenshot = self.hc.pages.active_page()
		self.hc.logger.info(active_page)
		delay = 0.3
		if not active_page:
			delay = 2
			if self.first_arena_after_waiting:
				self.first_arena_after_waiting = False
				delay = 5
			elif self.just_was_in_combat:
				self.just_was_in_combat = False
			else:
				if self.hc.check_window_size():
					self.hc.logger.error("I don't know where I am ..")
					self.hc.screenshot('unknown', screenshot=screenshot)			
		elif active_page.name == 'timeout':
			self.hc.human_click(425, 325, 536, 376) # 'Update' button
		elif active_page.name == 'maintenance':
			self.hc.human_click(415, 325, 546, 376) # 'OK' button
		elif active_page.name == 'chat':
			self.hc.human_click(532, 224, 555, 260) # close
		elif active_page.name == 'main':
			self.hc.human_click(19, 431, 100, 517) # Bottom left corner 'Map'
		elif active_page.name == 'map':
			self.hc.human_click(330, 400, 460, 490) # Arena
			delay = 1
		elif active_page.name == 'a_store':
			self.hc.human_click(685, 95, 830, 140) # Close
			delay = 1
		elif active_page.name == 'a_tickets':
			if self.use_tickets:
				self.hc.human_click(230, 440, 400, 480) # Participate
			else:	
				self.hc.human_click(170, 130, 300, 160) # for food
			delay = 1
		elif active_page.name == 'a_food':
			if self.use_tickets:
				self.hc.human_click(330, 130, 460, 160) # for tickets
			else:
				self.hc.human_click(230, 440, 400, 480) # Participate
			delay = 2
		elif active_page.name == 'a_cancel':
			self.hc.human_click(500, 325, 620, 375) # Close
			delay = 1
		elif active_page.name == 'a_asleep':
			self.hc.human_click(525, 315, 655, 365) # Return
			delay = 1
		elif active_page.name == 'a_nofood':
			self.hc.human_click(510, 330, 615, 375) # No
			self.hc.logger.error('Out of apples !')
			self.hc.stop_agents()
		elif active_page.name == 'a_team':
			self.hc.human_click(320, 440, 460, 490) # Confirm
			self.round = 1
		elif active_page.name in ['loading', 'a_looking', 'a_wait', 'a_wait2', 'a_combat']:
			delay = 2
			self.first_arena_after_waiting = True
			self.in_combatend = False
			if active_page.name == 'a_combat':
				self.just_was_in_combat = True
		elif active_page.name == 'a_next':
			self.in_combatend = False
			if not self.match_start:
				self.match_start = timer()
			if self.first_arena_after_waiting:
				self.first_arena_after_waiting = False
				delay = 5
			else:
				if self.state == STARTING:
					self.initialize_scan(screenshot)
				if self.state == SCANNING:
					delay = 0.5
					self.scan_enemies(screenshot)
				if self.state == FIGHTING:
					self.attack_next_enemy(screenshot)
		elif active_page.name in ['a_enemy', 'a_enemy2']:
			if self.state == SCANNING:				
				strength_pic = screenshot.crop( (520, 230, 712, 257) )
				i_location = pyscreeze.locate('images/a_i.png', strength_pic, confidence=0.9)
				if not i_location:
					i_location = pyscreeze.locate('images/a_i2.png', strength_pic, confidence=0.9)
				if not i_location:
					self.hc.logger.error('Could not find i')
					self.hc.screenshot('i_not_found')
					strength = self.beatable_strength + 1
				else:
					strength_pic = strength_pic.crop( (0, 0, i_location[0]-8, 25) )
					strength = recognize(strength_pic)

				if self.scanning_enemy:
					self.enemies[self.scanning_enemy]['strength'] = strength
				self.scanning_enemy = None

				where = random.choices(['left', 'right', 'x'], [0.2, 0.6, 0.2])[0]
				if where == 'left':
					self.hc.human_click(45, 75, 170, 430) 
				elif where == 'right':
					self.hc.human_click(800, 145, 930, 500) 
				else:
					self.hc.human_click(762, 57, 790, 80)

			if self.state == FIGHTING:
				if self.attacking_enemy:
					self.attacking_enemy['attacked'] = True
					self.attacking_enemy = None
				if active_page.name == 'a_enemy':
					self.hc.human_click(635, 430, 770, 475) # To battle!
					delay = 2
				else:
					self.hc.logger.error('Attacking passive enemy..')					
					self.hc.human_click(760, 55, 790, 80) # X to close
					delay = 2				
		elif active_page.name in ['a_defeat', 'a_victory']:
			if self.just_was_in_combat:
				delay = 1
				self.just_was_in_combat = False
			else:
				self.hc.human_click(415, 465, 545, 525) # Home
				if not self.in_combatend:
					self.hc.logger.info(active_page.name)
					self.round = self.round + 1
					if active_page.name == 'a_victory':
						self.victories = self.victories + 1
					delay = 2
					self.in_combatend = True
		elif active_page.name in ['a_end', 'a_end2']:
			rank = self.find_me(screenshot)
			self.hc.logger.info(f'')
			self.hc.logger.info(f'==================================')
			if self.start and self.match_start:
				self.hc.logger.info(f'Arena ending - {(timer()-self.start)/60:.1f} min total, {(self.match_start-self.start)/60:.1f} min waiting')
			self.hc.logger.info(f'Rank {rank}, {self.victories} wins')
			self.state = STARTING
			self.start = timer()
			self.match_start = None
			self.victories = 0
			self.round = 1
			# self.hc.stop_agents()
			self.hc.human_click(805,  65, 940, 130) # Home
			delay = 5
		else:
			self.hc.logger.error(f"I just don't know what to do with myself... {active_page.name} {str(self.state)}")
			self.hc.screenshot(f'confused_ArenaAgent_{active_page.name}')
			self.hc.stop_agents()
			delay = 2		

		return delay


	def find_me(self, screenshot):
		for nr, slot in enumerate(self.slots, 1):
			x, y = slot
			rgb = screenshot.getpixel( (x-1, y-1) )
			if rgb[0]==255 and rgb[1]==243 and rgb[2]==89:
				# copy = screenshot.copy()
				# draw = ImageDraw.Draw(copy)
				# draw.rectangle( (x, y, x+160, y+80), outline='red', width=2)
				# copy.save(f'screenshots/foundme_{datetime.datetime.now():%Y%m%d_%H%M%S}.png')
				return nr
		self.hc.logger.error('Could not find me in screenshot')
		screenshot.save(f'screenshots/couldnotfindme_{datetime.datetime.now():%Y%m%d_%H%M%S}.png')
		return None


	def initialize_scan(self, screenshot):
		self.state = SCANNING
		self.enemies = {nr:None for nr in range(1, len(self.slots))}
		self.scanning_enemy = None
		nr = self.find_me(screenshot)
		if nr:
			self.enemies[nr] = {'name':'ME!', 'strength':0, 'rank':nr}
			self.me = self.enemies[nr]
			print(f"I'm #{nr}")


	def scan_enemies(self, screenshot):
		self.scanning_enemy = None
		for nr in range(1, len(self.slots)+1):
			if not self.enemies.get(nr):
				self.scanning_enemy = nr
				break

		if not self.scanning_enemy:
			# print('All enemies scanned')
			# for nr in range(1, 16):
			# 	print(nr, self.enemies.get(nr))
			self.state = FIGHTING
			return

		x, y = self.slots[self.scanning_enemy-1]		
		self.enemies[self.scanning_enemy]={}
		name_pic = screenshot.crop( (x+40, y+10, x+140, y+35) )
		# name_pic.save(f'temp/name_{self.scanning_enemy}_{datetime.datetime.now():%Y%m%d_%H%M%S}.png')
		self.enemies[self.scanning_enemy]['name_pic'] = name_pic
		self.hc.human_click(x, y, x+165, y+85)

	def update_enemy_rankings(self, screenshot):
		for nr, enemy in self.enemies.items():
			enemy['rank'] = 0
			if enemy.get('name') == 'ME!':
				nr = self.find_me(screenshot)
				if nr:
					enemy['rank'] = nr
				self.me = enemy
			elif enemy.get('name_pic'):
				enemy_location = pyscreeze.locate(enemy.get('name_pic'), screenshot, confidence=0.9)
				if not enemy_location:
					enemy_location = pyscreeze.locate(enemy.get('name_pic'), screenshot, confidence=0.8)
				if not enemy_location:
					enemy_location = pyscreeze.locate(enemy.get('name_pic'), screenshot, confidence=0.7)
				if enemy_location:
					# copy = screenshot.copy()
					# draw = ImageDraw.Draw(copy)
					# draw.rectangle( (enemy_location[0], enemy_location[1], enemy_location[0]+enemy_location[2], enemy_location[1]+enemy_location[3]), outline='red', width=2)
					# copy.save(f'screenshots/enemy_{nr}_{datetime.datetime.now():%Y%m%d_%H%M%S}.png')
					for rank, slot in enumerate(self.slots, 1):
						x, y = slot
						if x < enemy_location[0] < x+50 and y < enemy_location[1] < y+20:
							enemy['rank'] = rank
				else:
					self.hc.logger.error(f'Could not find enemy {enemy} in screenshot')	
					# screenshot.save(f'screenshots/couldnotfindenemy_{datetime.datetime.now():%Y%m%d_%H%M%S}.png')
					# enemy.get('name_pic').save(f'screenshots/couldnotfindenemy2_{datetime.datetime.now():%Y%m%d_%H%M%S}.png')
			else:
				self.hc.logger.error(f'Could not find enemy {enemy} because no pic')

		s = sorted(self.enemies.values(), key=lambda enemy:enemy.get('rank'))
		print(f'Round {self.round} !!\n==========================')
		for enemy in s:
			if enemy.get('name') == 'ME!':
				print(f"#{enemy.get('rank')}: ME!")
			else:
				attacked = ''
				if enemy.get('attacked'):
					attacked = '[x]'
				if not enemy.get('rank'):
					self.hc.logger.error(f'enemy {enemy} has no rank')
					enemy['rank'] = 0
				if not enemy.get('strength'):
					self.hc.logger.error(f'enemy {enemy} has no strength')
					enemy['strength'] = 200000
				print(f"#{enemy.get('rank'): <2}: {enemy.get('strength'): <8} {attacked}")
		return s

	def weak_above_me(self):		
		weak = [enemy for enemy in self.enemies.values() if enemy.get('strength') < self.beatable_strength and enemy.get('rank') < self.me.get('rank') and not enemy.get('attacked')]
		closest = sorted(weak, key=lambda enemy:enemy.get('rank'), reverse=True)
		if closest:
			print('Vājie virs manis:')		
			for enemy in closest:
				print(f"#{enemy.get('rank')}: {enemy.get('strength')}")
			return closest[0]
		else:
			return None

	def weak_below_me(self):		
		weak = [enemy for enemy in self.enemies.values() if enemy.get('strength') < self.beatable_strength and enemy.get('rank') > self.me.get('rank') and not enemy.get('attacked')]
		closest = sorted(weak, key=lambda enemy:enemy.get('rank'), reverse=True)
		if closest:
			print('Vājie zem manis:')		
			for enemy in closest:
				print(f"#{enemy.get('rank')}: {enemy.get('strength')}")
			return closest[0]
		else:
			return None

	def weakest5(self):
		enemies = [enemy for enemy in self.enemies.values() if enemy.get('name') != 'ME!' and enemy.get('rank')]
		enemies_by_strength = sorted(enemies, key=lambda enemy:enemy.get('strength'))[:5]
		enemies_by_strength.reverse()	
		print('Candidates for attack:')		
		for enemy in enemies_by_strength:
			print(f"#{enemy.get('rank')}: {enemy.get('strength')}")
		for enemy in enemies_by_strength:
			if not enemy.get('attacked'):
				return enemy
		return None

	def choose_next_enemy(self):		
		if self.round > 1:
			candidate = self.weak_above_me()
			if candidate:
				return candidate
			candidate = self.weak_below_me()
			if candidate:
				return candidate

		candidate = self.weakest5()
		if candidate:
			return candidate

		self.hc.logger.error(f'Could not choose an enemy, all attacked')
		return self.enemies[1]

	def attack_next_enemy(self, screenshot):
		ranked = self.update_enemy_rankings(screenshot)
		self.attacking_enemy = self.choose_next_enemy()
		print(f"Attacking enemy #{self.attacking_enemy.get('rank')} with strength {self.attacking_enemy.get('strength')}")
		x, y = self.slots[self.attacking_enemy['rank']-1]		
		self.hc.human_click(x, y, x+165, y+85)


class InvasionAgent():
	def __init__(self, hc):
		self.hc = hc

	def act(self):
		active_page, screenshot = self.hc.pages.active_page()
		self.hc.logger.info(active_page)
		delay = 0.3
		if not active_page:
			self.hc.logger.error("I don't know where I am ..")
			delay = 2
		elif active_page.name == 'timeout':
			self.hc.human_click(425, 325, 536, 376) # 'Update' button
		elif active_page.name in ['loading', 'a_combat']:
			delay = 2
		elif active_page.name == 'main':
			self.hc.human_click(19, 431, 100, 517) # Bottom left corner 'Map'
		elif active_page.name == 'map':
			invasion = pyscreeze.locate('images/i_mapface.png', screenshot, confidence=0.9)
			if invasion:
				self.hc.human_click(invasion[0], invasion[1], invasion[0]+invasion[2], invasion[1]+invasion[3])
				delay = 2
			else:
				self.hc.logger.info('No invasions active!')
				self.hc.stop_agents()								
		elif active_page.name == 'i_map':
			invasion = pyscreeze.locate('images/i_mapface2.png', screenshot, confidence=0.8)
			if invasion:
				self.hc.human_click(invasion[0], invasion[1], invasion[0]+invasion[2], invasion[1]+invasion[3])
				delay = 1
			else:
				self.hc.human_click(19, 431, 100, 517) # Bottom left corner 'Map'
		elif active_page.name == 'i_invasion':
				self.hc.human_click(620, 430, 750, 475) # Attack
				delay = 1
		elif active_page.name in ['a_defeat', 'a_victory']:
			self.hc.human_click(415, 465, 545, 525) # Home
			# FIXME - use the new 'Next' button
		elif active_page.name == 'i_victory':
			self.hc.human_click(535, 460, 680, 500) # Home
			self.hc.logger.info('Invasions done!')
			self.hc.stop_agents()								
		else:
			self.hc.logger.error(f"I just don't know what to do with myself... {active_page.name}")
			self.hc.screenshot(f'confused_ArenaAgent_{active_page.name}')
			self.hc.stop_agents()
			delay = 2

		return delay



if __name__ == '__main__':
	enemy_location = pyscreeze.locate('ocrtest/needle1.png', 'ocrtest/haystack1.png', confidence=0.9)
	print(enemy_location)
	enemy_location = pyscreeze.locate('ocrtest/needle2.png', 'ocrtest/haystack2.png', confidence=0.8)
	print(enemy_location)
	enemy_location = pyscreeze.locate('ocrtest/needle3.png', 'ocrtest/haystack3.png', confidence=0.7)
	print(enemy_location)
