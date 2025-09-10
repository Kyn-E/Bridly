from turtle import position
import pygame
from pygame.locals import *
from sys import exit
import random

pygame.init()

fly_sound = pygame.mixer.Sound("asset/fly.mp3")
score_sound = pygame.mixer.Sound("asset/scoring.mp3")
hit_sound = pygame.mixer.Sound("asset/hit.mp3")
hit_played = False 
clock = pygame.time.Clock()
fps = 60

# Set up the game window dimensions
gamewidth = 864
gameheight = 936

screen = pygame.display.set_mode((gamewidth, gameheight))
pygame.display.set_caption("Flappy Bird")

#define font variables
font = pygame.font.SysFont("04b03", 80)  # Load the font
white = (255, 255, 255)  # Define white color

#define game variables
ground_scroll = 0
ground_scroll_change = 4
flying = False
gameover = False
pipegap = 150
pipefreq = 1500  # Frequency of pipe generation in milliseconds
last_pipe = pygame.time.get_ticks() - pipefreq  # Initialize last pipe time
score = 0
passthepipe = False


# Load the background image
background = pygame.image.load("asset/bg.png")
ground_img = pygame.image.load("asset/ground.png")
button_img = pygame.image.load("asset/restart.png")

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipegroup.empty()  # Clear the pipe group
    flappy.rect.x = 100  # Reset the bird's x position
    flappy.rect.y = int(gameheight / 2)  # Reset the bird's y position
    score = 0  # Reset the score
    return score  # Return the reset score

# Load the bird image
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []  # ← Ganti jadi images
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"asset/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]  # ← Gunakan self.image sebagai Surface aktif
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
    
    def update(self):
        #animate the bird

        if flying == True:
            self.vel += 0.5  # Gravity effect
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)  # Update vertical position
        if gameover == False:
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
                fly_sound.play()

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            cooldown = 5
            if self.counter >= cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):  # ← Gunakan self.images
                    self.index = 0
            self.image = self.images[self.index]  # ← Update surface yang aktif

            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -1.5)  # Rotate the bird based on velocity
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("asset/pipe.png")
        self.rect = self.image.get_rect()

        if position == 1:  # TOP PIPE
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - (pipegap // 2)]
        if position == -1:  # BOTTOM PIPE
            self.rect.topleft = [x, y + (pipegap // 2)]

    def update(self):
        self.rect.x -= ground_scroll_change
        if self.rect.right < 0:  # Remove pipe if it goes off screen
            self.kill()

class Button():
    def __init__ (self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    def draw(self):

        #mouse position
        pos = pygame.mouse.get_pos()
        #check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action if 'action' in locals() else False
birdgroup = pygame.sprite.Group()
pipegroup = pygame.sprite.Group()

flappy = Bird(100, int(gameheight / 2))

birdgroup.add(flappy)

#restart button
button = Button(gamewidth // 2 - 50, gameheight // 2 - 100, button_img)

pipebtm = Pipe(300, int(gameheight / 2), -1)  # Bottom pipe
pipetop = Pipe(300, int(gameheight / 2), 1)  # Top pipe
pipegroup.add(pipebtm)
pipegroup.add(pipetop)

run = True
while run:
    #fps
    clock.tick(fps)  # Control the frame rate

    screen.blit(background, (0,0))  # Draw the background

    birdgroup.draw(screen)  # Draw the bird
    birdgroup.update()  # Update the bird's animation

    pipegroup.draw(screen)  # Draw the pipes

    screen.blit(ground_img, (ground_scroll, 768))  # Draw the ground

    #check for score
    if len(pipegroup) > 0:
        if birdgroup.sprites()[0].rect.left > pipegroup.sprites()[0].rect.left\
            and birdgroup.sprites()[0].rect.right < pipegroup.sprites()[0].rect.right\
            and passthepipe == False:
            passthepipe = True
        if passthepipe == True:
            if birdgroup.sprites()[0].rect.left > pipegroup.sprites()[0].rect.right:
                score += 1
                score_sound.play()
                passthepipe = False

    draw_text(str(score), font, white, int(gamewidth / 2), 20)  # Draw the score

#check for collisions
    if pygame.sprite.groupcollide(birdgroup, pipegroup, False, False) or flappy.rect.top < 0:
        gameover = True

    #falling ground
    if flappy.rect.bottom >= 768:
        gameover = True
        flying = False
        flappy.rect.bottom = 768

    if gameover and not hit_played:
        hit_sound.play()
        hit_played = True


    if gameover == False and flying == True:
        # Generate new pipes at intervals
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe > pipefreq:
            pipeheight = random.randint(-100, 100)  # Random height for the pipes
            pipebtm = Pipe(gamewidth, int(gameheight / 2) + pipeheight, -1)  # Bottom pipe
            pipetop = Pipe(gamewidth, int(gameheight / 2) + pipeheight, 1)  # Top pipe
            pipegroup.add(pipebtm)
            pipegroup.add(pipetop)
            last_pipe = current_time

        #ground scrolling    
        ground_scroll -= ground_scroll_change  # Update ground scroll position
        if abs(ground_scroll) > 35:  # Reset ground scroll position
            ground_scroll = 0
        pipegroup.update()

    #game over screen
    if gameover == True:
        if button.draw() == True:
            gameover = False
            score = reset_game()
            hit_played = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and gameover == False:
            flying = True
    pygame.display.update()  # Update the display
pygame.quit()  # Quit the game