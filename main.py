import pygame as pg
import random
import time
import os

pg.font.init()

WIDTH, HEIGHT = 950, 1000
WIN = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Space Invaders")

# Load images

# BackGround
BACK_GROUND = pg.transform.scale(pg.image.load(os.path.join("assets", "Background.png")), (WIDTH, HEIGHT))

# Ships
RED_ENEMY = pg.transform.scale(pg.image.load(os.path.join("assets", "EnemyRed.png")), (50 , 75))
GREEN_ENEMY = pg.transform.scale(pg.image.load(os.path.join("assets", "EnemyGreen.png")), (50 , 75))
BLUE_ENEMY = pg.transform.scale(pg.image.load(os.path.join("assets", "EnemyBlue.png")), (50 , 75))
METEOR = pg.transform.scale(pg.image.load(os.path.join("assets", "Meteor.png")), (75 , 75))
PLAYER = pg.transform.scale(pg.image.load(os.path.join("assets", "PlayerShip.png")), (100, 100))

# Explosions
EXPLOSION_1 = pg.transform.scale(pg.image.load(os.path.join("assets", "Explosion1.png")), (30 , 30))
EXPLOSION_2 = pg.transform.scale(pg.image.load(os.path.join("assets", "Explosion2.png")), (40 , 40))
EXPLOSION_3 = pg.transform.scale(pg.image.load(os.path.join("assets", "Explosion3.png")), (55 , 55))
EXPLOSION_4 = pg.transform.scale(pg.image.load(os.path.join("assets", "Explosion4.png")), (65 , 65))
EXPLOSION_5 = pg.transform.scale(pg.image.load(os.path.join("assets", "Explosion5.png")), (75 , 75))
EXPLOSION_6 = pg.transform.scale(pg.image.load(os.path.join("assets", "Explosion6.png")), (80 , 80))
EXPLOSION_7 = pg.transform.scale(pg.image.load(os.path.join("assets", "Explosion7.png")), (100 , 100))

# Bullets
RED_LASER = pg.transform.scale(pg.image.load(os.path.join("assets", "RedLaser.png")), (5, 45))
GREEN_LASER = pg.transform.scale(pg.image.load(os.path.join("assets", "GreenLaser.png")), (5, 45))
BLUE_LASER = pg.transform.scale(pg.image.load(os.path.join("assets", "BlueLaser.png")), (5, 45))
YELLOW_LASER = pg.transform.scale(pg.image.load(os.path.join("assets", "YellowLaser.png")), (5, 45))

# Boosts
HEALTH_BOOST = pg.transform.scale(pg.image.load(os.path.join("assets", "Health.png")), (40, 40))
FIRE_RATE_BOOST = pg.transform.scale(pg.image.load(os.path.join("assets", "FireRate.png")), (40, 40))
GUN_BOOST = pg.transform.scale(pg.image.load(os.path.join("assets", "GunUpgrade.png")), (40, 40))

