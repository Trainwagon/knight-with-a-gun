import pygame, sys
from scripts.settings import *
# states
from scripts.states.menu import Menu
from scripts.states.gameplay import Gameplay
from scripts.states.game_over import GameOver
from scripts.states.splash import Splash
from scripts.states.backstory import Backstory
from scripts.states.tutorial import Tutorial

from game import Game

pygame.init()
pygame.display.set_caption('Knight With A Gun')
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN|pygame.SCALED)

states = {
    'SPLASH': Splash(),
    'BACKSTORY': Backstory(),
    'MENU': Menu(),
    'TUTORIAL': Tutorial(),
    'GAMEPLAY': Gameplay(),
    'GAME_OVER': GameOver(),
}

game = Game(screen, states, "SPLASH")
game.run()

pygame.quit()
sys.exit()