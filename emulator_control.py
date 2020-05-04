from pywinauto import Desktop
import pyscreeze
import datetime
from pages import Page, Pages

def log_event(message):
	# TODO - lai iet uz textlogu
	print(message)


def log_error(message):
	# TODO - lai iet uz textlogu
	print(message)

class HC():
	def __init__(self):
		self.fetch_hc_window()
		self.verify_bluestacks()
		self.pages = Pages(self)

	def run_arena(self):
		print('Nemāku palaist arēnu')

	def fetch_hc_window(self):
		self.bluestacks = None
		self.window = None
		for w in Desktop(backend='win32', allow_magic_lookup=False).windows():
			if w.window_text() == 'BlueStacks':
				self.bluestacks = w
				break
		if not self.bluestacks:
			log_error('Failed to find BlueStacks window - is it opened?')
			raise Exception('Failed to find BlueStacks window - is it opened?')

		for c in self.bluestacks.children():		
			if c.element_info.name == '_ctl.Window':
				self.window = c
				break
		if not self.window:
			log_error('Failed to find HustleCastle VM window - is it opened?')
			raise Exception('Failed to find HustleCastle VM  window - is it opened?')

		# img = window.capture_as_image()
		# img.save('test.png')

		bs_rect = self.bluestacks.rectangle() 
		hc_rect = self.window.rectangle() 
		bs_width = bs_rect.right-bs_rect.left
		bs_height = bs_rect.bottom-bs_rect.top
		hc_width = hc_rect.right-hc_rect.left
		hc_height = hc_rect.bottom-hc_rect.top

		if hc_width != 960 or hc_height != 540:
			log_event(f'Bluestacks {bs_width}x{bs_height}, HC {hc_width}x{hc_height}')
			self.bluestacks.move_window(width=(bs_width-hc_width+960), height=(bs_height-hc_height+540))
			bs_rect = self.bluestacks.rectangle() 
			hc_rect = self.window.rectangle() 
			bs_width = bs_rect.right-bs_rect.left
			bs_height = bs_rect.bottom-bs_rect.top
			hc_width = hc_rect.right-hc_rect.left
			hc_height = hc_rect.bottom-hc_rect.top
			log_event(f'Resized - Bluestacks {bs_width}x{bs_height}, HC {hc_width}x{hc_height}')

	# Verify if bluestacks window is active and visible by looking for the logo in coner
	def verify_bluestacks(self):
		bs_rect = self.bluestacks.rectangle() 
		coords = pyscreeze.locateOnScreen('images/bluestacks.png', region=(bs_rect.left, bs_rect.top, 200, 100))
		if not coords:
			log_error('Failed to verify BlueStacks')
		return coords

	def verify_image(self, image, region=None, must_succeed=False, description=''):
		hc_rect = self.window.rectangle()
		if region:
			assert len(region) == 4, 'verify_image needs a region with four items'
			region = (region[0]+hc_rect.left, region[1]+hc_rect.top, region[2], region[3])
		else:
			region = (hc_rect.left, hc_rect.top, hc_rect.right-hc_rect.left,  hc_rect.bottom-hc_rect.top)
		coords = pyscreeze.locateOnScreen(image, region=region)
		if not coords and must_succeed:
			log_error(f'Did not find image {description}')
			if description:				
				self.screenshot(f'didnotfind_{description}')
			else:
				self.screenshot(f'didnotfind')
		return coords

	def screenshot(self, prefix='screenshot'):
		screenshot = self.window.capture_as_image()
		now = datetime.datetime.now()			
		filename = f'screenshots/{prefix}_{now:%Y%m%d_%H%M%S}.png'
		screenshot.save(filename)
		log_event(f'Took screenshot {filename}')

if __name__ == '__main__':
	hc = HC()

