import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox
import random
import sys
import time
from collections import deque


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BOX_WIDTH = 30
HEADER_HEIGHT = int(SCREEN_HEIGHT/5)

SCREEN_WIDTH = max(SCREEN_WIDTH, 300)
SCREEN_WIDTH -= SCREEN_WIDTH % BOX_WIDTH
SCREEN_HEIGHT -= SCREEN_HEIGHT % BOX_WIDTH
HEADER_HEIGHT -= HEADER_HEIGHT % BOX_WIDTH

FONT_SIZE = int(HEADER_HEIGHT/3.25)

COLS = SCREEN_WIDTH / BOX_WIDTH
ROWS = (SCREEN_HEIGHT-HEADER_HEIGHT) / BOX_WIDTH



class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y


    def display(self, surface, color):
        x_coor = self.x*BOX_WIDTH + 1
        y_coor = HEADER_HEIGHT + self.y*BOX_WIDTH + 1
        width = BOX_WIDTH - 2
        rect = (x_coor, y_coor, width, width)
        pygame.draw.rect(surface, color, rect)



class Snake:
    def __init__(self, head_pos=(2, 2), length=0):
        self.head = Block(*head_pos)
        self.body = deque([self.head])
        self.dx = 0
        self.dy = 0
        for i in range(length):
            self.grow()


    def move(self, food):
        if food.x > self.head.x and self.dx != -1:
            self.dx = 1
            self.dy = 0
        elif food.x < self.head.x and self.dx != 1:
            self.dx = -1
            self.dy = 0
        elif food.y > self.head.y and self.dy != -1:
            self.dx = 0
            self.dy = 1
        elif food.y < self.head.y and self.dy != 1:
            self.dx = 0
            self.dy = -1

        if not 0 <= self.head.x + self.dx < COLS:
            self.dx = 0
            if self.head.y == 0:
                self.dy = 1
            else:
                self.dy = -1
        elif not 0 <= self.head.y + self.dy < ROWS:
            self.dy = 0
            if self.head.x == 0:
                self.dx = 1
            else:
                self.dx = -1

        tail = self.body[-1]
        tail.x = self.head.x + self.dx
        tail.y = self.head.y + self.dy
        self.head = self.body.pop()
        self.body.appendleft(self.head)


    def grow(self):
        # move() method will take care of its position
        self.body.append(Block(-1, -1))


    def display(self, surface):
        for block in self.body:
            block.display(surface, (200, 200, 200))
        self.head.display(surface, (0, 0, 0))



class Food(Block):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.dx = 0
        self.dy = 0


    def move(self, snake):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_LEFT:
                    self.dx = -2
                    self.dy = 0
                elif event.key == pygame.K_RIGHT:
                    self.dx = 2
                    self.dy = 0
                elif event.key == pygame.K_UP:
                    self.dx = 0
                    self.dy = -2
                elif event.key == pygame.K_DOWN:
                    self.dx = 0
                    self.dy = 2
            elif event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT and 
                        self.dx == -2 and self.dy == 0) or \
                    (event.key == pygame.K_RIGHT and 
                        self.dx == 2 and self.dy == 0) or \
                    (event.key == pygame.K_UP and 
                        self.dx == 0 and self.dy == -2) or \
                    (event.key == pygame.K_DOWN and 
                        self.dx == 0 and self.dy == 2):
                    self.dx = 0
                    self.dy = 0

        if self.x + self.dx < 0:
            self.x = 0
        elif self.x + self.dx >= COLS:
            self.x = COLS-1
        elif self.y + self.dy < 0:
            self.y = 0
        elif self.y + self.dy >= ROWS:
            self.y = ROWS-1
        else:
            min_dist_x = abs(self.dx)
            min_dist_y = abs(self.dy)
            dist_x = abs(self.dx)
            dist_y = abs(self.dy)
            for block in snake.body:
                if self.x == block.x:
                    # when dy is positive
                    if self.y < block.y <= self.y + self.dy:
                        dist_y = block.y - 1 - self.y
                    # when dy is negative
                    elif self.y + self.dy <= block.y < self.y:
                        dist_y = self.y - block.y - 1
                elif self.y == block.y:
                    # when dx is positive
                    if self.x < block.x <= self.x + self.dx:
                        dist_x = block.x - 1 - self.x
                    # when dx is negative
                    elif self.x + self.dx <= block.x < self.x:
                        dist_x = self.x - block.x - 1
                
                min_dist_x = min(min_dist_x, dist_x)
                min_dist_y = min(min_dist_y, dist_y)

            if self.dx != 0:
                min_dist_x *= self.dx / abs(self.dx)
            if self.dy != 0:
                min_dist_y *= self.dy / abs(self.dy)
            
            self.x += min_dist_x
            self.y += min_dist_y



def redraw_window(surface, snake, food, time_left):
    surface.fill((100, 100, 225))
    
    # Draws the borders of each boxes in the surface
    for x in range(0, SCREEN_WIDTH, BOX_WIDTH):
        for y in range(0, SCREEN_HEIGHT, BOX_WIDTH):
            rect = (x, y, BOX_WIDTH, BOX_WIDTH)
            pygame.draw.rect(surface, (0, 0, 0), rect, width=1)

    food.display(surface, (0, 200, 0))
    snake.display(surface)

    # Background color for the header
    surface.fill((200, 200, 200), (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))

    font = pygame.font.Font('freesansbold.ttf', FONT_SIZE)

    time_text = font.render(f"TIME LEFT: {time_left} sec", True, (0, 0, 0))
    time_pos = (25, (HEADER_HEIGHT - FONT_SIZE)/2)
    surface.blit(time_text, time_pos)

    pygame.display.update()



def play_game():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    icon = pygame.image.load("apple.png")
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Kill the Snake")
    
    clock = pygame.time.Clock()

    snake = Snake(length=2)
    food = Food(COLS-3, ROWS-3)
    
    start_time = time.time()
    total_time = 45
    time_taken = 0
    time_left = total_time

    game_result = None
    count = 0
    
    while game_result is None:
        snake.move(food)
        food.move(snake)

        if time_taken // 3 > count:
            count += 1
            snake.grow()

        time_taken = int(time.time() - start_time)
        time_left = total_time - time_taken

        for i in range(1, len(snake.body)):
            block = snake.body[i]
            if block.x == snake.head.x and block.y == snake.head.y:
                game_result = "won"
        if game_result:
            break
        elif snake.head.x == food.x and snake.head.y == food.y:
            game_result = "lose"
        elif time_left <= 0:
            game_result = "time up"

        redraw_window(screen, snake, food, time_left)
        clock.tick(8)

    ask_for_retry(game_result)



def ask_for_retry(game_result):
    root = tk.Tk()

    # destroying the unwanted main window
    root.overrideredirect(1)
    root.withdraw()
    
    if game_result == "won":
        title = "You Won!"
        msg = "Awesome! You killed the snake."
    elif game_result == "lose":
        title = "You Lose!"
        msg = "Sorry! You were eaten by the snake."
    elif game_result == "time up":
        title = "Time up!"
        msg = "Sorry! Your time is up."

    msg += "\nDo you want to play again ?"

    want_retry = messagebox.askyesno(title, msg)
    root.destroy()

    root.mainloop()

    if want_retry:
        play_game()

    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    play_game()



