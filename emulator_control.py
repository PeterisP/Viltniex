from pywinauto import Desktop, mouse
import pyscreeze
import datetime
from pages import Page, Pages
from agent import ArenaAgent, InvasionAgent
from random import gauss, randrange
from PIL import ImageDraw, Image
from win32api import GetCursorPos

def random_between(low, high):
	assert low < high, 'Random needs low < high'
	middle = (high+low)/2
	while True:
		sample = gauss(middle, (high-middle)/3) # Sample from normal distribution within 3 stddevs
		if low <= sample <= high:
			return int(sample)

class HC():
	def __init__(self, tkinterRoot, logger):
		self.fetch_hc_window()
		self.verify_bluestacks()
		self.pages = Pages(self)
		self.activeAgent = None
		self.tkinterRoot = tkinterRoot
		self.logger = logger

	def run_arena(self, beatable_strength, use_tickets, high_level):
		self.logger.info('Starting arena agent')
		self.activeAgent = ArenaAgent(self, beatable_strength, use_tickets, high_level)
		self.poke_agent()

	def run_invasion(self):
		self.logger.info('Starting invasion agent')
		self.activeAgent = InvasionAgent(self)
		self.poke_agent()

	def poke_agent(self):
		if not self.activeAgent:
			return # assume that agent is stopped
		delay = self.activeAgent.act()*1000 + randrange(100)
		delay = int(delay)
		self.tkinterRoot.after(delay, self.poke_agent)

	def stop_agents(self):
		self.logger.info('Stopping agents')
		self.activeAgent = None

	def human_click(self, left, top, right, bottom, debug_screenshots=False):
		x = random_between(left, right)
		y = random_between(top, bottom)

		if debug_screenshots:
			screenshot = self.window.capture_as_image()
			draw = ImageDraw.Draw(screenshot)
			draw.rectangle([left, top, right, bottom], outline='red', width=2)
			draw.line([x-5, y-5, x+5, y+5], fill='red', width=2)
			draw.line([x-5, y+5, x+5, y-5], fill='red', width=2)
			now = datetime.datetime.now()			
			filename = f'screenshots/click_{now:%Y%m%d_%H%M%S}.png'
			screenshot.save(filename)

		old_x, old_y = GetCursorPos()
		mouse.click(coords=(self.window.rectangle().left+x, self.window.rectangle().top+y))
		mouse.move((old_x, old_y))


	def fetch_hc_window(self):
		self.bluestacks = None
		self.window = None
		for w in Desktop(backend='win32', allow_magic_lookup=False).windows():
			if w.window_text() == 'BlueStacks':
				self.bluestacks = w
				break
		if not self.bluestacks:
			self.logger.error('Failed to find BlueStacks window - is it opened?')
			raise Exception('Failed to find BlueStacks window - is it opened?')

		for c in self.bluestacks.children():		
			if c.element_info.name == '_ctl.Window':
				self.window = c
				break
		if not self.window:
			self.logger.error('Failed to find HustleCastle VM window - is it opened?')
			raise Exception('Failed to find HustleCastle VM  window - is it opened?')

		self.check_window_size()

	def check_window_size(self):
		bs_rect = self.bluestacks.rectangle() 
		hc_rect = self.window.rectangle() 
		bs_width = bs_rect.right-bs_rect.left
		bs_height = bs_rect.bottom-bs_rect.top
		hc_width = hc_rect.right-hc_rect.left
		hc_height = hc_rect.bottom-hc_rect.top

		if hc_width == 960 and hc_height == 540:
			return True
		else:
			self.logger.info(f'Bluestacks {bs_width}x{bs_height}, HC {hc_width}x{hc_height}')
			self.bluestacks.move_window(width=(bs_width-hc_width+960), height=(bs_height-hc_height+540))
			bs_rect = self.bluestacks.rectangle() 
			hc_rect = self.window.rectangle() 
			bs_width = bs_rect.right-bs_rect.left
			bs_height = bs_rect.bottom-bs_rect.top
			hc_width = hc_rect.right-hc_rect.left
			hc_height = hc_rect.bottom-hc_rect.top
			self.logger.info(f'Resized - Bluestacks {bs_width}x{bs_height}, HC {hc_width}x{hc_height}')
			return False



	# Verify if bluestacks window is active and visible by looking for the logo in coner
	def verify_bluestacks(self):
		bs_rect = self.bluestacks.rectangle() 
		coords = pyscreeze.locateOnScreen('images/bluestacks.png', region=(bs_rect.left, bs_rect.top, 200, 100))
		if not coords:
			self.logger.error('Failed to verify BlueStacks')
		return coords

	# region is left, top, width, height
	def verify_image(self, image, region=None, must_succeed=False, description='', screenshot=None, confidence=1):
		try:
			if screenshot:
				coords = pyscreeze.locate(image, screenshot, region=region)
				if not coords and confidence < 1:
					coords = pyscreeze.locate(image, screenshot, region=region, confidence=confidence)
			else:
				hc_rect = self.window.rectangle()
				if region:
					assert len(region) == 4, 'verify_image needs a region with four items'
					region = (region[0]+hc_rect.left, region[1]+hc_rect.top, region[2], region[3])
				else:
					region = (hc_rect.left, hc_rect.top, hc_rect.right-hc_rect.left,  hc_rect.bottom-hc_rect.top)
				coords = pyscreeze.locateOnScreen(image, region=region)
				if not coords and confidence < 1:
					coords = pyscreeze.locateOnScreen(image, region=region, confidence=confidence)
		except Exception as e:
			self.logger.error(e)
			coords = None

		if not coords and must_succeed:
			self.logger.error(f'Did not find image {description}')
			if description:				
				self.screenshot(f'didnotfind_{description}')
			else:
				self.screenshot(f'didnotfind')
		return coords  # FIXME - coord reference point may differ depending on params

	def screenshot(self, prefix='screenshot', screenshot = None, full=False):
		if not screenshot:
			if full:
				screenshot = self.bluestacks.capture_as_image()
			else:
				screenshot = self.window.capture_as_image()
		now = datetime.datetime.now()			
		filename = f'screenshots/{prefix}_{now:%Y%m%d_%H%M%S}.png'
		screenshot.save(filename)
		self.logger.error(f'Took screenshot {filename}')

if __name__ == '__main__':
	hc = HC(None)
	victory = hc.pages.get_page('a_victory')
	pic = Image.open(f'ocrtest/victory_test.png')
	print(victory.is_active(hc, screenshot=pic))

	cancel = hc.pages.get_page('a_cancel')
	pic = Image.open(f'ocrtest/cancel_test.png')
	print(cancel.is_active(hc, screenshot=pic))