class Laser:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pg.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img , (self.x , self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Explosion:
    MAP = {
            1: (EXPLOSION_1),
            2: (EXPLOSION_2),
            3: (EXPLOSION_3),
            4: (EXPLOSION_4),
            5: (EXPLOSION_5),
            6: (EXPLOSION_6),
            7: (EXPLOSION_7)
          }

    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.img = self.MAP[type]
        self.mask = pg.mask.from_surface(self.img)

    def type_change(self):
        self.type += 1

    def draw(self, window):
        window.blit(self.img , (self.x , self.y))

class Boost:

    MAP = {
                "health":(HEALTH_BOOST),
                "firerate":(FIRE_RATE_BOOST),
                "gun":(GUN_BOOST)
           }

    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.img = self.MAP[type]
        self.mask = pg.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img , (self.x , self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.aimg.get_height()

class Meteor:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = METEOR
        self.mask = pg.mask.from_surface(self.img)

    def collision(self, obj):
        return collide(self, obj)

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height()

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def move(self, vel):
        self.y += vel

    def draw(self, window):
        window.blit(self.img , (self.x , self.y))

class Ship:

    def __init__(self, x, y, bullet, health = 100, cd = 40):
        self.x = x
        self.y = y
        self.health = health
        self.cd= cd
        self.ship_img = None
        self.ship_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x , self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.cd:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_height() / 2 - 14 , self.y + 65, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):



    def __init__(self, x, y, bullet, health = 100, cd = 40):
        super().__init__(x, y ,health)
        self.max_health = 100
        self.cd = cd
        self.bullet = bullet
        self.ship_img = PLAYER
        self.laser_img = YELLOW_LASER
        self.health =  health
        self.mask = pg.mask.from_surface(self.ship_img)


    def move_lasers(self, vel, objs1, objs2):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else :
                for obj in objs1:
                    if laser.collision(obj):
                        explosion = Explosion(int(obj.get_width() / 2 + obj.x), int(obj.get_height() / 2 + obj.y), random.randrange(1,7))
                        explosion.draw(WIN)
                        pg.display.update()
                        objs1.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                for obj in objs2:
                    if laser.collision(obj):
                        explosion = Explosion(int(obj.get_width() / 2 + obj.x), int(obj.get_height() / 2 + obj.y), random.randrange(6,7))
                        explosion.draw(WIN)
                        pg.display.update()
                        objs2.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def shoot(self):
        if self.cool_down_counter == 0:
            if self.bullet == 1:
                laser = Laser(self.x + self.get_height() / 2  , self.y -40, self.laser_img)
                self.lasers.append(laser)

            elif self.bullet == 2:
                laser = Laser(self.x + self.get_height() / 2 - 33, self.y - 20, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2 + 33, self.y - 20, self.laser_img)
                self.lasers.append(laser)

            elif self.bullet == 3:
                laser = Laser(self.x + self.get_height() / 2 - 33, self.y - 20, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2, self.y - 40, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2 + 33, self.y - 20, self.laser_img)
                self.lasers.append(laser)

            elif self.bullet == 4:
                laser = Laser(self.x + self.get_height() / 2 - 33, self.y - 20, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2 - 11, self.y - 40, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2 + 11, self.y - 40, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2 + 33, self.y - 20, self.laser_img)
                self.lasers.append(laser)

            else:
                laser = Laser(self.x + self.get_height() / 2 - 33, self.y - 20, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2 - 16, self.y - 40, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2, self.y - 40, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2 + 16, self.y - 40, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + self.get_height() / 2 + 33, self.y - 20, self.laser_img)
                self.lasers.append(laser)


            self.cool_down_counter = 1

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pg.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pg.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):

    COLOR_MAP = {
                    "red":(RED_ENEMY, RED_LASER),
                    "green":(GREEN_ENEMY, GREEN_LASER),
                    "blue":(BLUE_ENEMY, BLUE_LASER),
                }

    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pg.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

