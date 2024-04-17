import pygame
import time

class GameSystem:
    def __init__(self):
        pygame.init()
        self.screen_width = 600
        self.screen_height = 500
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Stick Man")
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load("background.png").convert()
        self.bg = pygame.transform.scale(self.bg, (self.screen_width, self.screen_height))
        self.sprites = []
        self.running = False
        self.game_over = False
        self.start_button_rect = pygame.Rect(250, 200, 100, 50)
        self.exit_button_rect = pygame.Rect(250, 300, 100, 50)
        self.start_time = None

    def main(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.start_button_rect.collidepoint(mouse_pos):
                        self.start_game()
                    elif self.exit_button_rect.collidepoint(mouse_pos):
                        self.running = False

            self.screen.blit(self.bg, (0, 0))

            pygame.draw.rect(self.screen, (0, 255, 0), self.start_button_rect)
            pygame.draw.rect(self.screen, (255, 0, 0), self.exit_button_rect)
            font = pygame.font.Font(None, 36)
            start_text = font.render("START", True, (255, 255, 255))
            exit_text = font.render("EXIT", True, (255, 255, 255))
            self.screen.blit(start_text, (self.start_button_rect.centerx - start_text.get_width() // 2,
                                           self.start_button_rect.centery - start_text.get_height() // 2))
            self.screen.blit(exit_text, (self.exit_button_rect.centerx - exit_text.get_width() // 2,
                                          self.exit_button_rect.centery - exit_text.get_height() // 2))

            pygame.display.flip()
            self.clock.tick(60)

    def start_game(self):
        self.running = False
        g = Game()
        platform1 = PlatformSprite(g, "platform1.png", 0, 480, 100, 10)  
        platform2 = PlatformSprite(g, "platform1.png", 150, 440, 100, 10)  
        platform3 = PlatformSprite(g, "platform1.png", 300, 400, 100, 10)  
        platform4 = SlowPlatformSprite(g, "platform1.png", 285, 160, 110, 10)  
        platform5 = PlatformSprite(g, "platform2.png", 175, 350, 66, 10)  
        platform6 = SlowPlatformSprite(g, "platform2.png", 50, 300, 90, 10)  
        platform7 = PlatformSprite(g, "platform2.png", 170, 120, 66, 10)  
        platform8 = SlowPlatformSprite(g, "platform2.png", 45, 60, 100, 10)  
        platform9 = PlatformSprite(g, "platform3.png", 170, 250, 32, 10)  
        platform10 = PlatformSprite(g, "platform3.png", 230, 200, 32, 10)  

        g.sprites.extend([platform1, platform2, platform3, platform4, platform5, platform6, platform7, platform8, platform8, platform9, platform10])

        door = DoorSprite(g, 45, 30, 40, 35)
        g.sprites.append(door)

        sf = StickFigureSprite(g)
        g.sprites.append(sf)

        g.main_loop()

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 600
        self.screen_height = 500
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Stick Man")
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load("background.png").convert()  
        self.bg = pygame.transform.scale(self.bg, (self.screen_width, self.screen_height))
        self.sprites = []
        self.running = True
        self.game_over_text = None
        self.out = None
        self.start_time = time.time()

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.sprites[-1].turn_left()
                    elif event.key == pygame.K_RIGHT:
                        self.sprites[-1].turn_right()
                    elif event.key == pygame.K_SPACE:
                        self.sprites[-1].jump()

            self.screen.blit(self.bg, (0, 0))

            for sprite in self.sprites:
                sprite.move()
                self.screen.blit(sprite.image, sprite.rect.topleft)

            if self.sprites[-1].endgame:
                self.display_score()
                break

            self.update_timer()
            pygame.display.flip()
            self.clock.tick(60)

    def update_timer(self):
        current_time = int(time.time() - self.start_time)
        font = pygame.font.Font(None, 36)
        timer_text = font.render(f"Time: {current_time}s", True, (255, 255, 255))
        self.screen.blit(timer_text, (self.screen_width - 150, 20))

class Coords:
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

class Sprite:
    def __init__(self, game):
        self.game = game
        self.endgame = False
        self.coordinates = None

    def move(self):
        pass

    def coords(self):
        return self.coordinates

class StickFigureSprite(Sprite):
    def __init__(self, game):
        Sprite.__init__(self, game)
        self.image = pygame.image.load("figure-L1.png")  
        self.image = pygame.transform.scale(self.image, (50, 50))  
        self.rect = self.image.get_rect(topleft=(200, 470))
        self.x = -2
        self.y = 0
        self.current_image = 0
        self.current_image_add = 1
        self.jump_count = 0
        self.last_time = time.time()
        self.speed = 2

    def turn_left(self):
        if self.y == 0:
            self.x = -self.speed

    def turn_right(self):
        if self.y == 0:
            self.x = self.speed

    def jump(self):
        if self.y == 0:
            self.y = -4
            self.jump_count = 0

    def animate(self):
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
                self.image = pygame.image.load("figure-L3.png")
            else:
                self.image = pygame.image.load(f"figure-L{self.current_image + 1}.png")
        elif self.x > 0:
            if self.y != 0:
                self.image = pygame.image.load("figure-R3.png")
            else:
                self.image = pygame.image.load(f"figure-R{self.current_image + 1}.png")

    def coords(self):
        return Coords(self.rect.left, self.rect.top, self.rect.right, self.rect.bottom)

    def move(self):
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

        for sprite in self.game.sprites:
            if isinstance(sprite, SlowPlatformSprite) and collided_bottom(1, co, sprite.coords()):
                self.speed = 1
                break
        else:
            self.speed = 2

        if falling and bottom and self.y == 0 and co.y2 < self.game.screen_height:
            self.y = 4
        self.rect.x += self.x
        self.rect.y += self.y

class PlatformSprite(Sprite):
    def __init__(self, game, image_path, x, y, width, height):
        Sprite.__init__(self, game)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.coordinates = Coords(x, y, x + width, y + height)

class SlowPlatformSprite(PlatformSprite):
    pass

class DoorSprite(Sprite):
    def __init__(self, game, x, y, width, height):
        Sprite.__init__(self, game)
        self.closed_door = pygame.image.load("door1.png")
        self.open_door = pygame.image.load("door2.png")
        self.image = self.closed_door
        self.rect = self.image.get_rect(topleft=(x, y))
        self.coordinates = Coords(x, y, x + (width / 2), y + height)
        self.endgame = True

    def opendoor(self):
        self.image = self.open_door

    def closedoor(self):
        self.image = self.closed_door

def within_x(co1, co2):
    return (co1.x1 > co2.x1 and co1.x1 < co2.x2) or (co1.x2 > co2.x1 and co1.x2 < co2.x2) or (co2.x1 > co1.x1 and co2.x1 < co1.x2) or (co2.x2 > co1.x1 and co2.x2 < co1.x1)

def within_y(co1, co2):
    return (co1.y1 > co2.y1 and co1.y1 < co2.y2) or (co1.y2 > co2.y1 and co1.y2 < co2.y2) or (co2.y1 > co1.y1 and co2.y1 < co1.y2) or (co2.y2 > co1.y1 and co2.y2 < co1.y1)

def collided_left(co1, co2):
    return within_y(co1, co2) and co1.x1 <= co2.x2 and co1.x1 >= co2.x1

def collided_right(co1, co2):
    return within_y(co1, co2) and co1.x2 >= co2.x1 and co1.x2 <= co2.x2

def collided_top(co1, co2):
    return within_x(co1, co2) and co1.y1 <= co2.y2 and co1.y1 >= co2.y1

def collided_bottom(y, co1, co2):
    y_calc = co1.y2 + y
    return within_x(co1, co2) and y_calc >= co2.y1 and y_calc <= co2.y2

g = GameSystem()
g.main()
