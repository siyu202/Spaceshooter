"""
EN.540.635 Software Carpentry
Final Project - Space shooter game
"""
import os
import random
import pygame

pygame.init()
pygame.font.init()
# Initializing pygame window
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# load img
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pinkenemy.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "greenenemy.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "blueenemy.png"))
MEDPACK_IMG = pygame.image.load(os.path.join("assets", "medpack.png"))

# player ship
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "catship.png"))

# lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
PLAYER_LASER = pygame.image.load(os.path.join("assets", "bullet.png"))
PLAYER_LASER2 = pygame.image.load(os.path.join("assets", "bullet2.png"))

# bk ground
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bk.png")), (WIDTH, HEIGHT))
BG2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bk2.png")), (WIDTH, HEIGHT))
BG3 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bk3.png")), (WIDTH, HEIGHT))

# background sound
pygame.mixer.music.load('Legendary.mp3')
pygame.mixer.music.play(-1)


class Laser:
    """
    This is the laser object, each laser(either enemies' or player's) will be an individual Laser obj

    **Attributes**
        x: *int*, x value of a laser
        y: *int*, y value of a laser
        img: *img*, the image of the laser
        mask: *mask*, the mask of the image(basically a cropped-out image)
    """
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        """
        This will draw the lasers onto the window

        **Parameters**
            self
            window: defined pygame's display

        **Returns**
            None
        """
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        """
        This will update laser's y value

        **Parameters**
            self
            vel: *int*, velocity of the laser

        **Returns**
            None
        """
        self.y += vel

    def out_boundry(self, height):
        """
        This will check if a laser went outside of the window or not

        **Parameters**
            self
            height: *int*, the height of the window

        **Returns**
            T/F: check if (y value of the laser is in the boundary) is false
        """
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        """
        This will check if a laser hits an object or not

        **Parameters**
            self
            obj: *obj*, another object can be enemy ship or player ship

        **Returns**
            Return the result of the collide function(of two objects)
        """
        return collide(self, obj)


