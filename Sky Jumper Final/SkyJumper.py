import pygame
from pygame import mixer
import time

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

#Loading Sounds
running_fx = pygame.mixer.Sound('running.wav')
running_fx.set_volume(0.5)
music_fx = pygame.mixer.Sound('music.wav')
music_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('jump.wav')
jump_fx.set_volume(0.5)
door_fx = pygame.mixer.Sound('door.wav')
door_fx.set_volume(0.5)
bird_fx = pygame.mixer.Sound('bird.wav')
bird_fx.set_volume(0.5)

music_fx.play(-1) #Plays music_fx on infinite loop

class Game: # Initializes the game, creates the game window, and sets up the game loop. Has methods for showing the start screen, running the main game loop, and updating the timer during the game.
    def __init__(self):
        pygame.init()
        self.screen_width = 540  # Increased the screen width to accommodate the timer
        self.screen_height = 500
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Stick Man")
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load("background.gif").convert()
        self.bg = pygame.transform.scale(self.bg, (self.screen_width, self.screen_height))
        self.start_screen_bg = pygame.image.load("Start_screen.gif").convert()  # Load the start screen background image
        self.start_screen_bg = pygame.transform.scale(self.start_screen_bg, (self.screen_width, self.screen_height))  # Scale it to match the screen dimensions
        self.sprites = []
        self.running = True
        self.start_time = time.time() 

    def show_start_screen(self): # Displays the start screen with a title and prompt to start the game. Runs in a loop until the player presses the space bar to start the game. 
        font = pygame.font.Font(None, 74)
        
        title_text = font.render("Sky Jumper", True, (255, 255, 255))
        start_text = font.render("Press Space to Start", True, (255, 255, 255))
        
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        start_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        
        start_screen = True
        while start_screen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        start_screen = False

            self.screen.blit(self.start_screen_bg, (0, 0))

            self.screen.blit(title_text, title_rect)
            self.screen.blit(start_text, start_rect)

            pygame.display.flip()

            self.clock.tick(60)

    def main_loop(self): # Main game loop. Handles events such as controlling the stick figure sprite's movements. Also updates the screen by moving sprites and drawing them, as well as updating the timer and limiting the frame rate
        self.show_start_screen()  # Show the start screen before the main loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # Handle key press events
                    if event.key == pygame.K_LEFT:
                        # Call turn_left only on StickFigureSprite instances
                        for sprite in self.sprites:
                            if isinstance(sprite, StickFigureSprite):
                                sprite.turn_left()
                    elif event.key == pygame.K_RIGHT:
                        # Call turn_right only on StickFigureSprite instances
                        for sprite in self.sprites:
                            if isinstance(sprite, StickFigureSprite):
                                sprite.turn_right()
                    elif event.key == pygame.K_SPACE:
                        # Call jump only on StickFigureSprite instances
                        for sprite in self.sprites:
                            if isinstance(sprite, StickFigureSprite):
                                sprite.jump()

            self.screen.blit(self.bg, (0, 0))
            for sprite in self.sprites:
                sprite.move()
                self.screen.blit(sprite.image, sprite.rect.topleft)

            self.update_timer()
            pygame.display.flip()
            self.clock.tick(60)

    def update_timer(self): # Updates and displays the elapsed time on the top-right corner of the screen
        current_time = int(time.time() - self.start_time)
        font = pygame.font.Font(None, 36)
        timer_text = font.render(f"Time: {current_time}s", True, (255, 255, 255))
        self.screen.blit(timer_text, (self.screen_width - 150, 20))

class Coords: # Represents the coordinates of a sprite or game object. Contains attributes for x1, y1 (top-left corner) and x2, y2 (bottom-right corner) of a rectangle.
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

class Sprite: # Base class for other sprites in the game. Contains a reference to the game instance.
    def __init__(self, game):
        self.game = game
        self.endgame = False
        self.coordinates = None

    def move(self): 
        pass

    def coords(self):
        return self.coordinates

