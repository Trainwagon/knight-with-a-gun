import pygame, sys
from scripts.settings import *
# states
from scripts.states.menu import Menu
from scripts.states.gameplay import Gameplay
from scripts.states.game_over import GameOver
from scripts.states.splash import Splash

from game import Game

pygame.init()
pygame.display.set_caption('Knight With A Gun')
screen = pygame.display.set_mode((WIDTH, HEIGHT))#, pygame.FULLSCREEN|pygame.SCALED)

states = {
    'MENU': Menu(),
    'SPLASH': Splash(),
    'GAMEPLAY': Gameplay(),
    'GAME_OVER': GameOver(),
}

game = Game(screen, states, "SPLASH")
game.run()

pygame.quit()
sys.exit()

  