class Ship:
    COOLDOWN = 15
    """
    This is the ship object, either enemies' or player's will be a child of this obj

    **Attributes**
        x: *int*, x value of a ship
        y: *int*, y value of a ship
        ship_img: *img*, updated later in their own classes
        laser_img: *img*, same above
        lasers: *list*, the list of lasers of a particular ship
        health: *int*, the health of a ship
        cool_down_counter: *int*, the CD counter of laser shooting(only able to shoot when CD=0)
    """
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.health = health
        self.cool_down_counter = 0

    def draw(self, window):
        """
        This will draw the lasers onto the window, using the Laser's draw method

        **Parameters**
            self
            window: defined pygame's display

        **Returns**
            None
        """
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def cooldown(self):
        """
        This will set the cool down counter of a ship. Notice it resets to 0 when > 15, because
        we are running 60fps, thus limiting all ship to shoot only every quarter second.
        **Parameters**
            self

        **Returns**
            None
        """
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def move_lasers(self, vel, obj):
        """
        This will move the lasers of a ship.
        **Parameters**
            self
            vel: *int*, the velocity of the laser
            obj: *ship*, another ship to be hit by a laser

        **Returns**
            None
        """
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.out_boundry(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def shoot(self):
        """
        This will decide if a ship will shoot during a particular cycle run(remember 60 fps)
        If yes, then counter goes to 1, creates a laser with the same y and x(calibrated to +35 due to image
        of the ship) value of the ship, and then append to the lasers list(of that ship)
        **Parameters**
            self

        **Returns**
            None
        """
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 35, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class MEDPACK:
    """
    This is the MEDPACK object, a medical package to restore health of the player ship

    **Attributes**
        x: *int*, x value of a medpack
        y: *int*, y value of a medpack
        img: *img*, medpack image
        mask: *mask*, mask of the medpack
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = MEDPACK_IMG
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, vel):
        """
        This will move the medpack
        **Parameters**
            self
            vel: *int*, the moving speed of medpack

        **Returns**
            None
        """
        self.y += vel

    def draw(self, window):
        """
        This draw the medpack onto the window
        **Parameters**
            self
            vel: *int*, the moving speed of medpack

        **Returns**
            None
        """
        window.blit(self.img, (self.x, self.y))


class Player(Ship):
    """
    This is the Player object, a child of the ship object

    **Attributes**
        x: *int*, x value of the player ship
        y: *int*, y value of the player ship
        ship_img: *img*, player ship image
        laser_img: *img*, player ship laser image
        mask: *mask*, mask of the player ship
        max_health: *int*, health of the player ship
        score: *int*, player score
    """
    def __init__(self, x, y, health=100, score=0):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.laser_img = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = score

    def shoot(self):
        """
        This lets the player shoot lasers. Notice after reached 800 pts, player gets the double-rocket lasers,
        this is by switch the laser image. Then, similar to the shooting mechanism of the SHIP class, if CD = 0,
        player can shoot laser. With added sound.
        **Parameters**
            self

        **Returns**
            None
        """
        if self.score >= 800:
            self.laser_img = PLAYER_LASER2

        if self.cool_down_counter == 0:
            laser = Laser(self.x + 35, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            bullet_sound = pygame.mixer.Sound('gun shot.wav')
            bullet_sound.play()

    def move_lasers(self, vel, objs):
        """
        This moves the laser of the player ship, if laser is out of boundary, it will be removed. Else, it
        check if it collides with an enemy ship, if yes, the enemy is removed and so as the laser. Score will
        be updated += 10 with added sound
        **Parameters**
            self
            vel: *int*, the moving speed of lasers
            obj: *SHIP*, another ship to be hit by a laser

        **Returns**
            None
        """
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.out_boundry(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        collide_sound = pygame.mixer.Sound('collide.wav')
                        collide_sound.play()
                        self.score += 10
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        """
        This draws the health bar of the player ship. It first draw the red bar(its max health), then covers
        the red bar with a green bar(which length will be the proportional to current health)
        **Parameters**
            self
            window: PYgame window

        **Returns**
            None
        """
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10))

    def draw(self, window):
        """
        This draws the player ship as well as the healthbar
        **Parameters**
            self
            window: PYgame window

        **Returns**
            None
        """
        super().draw(window)
        self.healthbar(window)


class Enemy(Ship):
    """
    This is the Enemy ship object, a child of the ship object. It can be either
    red green or blue.

    **Attributes**
        x: *int*, x value of the enemy ship
        y: *int*, y value of the enemy ship
        ship_img: *img*, enemy ship image
        laser_img: *img*, enemy ship laser image
        mask: *mask*, mask of the enemy ship
    """
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color):
        super().__init__(x, y)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        """
        This moves the enemy ship
        **Parameters**
            self
            vel: *int*, the moving speed of enemy ship

        **Returns**
            None
        """
        self.y += vel

    def shoot(self):
        """
        This lets the enemy ship shoot lasers. Similar mechanism as before, each ship have
        their own counter. When cd=0, they can shoot, in here the laser imgs are calibrated -20
        **Parameters**
            self

        **Returns**
            None
        """
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    """
    This tells if two objects are colliding each other by using their masks. If their
    pixels are touching then they are definitely colliding.
    **Parameters**
        obj1: *obj*, can be ship or laser
        obj2: *obj*, can be ship or laser

    **Returns**
        T/F: Either the set of touching pixels are none or some.
    """
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def pause_game():
    """
    This lets the user to pause the game. If pygame reached a event of player
    hit p(in later function). The function will loop until player hit c to continue.
    While stuck, the screen will prompt the user to know how to unpause.
    **Parameters**
        None
    **Returns**
        None
    """
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    paused = False
            if event.type == pygame.QUIT:
                quit()

        title_font = pygame.font.SysFont("comicsans", 70)
        pause_label = title_font.render('Game paused', 1, (255, 255, 255))
        continue_label = title_font.render('Press C to continue', 1, (255, 255, 255))
        WIN.blit(pause_label, (WIDTH / 2 - pause_label.get_width() / 2, 300))
        WIN.blit(continue_label, (WIDTH / 2 - continue_label.get_width() / 2, 350))
        pygame.display.update()


def game():
    """
    This is where the game sets up itself(with FPS, level, lives, velocities, enemy numbers etc.)
    It has a nested "redraw_window" function that keeps redraw the pygame window.
    It then uses a while loop to hold us in the game(until we lost), keep updating each command (mouse click
    keyboard downs, like moving, shooting) during the loop (clock tick is 60)

    If lost, the screen will show player's final score and back to the opening page in 3 seconds.
    The user can exit anytime by close the window.
    **Parameters**
        None
    **Returns**
        None
    """
    run = True
    FPS = 60
    level = 0
    lives = 3

    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    clock = pygame.time.Clock()

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5
    medpacks = []

    player = Player(300, 630)

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        if level == 2:
            WIN.blit(BG2, (0, 0))
        if level == 3:
            WIN.blit(BG3, (0, 0))

        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Levels: {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Scores: {player.score}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (WIDTH - level_label.get_width() - 10 - 300, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        for medpack in medpacks:
            medpack.draw(WIN)

        if lost:
            score_label = lost_font.render(f"Final Score is {player.score}", 1, (255, 255, 255))
            lost_label = lost_font.render(f"You Lost :(", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 300))
            WIN.blit(score_label, (WIDTH / 2 - score_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 2:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
            medpack = MEDPACK(random.randrange(50, WIDTH - 100), -1500)
            medpacks.append(medpack)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            pause_game()
        if keys[pygame.K_LEFT] and player.x + player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel < WIDTH - PLAYER_SHIP.get_width():  # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y + player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel < HEIGHT - PLAYER_SHIP.get_height() - 15:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for medpack in medpacks[:]:
            medpack.move(enemy_vel)
            if collide(medpack, player):
                player.health = 100
                med_sound = pygame.mixer.Sound('med.wav')
                med_sound.play()
                medpacks.remove(medpack)
            elif medpack.y + MEDPACK_IMG.get_height() > HEIGHT:
                medpacks.remove(medpack)

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                collide_sound = pygame.mixer.Sound('collide.wav')
                collide_sound.play()

            elif enemy.y + enemy.ship_img.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main():
    """
    This starts the pygame with a front page. Only if the player follows the prompt:
    press the mouse, the game will start.
    **Parameters**
        None
    **Returns**
        None
    """
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                game()

    pygame.quit()


main()
