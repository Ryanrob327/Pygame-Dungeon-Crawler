import pygame
import os
import random
import csv
import button
import math

pygame.init()
clock = pygame.time.Clock()
wn_width = 800
wn_height = 600
screen = pygame.display.set_mode((wn_width,wn_height))

white = (255,255,255)
blue = (0,0,255)
lightblue = (68,166,198)
bg_color = (36,51,41)
red = (255,0,0)
black = (0,0,0)

rows = 150
cols = 150
tile_size = 48
tile_types = 23
x_scroll = 0
y_scroll = 0
level = 0
scroll_thresh = 200
bg_scroll = 0
MAX_LEVELS = 2
apple_frames = 0


move_up = False
move_down = False
move_right = False
move_left = False
game_over = False

img_list = []
for x in range(tile_types):
    img = pygame.image.load(f'Tileset/{x}.png')
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)

def healthbar():
    pygame.draw.rect(screen, white, (10, 10, player.max_health * 30, 25))
    pygame.draw.rect(screen, red, (10, 10, player.health * 30, 25))
    pygame.draw.rect(screen, black, (10, 10, player.max_health * 30, 25), 3)

class Ground(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
    def update(self):
        self.rect.x += x_scroll
        self.rect.y += y_scroll

def reset_level():
    bullet_group.empty()
    pollin_group.empty()
    ground_group.empty()
    bush_group.empty()
    rock_group.empty()
    flower_group.empty()

    data = []
    for row in range(rows):
        r = [-1] * cols
        data.append(r)

    return data

class Player():
    def __init__(self,x,y):
        self.speed = 12
        self.x_direction = 1
        self.y_direction = 1
        self.width = tile_size
        self.height = tile_size
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.max_health = 5
        self.health = 5

        # load all images for the players
        animation_types = ['Idle animation', 'Left animation', 'Right animation']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'Apple animation/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Apple animation/{animation}/{i}.png')
                img = pygame.transform.scale(img, (tile_size, tile_size))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def move(self):
        screen_xscroll = 0
        screen_yscroll = 0
        dy = 0
        dx = 0

        if move_up == True:
            dy = -self.speed
        if move_down == True:
            dy = self.speed
        if move_right == True:
            dx = self.speed
        if move_left == True:
            dx = -self.speed

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height): # x direction
                dx = 0
                self.x_direction *= -1
                self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): # y direction
                dy = 0
                self.y_direction *= -1
                self.move_counter = 0

        for bush in bush_group:
            if bush.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height): # x direction
                dx = 0
                self.x_direction *= -1
                self.move_counter = 0
            if bush.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): # y direction
                dy = 0
                self.y_direction *= -1
                self.move_counter = 0
        for rock in rock_group:
            if rock.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height): # x direction
                dx = 0
                self.x_direction *= -1
                self.move_counter = 0
            if rock.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): # y direction
                dy = 0
                self.y_direction *= -1
                self.move_counter = 0
        for pollin in pollin_group:
            if pollin.rect.colliderect(self.rect.x, self.rect.y, self.width, self.height):
                self.health -= 1
                pollin.kill()
        level_complete = False
        if portal.rect.colliderect(self.rect):
            level_complete = True

        self.rect.x += dx
        self.rect.y += dy
        self.rect.center = (self.rect.x + tile_size // 2, self.rect.y + tile_size // 2)


        if (self.rect.right > wn_width - scroll_thresh):
            self.rect.x -= dx
            screen_xscroll = -dx
        if (self.rect.left < scroll_thresh):
            self.rect.x -= dx
            screen_xscroll = -dx
        if (self.rect.bottom > wn_height - scroll_thresh):
            self.rect.y -= dy
            screen_yscroll = -dy
        if (self.rect.top < scroll_thresh):
            self.rect.y -= dy
            screen_yscroll = -dy

        return screen_xscroll, screen_yscroll, level_complete

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 70
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)
    def hitbox(self):
        pygame.draw.rect(screen, red,(self.rect.x, self.rect.y, self.width, self.height), 2)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size - (rows * tile_size - wn_height)
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 7 or tile >= 13 and tile <= 16: # tiles with collision
                        self.obstacle_list.append(tile_data)
                    if tile >= 8 and tile <= 12 or tile == 17: # ground tiles
                        ground = Ground(img, x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                        ground_group.add(ground)
                    if tile == 18:
                        grass = Ground(img_list[8], x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                        ground_group.add(grass)
                        player = Player(x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                    if tile == 19:
                        grass = Ground(img_list[8], x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                        ground_group.add(grass)
                        bush = Bush(img_list[19], x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                        bush_group.add(bush)
                    if tile == 20:
                        grass = Ground(img_list[8], x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                        ground_group.add(grass)
                        rock = Rock(x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                        rock_group.add(rock)
                    if tile == 21:
                        grass = Ground(img_list[8], x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                        ground_group.add(grass)
                        flower = Flower(x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                        flower_group.add(flower)
                    if tile == 22:
                        grass = Ground(img_list[8], x * tile_size, y * tile_size - (rows * tile_size - wn_height))
                        ground_group.add(grass)
                        portal = Portal(x * tile_size, y * tile_size - (rows * tile_size - wn_height))



        return player, portal

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += x_scroll
            tile[1][1] += y_scroll
            screen.blit(tile[0],tile[1])

    def hitbox(self):
        for tile in self.obstacle_list:
            pygame.draw.rect(screen, blue, tile[1], 2)

class Bush(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
    def update(self):
        self.rect.x += x_scroll
        self.rect.y += y_scroll
        for bullet in bullet_group:
            if self.rect.colliderect(bullet.rect):
                self.kill()
                bullet.kill()

class Rock(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.img = pygame.image.load(f'Tileset/20.png')
        self.image = pygame.transform.scale(self.img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
    def update(self):
        self.rect.x += x_scroll
        self.rect.y += y_scroll
        for bullet in bullet_group:
            if pygame.sprite.spritecollide(bullet, rock_group, False):
                bullet.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Bullet.png').convert_alpha()
        self.image = pygame.transform.scale(img, (10, 10))
        self.pos = (x, y)
        mx, my = pygame.mouse.get_pos()
        self.dir = (mx - x, my - y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0]/length, self.dir[1]/length)

        self.speed = 20
        self.rect = self.image.get_rect()

    def update(self):
        self.pos = (self.pos[0]+self.dir[0]*self.speed + x_scroll,
                    self.pos[1]+self.dir[1]*self.speed + y_scroll)

        #for tile in world.obstacle_list:
            #if tile[1].colliderect(self.rect):
                #self.kill()
        self.rect.center = self.pos
        #pygame.draw.rect(screen,white, self.rect, 4)
        screen.blit(self.image, self.rect)

class Flower(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Tileset/21.png').convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.update_time = pygame.time.get_ticks()
        self.health = 1
    def update(self):
        self.rect.x += x_scroll
        self.rect.y += y_scroll

        cooldown = 1500

        if player.rect.x >= self.rect.x - tile_size*4 and player.rect.x <= self.rect.x + tile_size * 5 and \
                player.rect.y >= self.rect.y - tile_size * 5 and player.rect.y <= self.rect.y + tile_size * 4:
            if pygame.time.get_ticks() - self.update_time > cooldown:
                self.update_time = pygame.time.get_ticks()
                pollin = Pollin(*self.rect.center)
                pollin_group.add(pollin)

        if player.rect.x >= self.rect.x - tile_size * 7 and player.rect.x <= self.rect.x + tile_size * 8 and \
                (player.rect.x <= self.rect.x - tile_size*4 or player.rect.x >= self.rect.x + tile_size * 5) and \
                player.rect.y >= self.rect.y - tile_size * 8 and player.rect.y <= self.rect.y + tile_size * 7 and \
                (player.rect.y <= self.rect.y - tile_size * 5 or player.rect.y >= self.rect.y + tile_size * 4):
            print('follow')

        for bullet in bullet_group:
            if self.rect.colliderect(bullet.rect):
                self.health -= 1
                bullet.kill()

        if self.health <= 0:
            self.kill()

class Pollin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Pollin.png').convert_alpha()
        self.image = pygame.transform.scale(img, (10, 10))
        self.pos = (x, y)
        mx, my = player.rect.x + tile_size // 2, player.rect.y + tile_size // 2
        self.dir = (mx - x, my - y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0]/int(length), self.dir[1]/int(length))

        self.speed = 12
        self.rect = self.image.get_rect()

    def update(self):
        self.pos = (self.pos[0]+self.dir[0]*self.speed + x_scroll,
                    self.pos[1]+self.dir[1]*self.speed + y_scroll)
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        self.rect.center = self.pos
        screen.blit(self.image, self.rect)

class Portal():
    def __init__(self,x,y):
        img = pygame.image.load('Tileset/22.png').convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = tile_size
        self.height = tile_size

    def draw(self):
        self.rect.x += x_scroll
        self.rect.y += y_scroll
        screen.blit(self.image, self.rect)


world_data = []
for row in range(rows):
    r = [-1] * cols
    world_data.append(r)

with open(f'levels/level{level}_data_topdown.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)


bullets = []

bullet_group = pygame.sprite.Group()
pollin_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()
bush_group = pygame.sprite.Group()
rock_group = pygame.sprite.Group()
flower_group = pygame.sprite.Group()

world = World()
player = world.process_data(world_data)[0]
portal = world.process_data(world_data)[1]

run = True
while run:
    screen.fill(bg_color)

    if player.health <= 0:
        game_over = True

    if game_over == False:
        world.draw()
        #world.hitbox()
        ground_group.update()
        ground_group.draw(screen)
        bush_group.update()
        bush_group.draw(screen)
        rock_group.update()
        rock_group.draw(screen)
        player.update_animation()
        player.draw()
        portal.draw()
        bullet_group.update()
        flower_group.update()
        flower_group.draw(screen)
        pollin_group.update()

        healthbar()

        x_scroll, y_scroll, level_complete = player.move()

        if level_complete:
            level += 1
            bg_scroll = 0
            world_data = reset_level()
            if level <= MAX_LEVELS:
                with open(f'levels/level{level}_data_topdown.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, portal = world.process_data(world_data)

        if move_left == True:
            player.update_action(1)  # left
        elif move_right == True:
            player.update_action(2)  # right
        elif move_up == True:
            player.update_action(2) # up
        elif move_down == True:
            player.update_action(2) # down
        else:
            player.update_action(0)  # idle

    else:
        run = False


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            bullet = Bullet(*player.rect.center)
            bullet_group.add(bullet)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                move_up = True
            if event.key == pygame.K_s:
                move_down = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_a:
                move_left = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                move_up = False
            if event.key == pygame.K_s:
                move_down = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_a:
                move_left = False


    pygame.display.update()
    clock.tick(30)
pygame.quit()