###########################################################################
#                                                                         #
# Copyright (c) 2014 Romain Mueller                                       #
# Distributed under the GNU GPL v2. For full terms see the file LICENSE.  #
#                                                                         #
###########################################################################
import pygame, copy, random

# some constants
up, left, down, right, none = 0, 1, 2, 3, -1
blocksize = 16
fps = 50
keys = [ [ pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT ],
         [ pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d ],
         [ pygame.K_u, pygame.K_h, pygame.K_j, pygame.K_k ] ]

class snake:
  """Represents some small snake.
    
    """
  def __init__(self, pos, keys):
    self.head  = pos
    self.headsize = blocksize
    self.size  = 10
    self.tail  = [ copy.deepcopy(self.head) ]
    self.dire  = none
    self.dire_tmp = right
    self.speed = 5
    self.cnt   = 0
    self.keys  = keys
    self.color = [80+random.uniform(-20, 50), 80+random.uniform(-20, 50), 80+random.uniform(-20, 50)]
    self.dead  = True
    self.dead_time = 50
    self.new = True
    self.feedonce = False

    self.square = pygame.Surface([self.headsize, self.headsize])
    self.square.fill(self.color)

  def draw(self, screen):
    for pos in self.tail:
      screen.blit(self.square, pos)

  def feed(self, n=1):
    self.size += n
    # speed control
    if self.size == 60:
      self.speed = 4
    if self.size == 120:
      self.speed = 3
    if self.size == 180:
      self.speed = 2

  def change_direction(self, dire):
    if ( set([self.dire, dire])!=set([up, down]) and 
         set([self.dire, dire])!=set([left,right]) ):
      self.dire_tmp  = dire

  def move(self, board):
    if self.dead:
      if not self.new:
        self.dead_time = self.dead_time>0 and self.dead_time-1 or 0
    else:
      # speed control
      self.cnt = (self.cnt+1)%self.speed
      if self.cnt == 0:
        # set direction
        self.dire = self.dire_tmp
        # move head
        if self.dire == right:
          self.head[0] += self.headsize
        elif self.dire == left:
          self.head[0] -= self.headsize
        if self.dire == up:
          self.head[1] -= self.headsize
        elif self.dire == down:
          self.head[1] += self.headsize

        # check position
        if board.bad_pos(self.head):
          self.die()

        # grow tail
        if not self.dead:
          self.tail.insert(0, copy.deepcopy(self.head))
          while len(self.tail)>self.size:
            self.tail.pop()
        
        self.new = False

  def die(self):
    self.dead = True
    self.color = [ min(255, int(i*1.5)) for i in self.color ] 
    self.square.fill(self.color)

class tree:
  """Drops fruits.
    
    """
  def __init__(self):
    self.crea_time = 150
    self.life_time = 400

    self.fruits = [] 
    self.color = [75, 75, 75]
    self.square = pygame.Surface([blocksize/3., blocksize/3.])
    self.square.fill(self.color)

  def draw(self, screen):
    i = blocksize/3.
    for pos in [ j['pos'] for j in self.fruits]:
      screen.blit(self.square, [ pos[0]+i, pos[1] ])
      screen.blit(self.square, [ pos[0]+i, pos[1]+2*i ])
      screen.blit(self.square, [ pos[0], pos[1]+i ])
      screen.blit(self.square, [ pos[0]+2*i, pos[1]+i ])

  def move(self, board):
    # fruits are aging
    for i in range(len(self.fruits)):
      self.fruits[i]['life'] -= 1
    self.fruits = [ i for i in self.fruits if i['life']>0 ]
    # but create new ones
    if random.uniform(0, 1)<1./self.crea_time:
      self.fruits.append({'pos': board.random_pos(), 'life': self.life_time })

  def eat(self, pos):
    self.fruits.pop([ i['pos'] for i in self.fruits ].index(pos))
      
      
class game:
  """Let the party begin!
    
    """
  def __init__(self):
    pygame.init()
    pygame.mouse.set_visible(False)
    self.size = self.width, self.height = 1360, 768
    self.screen = pygame.display.set_mode(self.size, 
                                          pygame.FULLSCREEN)
    self.font  = pygame.font.SysFont('Helvetica', 20)
    self.text  = self.font.render('HIGHSCORE: ', True, (75, 75, 75))
    self.text2 = self.font.render('CURRENT: ', True, (75, 75, 75))
    self.clock = pygame.time.Clock()
    self.snakes = []
    self.tree = tree()


  def random_pos(self):
    while True:
      pos = [ blocksize*random.randint(0, self.width/blocksize), 
               blocksize*random.randint(0, self.height/blocksize) ]
      if not self.bad_pos(pos): break
    return pos

  def bad_pos(self, pos):
    #  check borders
    if pos[0]<0 or pos[0]>=self.width : return True
    if pos[1]<0 or pos[1]>=self.height: return True
    # check other snakes
    for s in self.snakes:
      if pos in s.tail: return True
    # nothing bad happened
    return False

  def run(self):
    running = True
    time = 0
    highscore = 0
    hs_color = [ 75, 75, 75 ]

    while running:
      # ultimate time control
      self.clock.tick(fps)

      # keyboard
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
        if event.type == pygame.KEYDOWN:
          # esc
          if event.key == pygame.K_ESCAPE:
            running = False
          # snake control
          for i in range(len(self.snakes)):
            if event.key in self.snakes[i].keys:
              if self.snakes[i].dead and self.snakes[i].new:
                self.snakes[i].dead = False
              self.snakes[i].change_direction(self.snakes[i].keys.index(event.key))
          # snake birth
          if event.key not in [ k for s in self.snakes for k in s.keys ]:
            for k in keys:
              if event.key in k:
                self.snakes.append(snake(self.random_pos(), k))

      # tree vs. snake
      for i in range(len(self.snakes)):
        if self.snakes[i].head in [ j['pos'] for j in self.tree.fruits]:
          self.snakes[i].feed(10)
          self.tree.eat(self.snakes[i].head)

      # moving
      for s in self.snakes:
        s.move(self)
      self.tree.move(self)

      # drawing
      self.screen.fill([183, 223, 160])

      for s in self.snakes:
        s.draw(self.screen)
      self.tree.draw(self.screen)

      # highscore
      for s in self.snakes:
        if len(s.tail)>highscore:
          highscore = len(s.tail)
          hs_color  = s.color

      hs_text = self.font.render(str(highscore), True, hs_color)
      self.screen.blit(self.text,
                       ( self.width-100-self.text.get_width(), 
                         self.text.get_height()))
      self.screen.blit(self.text2,
                       ( self.width-100-self.text.get_width(), 
                         2*self.text.get_height()))
      self.screen.blit(hs_text, 
                       ( self.width-50-hs_text.get_width(), 
                         self.text.get_height()))

      # scores
      i = 2
      for s in self.snakes:
        txt = self.font.render(str(len(s.tail)), True, s.color)
        self.screen.blit(txt, (self.width-50-txt.get_width(), i*txt.get_height()) )
        i += 1

      pygame.display.flip()

      # kick out dead animals
      self.snakes = [ i for i in self.snakes if i.dead_time>0 ]

if __name__ == "__main__":
  app = game() 
  app.run()