class Timer: # Manages and displays the game timer. Initializes the timer with the start time. Updates and draws the timer on the screen.
    def __init__(self, game):
        self.game = game
        self.start_time = time.time() 
        self.font = pygame.font.Font(None, 36) 

    def update(self):
        elapsed_time = int(time.time() - self.start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        self.time_str = f"{minutes:02}:{seconds:02}"

    def draw(self):
        timer_surface = self.font.render(self.time_str, True, (255, 255, 255))
        self.game.screen.blit(timer_surface, (self.game.screen_width - 100, 10))

class StickFigureSprite(Sprite): # Represents the player's stick figure sprite. Handles player movement (left, right, jump). Animates the stick figure sprite and checks for collisions with other sprites.
    def __init__(self, game):
        Sprite.__init__(self, game)
        self.image = pygame.image.load("figure-L1.gif")
        self.rect = self.image.get_rect(topleft=(200, 470))
        self.x = 0
        self.y = 0
        self.current_image = 0
        self.current_image_add = 1
        self.jump_count = 0
        self.last_time = time.time()
        self.last_bird_sound_time = 0
        self.bird_sound_cooldown = 1
        self.is_moving = False

    def turn_left(self): # Called when the left arrow key is pressed. Sets the stick figure's horizontal speed to -2 to move left and starts playing the running sound
        if self.y == 0:
            if self.x == 0:
                running_fx.play(loops=-1)  #Plays running_fx on loop
            self.x = -2
            self.is_moving = True

    def turn_right(self): # Called when the right arrow key is pressed. Sets the stick figure's horizontal speed to 2 to move right and starts playing the running sound
        if self.y == 0:
            if self.x == 0:
                running_fx.play(loops=-1)  #Also plays running_fx on loop
            self.x = 2
            self.is_moving = True

    def stop_moving(self): #Stops the stick figure from moving and stops playing the running sound
        if self.is_moving:
            running_fx.stop()  #Stops running_fx when stationary
            self.is_moving = False
        self.x = 0

    def jump(self): # Called when the space bar is pressed. Sets the stick figure's vertical speed to -4 to start a jump and plays the jump sound
        if self.y == 0:
            self.y = -4
            self.jump_count = 0
            jump_fx.play() #Plays jump_fx when the spacebar is pressed

    def animate(self): # Handles the stick figure sprite's animations based on its movement and jumping status. Loads different images for different actions such as jumping and running
        if self.x != 0 and self.y == 0:
            if time.time() - self.last_time > 0.1:
                self.last_time = time.time()
                self.current_image += self.current_image_add
                if self.current_image >= 2:
                    self.current_image_add = -1
                if self.current_image <= 0:
                    self.current_image_add = 1
        if self.x < 0:
            if self.y != 0:
                self.image = pygame.image.load("figure-L3.gif")
            else:
                self.image = pygame.image.load(f"figure-L{self.current_image + 1}.gif")
        elif self.x > 0:
            if self.y != 0:
                self.image = pygame.image.load("figure-R3.gif")
            else:
                self.image = pygame.image.load(f"figure-R{self.current_image + 1}.gif")

    def coords(self): # Returns a Coords object representing the coordinates of the stick figure sprite
        return Coords(self.rect.left, self.rect.top, self.rect.right, self.rect.bottom)

    def move(self): # Handles the stick figure sprite's movement, as well as checking for collisions with platforms, doors, and obstacles. Updates the stick figure's position and plays sounds for certain events
        self.animate()
        if self.y < 0:
            self.jump_count += 1
            if self.jump_count > 20:
                self.y = 4
        if self.y > 0:
            self.jump_count -= 1
        co = self.coords()
        left = True
        right = True
        top = True
        bottom = True
        falling = True
        if self.y > 0 and co.y2 >= self.game.screen_height:
            self.y = 0
            bottom = False
        elif self.y < 0 and co.y1 <= 0:
            self.y = 0
            top = False
        if self.x > 0 and co.x2 >= self.game.screen_width:
            self.x = 0
            right = False
        elif self.x < 0 and co.x1 <= 0:
            self.x = 0
            left = False
        for sprite in self.game.sprites:
            if sprite == self:
                continue
            sprite_co = sprite.coords()
            if isinstance(sprite, DoorSprite):
                if collided_left(co, sprite_co) or collided_right(co, sprite_co) or \
                collided_top(co, sprite_co) or collided_bottom(self.y, co, sprite_co):
                    door_fx.play()  #Plays door_fx when the player reaches the door
                    pygame.time.delay(500) #500 ms delay so that the sound is actually audible before the game ends
                    self.game.running = False  #Game ends
            if isinstance(sprite, ObstacleSprite) and (
                collided_left(co, sprite_co) or
                collided_right(co, sprite_co) or
                collided_top(co, sprite_co) or
                collided_bottom(self.y, co, sprite_co)
            ):
                current_time = time.time()
                if current_time - self.last_bird_sound_time > self.bird_sound_cooldown:
                    bird_fx.play() #Created a cooldown for bird_fx of 1 second so it doesn't repeat if the player collides with a bird
                    self.last_bird_sound_time = current_time
            if top and self.y < 0 and collided_top(co, sprite_co):
                self.y = -self.y
                top = False
            if bottom and self.y > 0 and collided_bottom(self.y, co, sprite_co):
                self.y = sprite_co.y1 - co.y2
                if self.y < 0:
                    self.y = 0
                bottom = False
                top = False
            if bottom and falling and self.y == 0 and co.y2 < self.game.screen_height and collided_bottom(1, co, sprite_co):
                falling = False
            if left and self.x < 0 and collided_left(co, sprite_co):
                self.x = 0
                left = False
                if sprite.endgame:
                    self.end(sprite)
            if right and self.x > 0 and collided_right(co, sprite_co):
                self.x = 0
                right = False
                if sprite.endgame:
                    self.end(sprite)
        if falling and bottom and self.y == 0 and co.y2 < self.game.screen_height:
            self.y = 4
        if self.x == 0 and self.is_moving:
            self.stop_moving()
        self.rect.x += self.x
        self.rect.y += self.y

class PlatformSprite(Sprite): # Represents a platform sprite in the game. Takes in the game instance, image path, and position and dimensions of the platform. Initializes the sprite and its coordinates.
    def __init__(self, game, image_path, x, y, width, height):
        Sprite.__init__(self, game)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.coordinates = Coords(x, y, x + width, y + height)

class DoorSprite(Sprite): # Represents the door sprite in the game. Takes in the game instance, position, and dimensions of the door. Initializes the sprite and its coordinates. 
    def __init__(self, game, x, y, width, height):
        Sprite.__init__(self, game)
        self.closed_door = pygame.image.load("door1.gif")
        self.open_door = pygame.image.load("door2.gif")
        self.image = self.closed_door
        self.rect = self.image.get_rect(topleft=(x, y))
        self.coordinates = Coords(x, y, x + (width / 2), y + height)
        self.endgame = True

    def opendoor(self): # Changes the door sprite's image to show the door as open
        self.image = self.open_door

    def closedoor(self): # Changes the door sprite's image to show the door as closed
        self.image = self.closed_door

def within_x(co1, co2): # Checks if two coordinates overlap in the x-axis
    return (co1.x1 > co2.x1 and co1.x1 < co2.x2) or (co1.x2 > co2.x1 and co1.x2 < co2.x2) or (co2.x1 > co1.x1 and co2.x1 < co1.x2) or (co2.x2 > co1.x1 and co2.x2 < co1.x1)

def within_y(co1, co2): # Checks if two coordinates overlap in the y-axis
    return (co1.y1 > co2.y1 and co1.y1 < co2.y2) or (co1.y2 > co2.y1 and co1.y2 < co2.y2) or (co2.y1 > co1.y1 and co2.y1 < co1.y2) or (co2.y2 > co1.y1 and co2.y2 < co1.y1)

def collided_left(co1, co2): # Checks if co1's left side collides with co2
    return within_y(co1, co2) and co1.x1 <= co2.x2 and co1.x1 >= co2.x1

def collided_right(co1, co2): # Checks if co1's right side collides with co2
    return within_y(co1, co2) and co1.x2 >= co2.x1 and co1.x2 <= co2.x2

def collided_top(co1, co2): # Checks if co1's top collides with co2
    return within_x(co1, co2) and co1.y1 <= co2.y2 and co1.y1 >= co2.y1

def collided_bottom(y, co1, co2): # Checks if co1's bottom collides with co2's top considering the y-value
    y_calc = co1.y2 + y
    return within_x(co1, co2) and y_calc >= co2.y1 and y_calc <= co2.y2

class ObstacleSprite(Sprite): # Represents an obstacle sprite in the game. Takes in the game instance, position, dimensions, speed, and range of movement. Initializes the sprite and its coordinates. Contains a method to move the obstacle within a specified range and change direction upon reaching the range limits. 
    def __init__(self, game, x, y, width, height, speed, range_min, range_max):
        Sprite.__init__(self, game)
        
        image_right_path = "obstacle_right.gif"
        image_left_path = "obstacle_left.gif"
        
        self.image_right = pygame.image.load(image_right_path)
        self.image_left = pygame.image.load(image_left_path)
        
        self.image_right = pygame.transform.scale(self.image_right, (width, height))
        self.image_left = pygame.transform.scale(self.image_left, (width, height))
        
        self.image = self.image_right
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.coordinates = Coords(x, y, x + width, y + height)
        
        self.speed = speed
        self.direction = 1  # Start moving to the right
        self.range_min = range_min
        self.range_max = range_max

    def move(self): # Handles the movement of obstacle sprites within a specified range. Changes the sprite's image depending on the direction of movement
        self.rect.x += self.speed * self.direction
        self.coordinates.x1 += self.speed * self.direction
        self.coordinates.x2 += self.speed * self.direction

        if self.rect.x <= self.range_min:
            self.direction = 1
            self.image = self.image_right  
        elif self.rect.x >= self.range_max:
            self.direction = -1
            self.image = self.image_left 

g = Game()
platform1 = PlatformSprite(g, "platform1.gif", 0, 480, 100, 10)
platform2 = PlatformSprite(g, "platform1.gif", 150, 440, 100, 10)
platform3 = PlatformSprite(g, "platform1.gif", 300, 400, 100, 10)
platform4 = PlatformSprite(g, "platform1.gif", 300, 160, 100, 10)
platform5 = PlatformSprite(g, "platform2.gif", 175, 350, 66, 10)
platform6 = PlatformSprite(g, "platform2.gif", 50, 300, 66, 10)
platform7 = PlatformSprite(g, "platform2.gif", 170, 120, 66, 10)
platform8 = PlatformSprite(g, "platform2.gif", 45, 60, 66, 10)
platform9 = PlatformSprite(g, "platform3.gif", 170, 250, 32, 10)
platform10 = PlatformSprite(g, "platform3.gif", 230, 200, 32, 10)

g.sprites.extend([platform1, platform2, platform3, platform4, platform5, platform6, platform7, platform8, platform8, platform9, platform10])

door = DoorSprite(g, 45, 30, 40, 35)
g.sprites.append(door)

sf = StickFigureSprite(g)
g.sprites.append(sf)

obstacle = ObstacleSprite(g, 170, 50, 25, 15, speed=3, range_min=150, range_max=300)
g.sprites.append(obstacle)

obstacle = ObstacleSprite(g, 170, 180, 25, 15, speed=2, range_min=150, range_max=300)
g.sprites.append(obstacle)

obstacle = ObstacleSprite(g, 170, 360, 25, 15, speed=1, range_min=200, range_max=350)
g.sprites.append(obstacle)

g.main_loop()