import pygame
import neat
import os
import random

pygame.font.init()

win_width = 500
win_height = 800

GEN = 0
#Setting the window of the game
WIN = pygame.display.set_mode((win_width, win_height))
#Setting name to the window
pygame.display.set_caption("Flappy_Bird")

#List of images of bird
bird_images =  [pygame.transform.scale2x(pygame.image.load(os.path.join("Pics", "bird1.png"))),
                pygame.transform.scale2x(pygame.image.load(os.path.join("Pics", "bird2.png"))),
                pygame.transform.scale2x(pygame.image.load(os.path.join("Pics", "bird3.png")))]
#Image of pipe
pipe_image = pygame.transform.scale2x(pygame.image.load(os.path.join("Pics", "pipe.png")))
#Image of Base
base_image = pygame.transform.scale2x(pygame.image.load(os.path.join("Pics", "base.png")))
#Background image
background_image = pygame.transform.scale2x(pygame.image.load(os.path.join("Pics", "bg.png")))
#Font to display data
stat_font = pygame.font.SysFont("comicsans", 40)

class Bird:

    images = bird_images
    max_rotation = 25
    rotation_velocity = 20
    animation_time = 5

    #constructor of the class Bird
    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.image_count = 0
        self.image = self.images[0]

    #method for jumping of the bird
    def jump(self):

        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    #method for moving the bird
    def move(self):

        self.tick_count += 1

        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        if displacement >= 16:

            displacement = (displacement/abs(displacement)) * 16

        if displacement <0:

            displacement -= 2

        self.y = self.y + displacement
        
        if displacement < 0 or self.y < self.height:

            if self.tilt < self.max_rotation:

                self.tilt = self.max_rotation

        else:

            if self.tilt > -90:

                self.tilt -= self.rotation_velocity

    #to draw the bird on the window
    def draw(self, win):

        self.image_count += 1

        if self.image_count < self.animation_time:

            self.image = self.images[0]

        elif self.image_count < self.animation_time * 2:

            self.image = self.images[1]

        elif self.image_count < self.animation_time * 3:

            self.image = self.images[2]

        elif self.image_count < self.animation_time * 4:

            self.image = self.images[1]

        elif self.image_count < self.animation_time * 4 + 1:

            self.image = self.images[0]
            self.image_count = 0

        if self.tilt <= -80:

            self.image = self.images[1]

            self.image_count = self.animation_time * 2

        rotated_image = pygame.transform.rotate(self.image, self.tilt)

        new_rectangle = rotated_image.get_rect(center = self.image.get_rect(topleft = (self.x, self.y)).center)

        win.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):

        return pygame.mask.from_surface(self.image)

class Pipe():

    gap = random.randrange(200, 250)
    velocity = 5

    def __init__(self, xc):
        
        self.x = xc
        self.height = 0
        
        self.top = 0
        self.bottom = 0
        self.pipe_top = pygame.transform.flip(pipe_image, False, True)  #flipped pipe image
        self.pipe_bottom = pipe_image
        
        self.passed = False
        self.set_height()

    #method to choose the height of the pipe
    def set_height(self):

        self.height = random.randrange(50, 450)     #to choose random height for the pipes

        self.top = self.height - self.pipe_top.get_height()

        self.bottom = self.height + self.gap

    #method to move the pipe
    def move(self):

        self.x -= self.velocity

    #to draw the pipe on the game window
    def draw(self, win):

        win.blit(self.pipe_top, (self.x, self.top))

        win.blit(self.pipe_bottom, (self.x, self.bottom))

    #collision of bird and pipe
    def collision(self, bird):

        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface((self.pipe_top))
        bottom_mask = pygame.mask.from_surface(self.pipe_bottom)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:

            return True
        
        return False

class Base:

    velocity = 5
    width = base_image.get_width()
    image = base_image

    def __init__(self, yc):

        self.y = yc
        self.x1 = 0
        self.x2 = self.width

    #method for moving the base with the pipes and bird
    def move(self):

        self.x1 -= self.velocity
        self.x2 -= self.velocity

        if self.x1 + self.width < 0:
            
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:

            self.x2 = self.x1 + self.width

    #method to draw the base on the game window
    def draw(self, win):

        win.blit(self.image, (self.x1, self.y))
        win.blit(self.image, (self.x2, self.y))

# method to draw the game window by calling the draw methods from respective classes
def draw_window(win, birds, pipes, base, score, gen):

    win.blit(background_image, (0,0))

    for pipe in pipes:

        pipe.draw(win)

    text = stat_font.render("Score : " + str(score), 1, (0,0,0)) # to display the score

    win.blit(text, (win_width -10 - text.get_width(), 10))

    text = stat_font.render("Gen : " + str(gen-1), 1, (0,0,0)) # to display the current generation number

    win.blit(text, (10 , 10))

    text = stat_font.render("Population : " + str(len(birds)), 1, (0,0,0)) # to display current population in the current generation

    win.blit(text, (10 , 50))

    base.draw(win)

    for bird in birds:
        bird.draw(win)
    
    pygame.display.update()

# the main method
def main(genomes, config):

    global GEN

    GEN += 1

    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(win_width)]
    win = WIN
    clock = pygame.time.Clock()

    score = 0

    running = True

    while running:      # the loop for running the game

        clock.tick(30)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:       #quit the game if quit is clicked
                
                running = False

                pygame.quit()
                quit()
        
        pipe_index = 0

        if len(birds) > 0:

            if len(pipes) > 1 and birds[0].x + pipes[0].pipe_top.get_width():

                pipe_index = 1

        else:

            running = False
            break

        for x, bird in enumerate(birds):

            bird.move()
            ge[x].fitness += 0.1    # increasing the fitness of each bird that is alive 

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:

                bird.jump()

        add_pipe = False

        removed = []

        for pipe in pipes:

            for x, bird in enumerate(birds):

                if pipe.collision(bird):
                    
                    ge[x].fitness -= 1      # decreasing the fitness of the bird collided with the pipe

                    birds.pop(x)        #removing the bird from the population
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.pipe_top.get_width() < 0:

                removed.append(pipe)

            pipe.move()

        if add_pipe:

            score += 1      # increasing the score for each pipe passed
            
            for g in ge:

                g.fitness += 2  # increasing the fitness of the birds passing the pipe to promote passage of more birds

            pipes.append(Pipe(win_width))

        for rem in removed:
            
            pipes.remove(rem)       #removing the pipes passed

        for x, bird in enumerate(birds):

            if bird.y + bird.image.get_height() -10 >= 730 or bird.y < -50:
                
                ge[x].fitness -= 1  # decreasing the fitness of the birds colliding with follr or celling

                birds.pop(x)    # removing the birds collided with floor or the celling
                nets.pop(x)
                ge.pop(x)

        if score > 100: #to quit the game if score of 100 is reached

            break

        base.move()
        draw_window(win, birds, pipes, base, score, GEN)    #calling the draw window method to draw different components

def run(config_path):
    
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()

    population.add_reporter(stats)

    winner = population.run(main, 50)   #calling the main function to decide the winner bird

if __name__ == "__main__":

    local_dir  = os.path.dirname(__file__)

    config_path = os.path.join(local_dir, "config.txt")     #setting the configuration file path

    run(config_path)