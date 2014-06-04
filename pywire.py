'''
Documentation, License etc.

@package pywire
'''
import libtcodpy as libtcod
import sys

class CellState:
  def __str__(self):
    return self.name
  
  def __init__(self, name, colour):
    self.name = name
    self.colour = colour
    self.process = True
    
  def transition(self, neighbours):
    return self
  
  def setTransition(self, transition):
    self.transition = transition

class Cell:
  def __init__(self,x,y, state):
    self.x = x
    self.y = y
    self.state = state
  
  def setState(self, state):
    self.state = state

class Pyca:
  def __init__(self, width, height, states):
    self.width = width
    self.height = height
    self.console = libtcod.console_new(width, height)
    self.states = states
    self._defaultState = states[0]
    self.cells     = [[Cell(x, y, self._defaultState) for y in range(height)] for x in range(width)]
    
    self.frame = 0
    
    self._showFrame = True
    self._countDiagonals = True
    
    print "CA: Done."
  
  def countDiagonals(self, include):
    self._countDiagonals = include
  
  def defaultState(self, state):
    self._defaultState = state
  def resetCell(self, x, y):
    self.cells[x][y].state = self._defaultState
  
  def cycleState(self, x, y):
    curState = self.cells[x][y].state
    stateIndex = self.states.index(curState)
    try:
      newState = self.states[stateIndex + 1]
    except:
      newState = self.states[0]
    
    self.cells[x][y].state = newState
    return True
    
  def update(self):
    self.updateConsole()
  
  def updateConsole(self):
    for x in range(self.width):
      for y in range(self.height):
        c = self.cells[x][y]
        col = c.state.colour
        libtcod.console_set_char_background(self.console, x, y, col)
    if self._showFrame:
      libtcod.console_print(self.console, 0, self.height - 1, "Frame: " + str(self.frame))
  
  def getConsole(self):
    return self.console
  
  def doTransition(self) :
    nextCells = [[Cell(x, y, self._defaultState) for y in range(self.height)] for x in range(self.width)]
    for x in range(self.width):
      for y in range(self.height):
        if self.cells[x][y].state.process:
          neighbours = self.getNeighbours(x, y)
          nextCells[x][y].state = self.cells[x][y].state.transition(neighbours)
    
    self.cells = nextCells
    self.frame += 1
  
  def getNeighbours(self, x, y):
    neighbours = []
    
    ' Top '
    if y - 1 >= 0:
      neighbours.append(Cell(x, y - 1, self.cells[x][y - 1].state))
    ' Right '
    if x + 1 < self.width:
      neighbours.append(Cell(x + 1, y, self.cells[x + 1][y].state))
    ' Bottom '
    if y + 1 < self.height:
      neighbours.append(Cell(x, y + 1, self.cells[x][y + 1].state))
    ' Left '
    if x - 1 >= 0:
      neighbours.append(Cell(x - 1, y, self.cells[x - 1][y].state))
    
    if self._countDiagonals:
      ' Top-Right '
      if x + 1 < self.width and y - 1 >= 0:
        neighbours.append(Cell(x + 1, y - 1, self.cells[x + 1][y - 1].state))
      ' Bottom-Right '
      if x + 1 < self.width and y + 1 < self.height:
        neighbours.append(Cell(x + 1, y + 1, self.cells[x + 1][y + 1].state))
      ' Bottom-Left '
      if x - 1 >= 0 and y + 1 < self.height:
        neighbours.append(Cell(x - 1, y + 1, self.cells[x - 1][y + 1].state))
      ' Top-Left '
      if x - 1 >= 0 and y - 1 >= 0:
        neighbours.append(Cell(x - 1, y - 1, self.cells[x - 1][y - 1].state))
    
    return neighbours

###### CA
############

def renderWires(ww):
  con = ww.getConsole()
  conW = libtcod.console_get_width(con)
  conH = libtcod.console_get_height(con)
  root = 0
  libtcod.console_blit(con, 0,0, conW, conH, root, 0, 0)
  