def collide(obj1, obj2):

    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():

    run = True
    FPS = 60

    clock = pg.time.Clock()
    level = 0
    lives = 3

    main_font = pg.font.SysFont("comicsans", 25)
    lost_font = pg.font.SysFont("comicsans", 70)

    player = Player(WIDTH / 2 - 50,HEIGHT - 120, 1)

    enemies = []
    wave_length = 5
    wave_range = -800
    meteors = []
    meteor_length = 3
    boosts = []
    boost_length = 1

    enemy_vel = 1
    meteor_vel = 5
    boost_vel = 5
    laser_vel = 6
    player_vel = 5

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BACK_GROUND, (0, 0))
        #Text
        lives_label = main_font.render(f"Lives:{lives}", 1, (200, 5, 5))
        level_label = main_font.render(f"Level:{level}", 1, (5, 200, 5))
        fire_rate_label = main_font.render(f"Fire Rate:{player.cd}", 1, (200, 5, 5))
        gun_level_label = main_font.render(f"Gun Level w:{player.bullet}", 1, (200, 5, 5))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(fire_rate_label, (10, 40))
        WIN.blit(gun_level_label, (10, 70))

        for enemy in enemies:
            enemy.draw(WIN)

        for boost in boosts :
            boost.draw(WIN)

        for meteor in meteors:
            meteor.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You lost!", 1,(255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2 , 350 -  lost_label.get_height() / 2))

        pg.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if player.health <= 0 and lives > 0:
            lives -= 1
            if player.bullet > 1:
                player.bullet -= 1
                player.cd -= 2
            player = Player(300, 620, player.bullet, health = 100, cd = player.cd)

        if lives <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else :
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 3
            meteor_length += 2
            wave_range -= 450

            if level % 3 == 0 :
                meteor_vel += 1
                enemy_vel += 1

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(wave_range -250 * level, -250 * level), random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

            for j in range(boost_length):
                boost = Boost(random.randrange(50, WIDTH - 100), random.randrange(-200, 50), random.choice(["firerate", "health","gun"]))
                boosts.append(boost)

            for k in range(meteor_length):
                meteor = Meteor(random.randrange(50, WIDTH - 100), random.randrange(-250 * level, -100))
                meteors.append(meteor)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()

        keys = pg.key.get_pressed()

        if ( keys[pg.K_a] or keys[pg.K_LEFT] ) and player.x + player_vel > 0: #left
            player.x -= player_vel
        if ( keys[pg.K_d] or keys[pg.K_RIGHT] ) and player.x + player_vel + player.get_width() - 1 < WIDTH: #right
            player.x += player_vel
        if ( keys[pg.K_w] or keys[pg.K_UP] ) and player.y - player_vel > 0: #up
            player.y -= player_vel
        if ( keys[pg.K_s] or keys[pg.K_DOWN] ) and player.y + player_vel + player.get_height() + 15 < HEIGHT: #down
            player.y += player_vel
        if keys[pg.K_SPACE]:
            player.shoot()


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if enemy.y + enemy.get_width() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

            if collide(enemy, player):
                player.health -= 25
                enemies.remove(enemy)
            elif random.randrange(0 , 4*FPS) == 1:
                enemy.shoot()

        for boost in boosts[:]:
            boost.move(boost_vel)

            if boost.y + boost.get_width() > HEIGHT:
                boosts.remove(boost)

            if collide(boost, player):

                if boost.type == "health":

                    if player.health == player.max_health:
                        lives += 1

                    elif player.health + 25 > player.max_health:
                        player.health = player.max_health

                    else:
                        player.health += 25
                        player = Player(player.x, player.y, player.bullet, health = player.health, cd = player.cd)

                elif boost.type == "firerate":
                    player.cd -= 2
                    player = Player(player.x, player.y, player.bullet, health = player.health, cd = player.cd)

                elif boost.type == "gun":

                    if player.bullet < 5:
                        player.bullet += 1
                        player = Player(player.x, player.y, player.bullet, health = player.health, cd = player.cd)


                boosts.remove(boost)

        for meteor in meteors[:]:
            meteor.move(meteor_vel)

            if meteor.y + meteor.get_width() > HEIGHT:
                meteors.remove(meteor)

            if collide(meteor, player):
                player.health -= 40
                meteors.remove(meteor)

        player.move_lasers(-laser_vel, enemies, meteors)

def main_menu():

    run = True
    title_font = pg.font.SysFont("comicsans", 60)

    while run:
        WIN.blit(BACK_GROUND, (0, 0))
        title_label = title_font.render("Press the mouse", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width() / 2, 225))
        title_label = title_font.render("to begin your", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 375))
        title_label = title_font.render("journey", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 525))
        pg.display.update()
        for event in pg.event.get():
            if event.type ==  pg.QUIT:
                run = False
            if event.type ==  pg.MOUSEBUTTONDOWN:
                main()

    pg.quit()

main_menu()