def update(ww):
  global mouse, running
  ww.update()
  
def renderOverlay():
  global mouse
  mouseX = mouse.cx
  mouseY = mouse.cy
  if running:
    libtcod.console_print(0, 0, 0, "Running")
  
  libtcod.console_print(0, 0, 1, "Mouse at [" + str(mouseX) + "," + str(mouseY) + "]")
  libtcod.console_set_char_background(0, mouseX, mouseY, libtcod.lightest_lime, libtcod.BKGND_ADDALPHA(0.2))

def processInput(ww):
  global states, mouse, key, running, drawingLine, drawingRect, x1, y1, x2, y2
  
  if key and key != libtcod.KEY_NONE:
    if key.vk == libtcod.KEY_ESCAPE:
      sys.exit()
    elif key.vk == libtcod.KEY_SPACE:
      running = not running
  
  mx = mouse.cx
  my = mouse.cy
  
  if mouse.lbutton_pressed:
    if key.shift:
      drawingLine = not drawingLine
      if drawingLine:
        x1 = mx
        y1 = my
      else:
        key.shift = False
        x2 = mx
        y2 = my
        libtcod.line(x1,y1,x2,y2,ww.cycleState)
    
    elif key.lctrl or key.rctrl:
      drawingRect = not drawingRect
      if drawingRect:
        x1 = mx
        y1 = my
      else:
        key.lctrl = key.rctrl = False
        x2 = mx
        y2 = my
        libtcod.line(x1, y1, x2, y1, ww.cycleState)
        libtcod.line(x2, y1, x2, y2, ww.cycleState)
        libtcod.line(x2, y2, x1, y2, ww.cycleState)
        libtcod.line(x1, y2, x1, y1, ww.cycleState)
        
    
    else:
      ww.cycleState(mx, my)
    
  if mouse.rbutton_pressed:
    ww.resetCell(mx, my)
    
  
' INIT '
CONSOLE_WIDTH = 80
CONSOLE_HEIGHT = 50

libtcod.console_set_custom_font(b'consolas10x10_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_set_default_foreground(0, libtcod.white)
libtcod.console_init_root(CONSOLE_WIDTH, CONSOLE_HEIGHT, b'PYWIRE', False, libtcod.RENDERER_GLSL)

libtcod.sys_set_fps(16)

running = False

' State definitions '
offState = CellState('Off', libtcod.black)
wireState = CellState('Wire', libtcod.gold)
headState = CellState('Electron Head', libtcod.white)
tailState = CellState('Electron Tail', libtcod.desaturated_blue)

def wireTransition(neighbours):
  headNeighbours = 0
  for n in neighbours:
    if n.state == headState:
      headNeighbours += 1
  if headNeighbours == 1 or headNeighbours == 2:
    return headState
  else:
    return wireState
  
def headTransition(neighbours):
  return tailState
def tailTransition(neighbours):
  return wireState

offState.process = False
wireState.setTransition(wireTransition)
headState.setTransition(headTransition)
tailState.setTransition(tailTransition)

states = [
  offState,
  wireState,
  headState,
  tailState
]

' Main '

wireWorld = Pyca(CONSOLE_WIDTH, CONSOLE_HEIGHT, states)

wireWorld.countDiagonals(True)    # Include diagonal neighbours
wireWorld.defaultState(offState)  # The state that resetCell() will set a cell to

mouse = libtcod.Mouse()
key = libtcod.Key()
drawingLine = False
drawingRect = False

x1 = y1 = x2 = y2 = None

while not libtcod.console_is_window_closed() :
  if running:
    wireWorld.doTransition()
  
  libtcod.sys_check_for_event(
    libtcod.EVENT_MOUSE |
    libtcod.EVENT_MOUSE_MOVE |
    libtcod.EVENT_KEY_PRESS,
    key,
    mouse
  )
  
  libtcod.console_clear(0)
  processInput(wireWorld)
  update(wireWorld)
  renderWires(wireWorld)
  renderOverlay()
  libtcod.console_flush()
  
