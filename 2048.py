#!/usr/bin/python -t

import curses
import sys
from random import randint
from copy import copy, deepcopy
import time

def PrintMatrix(screen, message, m, p):
  if screen is not None:
    screen.addstr(0, 0, message)
    for i in range(len(m)):
      screen.addstr(i+1, 0, ','.join(['%4s' % e for e in m[i][:]]))

    if p is not None:
      screen.addstr(len(m)+2, 0, 'PREVIOUS')
      for j in range(len(p)):
        screen.addstr(len(m)+j+2, 0, ','.join(['%4s' % e for e in p[j][:]]))
  else:
    print message
    for i in range(len(m)):
      print ','.join(['%4s' % e for e in m[i][:]])

def InBounds(x, A):
  return x >= 0 and x < len(A)

def FillSpaces(m):
  count = 0
  for r in range(len(m)):
    for c in range(len(m[0])):
      if m[r][c] == '.':
        count += 1
  # pick a place
  fill = randint(1,count)

  count = 1 
  for r in range(len(m)):
    for c in range(len(m[0])):
      if m[r][c] == '.':
        if count == fill:
          m[r][c] = str(randint(1,2)*2)
          return
        else:
          count += 1

def Lateral(m, start, step):
  moved = False
  added_block = False
  #columns fixed
  for r in range(len(m)):
    current = start
    nxt = current + step
    while InBounds(current, m[r]) and InBounds(nxt, m[r]):
      # 1- if you are an empty cell, bring the 
      #    next non empty cell forward.
      # 2- if you are non-empty, check the next
      #    and merge it if you are similar.
      # 3- Advance current if you merged or did
      #    nothing
      while InBounds(nxt, m[r]) and m[r][nxt] == '.':
        nxt += step
      if InBounds(nxt, m[r]):
        if m[r][current] == '.':
          m[r][current] = m[r][nxt]
          m[r][nxt] = '.'
          moved = True
        elif m[r][nxt] == m[r][current]:
          m[r][current] = str(2*int(m[r][nxt]))
          m[r][nxt] = '.'
          nxt += step
          current += step
          moved = True
        else:
          current += step
          if current == nxt:
            nxt += step
  value = Value(m)
  if moved == True:
    FillSpaces(m)

  return (moved, value)

def Vertical(m, start, step):
  moved = False
  #rows fixed
  for c in range(len(m[0])):
    current = start
    nxt = current + step
    while InBounds(current, m) and InBounds(nxt, m):
      # 1- if you are an empty cell, bring the 
      #    next non empty cell forward.
      # 2- if you are non-empty, check the next
      #    and merge it if you are similar.
      # 3- Advance current if you merged or did
      #    nothing
      while InBounds(nxt, m) and m[nxt][c] == '.':
        nxt += step
      if InBounds(nxt, m):
        if m[current][c] == '.':
          m[current][c] = m[nxt][c]
          m[nxt][c] = '.'
          moved = True
        elif m[nxt][c] == m[current][c]:
          m[current][c] = str(2*int(m[nxt][c]))
          m[nxt][c] = '.'
          nxt += step
          current += step
          moved = True
        else:
          current += step
          if current == nxt:
            nxt += step
  value = Value(m)
  if moved == True:
    FillSpaces(m)
  
  return (moved, value)

def Left(m):
  return Lateral(m, 0, 1)

def Right(m):
  return Lateral(m, len(m[0])-1, -1)

def Up(m):
  return Vertical(m, 0, 1)

def Down(m):
  return Vertical(m, len(m)-1, -1)

def Score(m):
  result = 0  
  for i in range(len(m)):
    for j in range(len(m[i])):
      if m[i][j] != '.' and int(m[i][j]) > result:
        result = int(m[i][j])

  return result

def Value(m):
  cumulative = 0
  spaces = 0
  for i in range(len(m)):
    for j in range(len(m[i])):
      if m[i][j] != '.':
        cumulative += int(m[i][j])
      else:
        spaces += 1

  return cumulative*spaces

def Move(m):
  screen = curses.initscr()
  screen.keypad(1)

  try:
    PrintMatrix(screen, 'INIT', m, None)
    p = [None]
    ch = screen.getch()
    message = ''
    while ch != ord('q'):
      screen.clear()
      if ch == curses.KEY_UP:
        p.append(deepcopy(m))
        Up(m)
        message = 'UP'
      elif ch == curses.KEY_DOWN:
        p.append(deepcopy(m))
        Down(m)
        message = 'DOWN'
      elif ch == curses.KEY_LEFT:
        p.append(deepcopy(m))
        Left(m)
        message = 'LEFT'
      elif ch == curses.KEY_RIGHT:
        p.append(deepcopy(m))
        Right(m)
        message = 'RIGHT'
      elif ch == ord('b') and p[-1] is not None:
        m = p.pop()
        message = 'BACK'
      
      PrintMatrix(screen, message, m, None)
      ch = screen.getch()
    
    curses.endwin()
  except:
    curses.endwin()
    print "Unexpected error:", sys.exc_info()[0]
    print sys.exc_info()[1]
    print sys.exc_info()[2].format_tb()

"""Solver that sticks to a strict ordering of moves"""
def OrderedMovesSolver(m):
  moves = [Left, Down, Right, Up]
  message = ['LEFT', 'DOWN', 'RIGHT', 'UP']

  done = False
  while not done:
    i = 0
    while i < len(moves) and not moves[i](m)[0]:
      i += 1
    if i == len(moves):
      done = True
    else:
      PrintMatrix(None, message[i], m, None)
      time.sleep(.1)

"""Solver that cycles through the moves in order"""
def CycledSolver(m):
  moves = [Right, Up, Left, Down]
  message = ['RIGHT', 'UP', 'LEFT', 'DOWN']

  done = False
  i = 0
  while not done:
    failures = 0
    while not moves[i](m)[0] and failures < len(moves):
      failures += 1
      i = (i + 1) % len(moves)
    if failures == len(moves):
      done = True
    else:
      PrintMatrix(None, message[i], m, None)
      time.sleep(0.1)
      i = (i + 1) % len(moves)

"""Solver that picks the move with the most gain"""
def GreedySolver(m):
  moves = [Left, Down, Right, Up]
  message = ['LEFT', 'DOWN', 'RIGHT', 'UP']

  done = False
  i = 0
  while not done:
    best_score = 0
    best_move = -1
    best_matrix = None
    for i in range(len(moves)):
      n = deepcopy(m)
      (moved, score) = moves[i](n)
      if not moved:
        continue
      if score > best_score:
        best_score = score
        best_move = i
        best_matrix = deepcopy(n)
    if best_move >= 0:
      m = best_matrix
      PrintMatrix(None, message[best_move], m, None)
      time.sleep(0.1)
    else:
      done = True

def main(argv):
  matrix = [[],[],[],[]]
  matrix[0].extend('....')
  matrix[1].extend('....')
  matrix[2].extend('....')
  matrix[3].extend('....')

  FillSpaces(matrix)
  FillSpaces(matrix)

  choices = [Move, OrderedMovesSolver, CycledSolver, GreedySolver]
  print 'Choose mode:'
  print '1- Interactive game: Arrow keys to move, "b" to undo, "q" to quit'  
  print '2- Ordered solver: Prefer moves in this order: L, D, R, U'
  print '3- Cycle solver: Always go in a cycle: L, D, R, U'
  print '4- Greedy solver: Like "2" but it chooses the best current move (best is the sum of numbers after move * number of spaces)'
  choice = raw_input('Enter choice: ')
  while True:
    try:
      choice = int(choice)
      if choice > 0 and choice < 5:
        break
      else:
        raise ValueError
    except ValueError:
      print 'Incorrect choice. Enter a number from 1-4'
    choice = raw_input('Enter choice: ')

  choices[choice-1](matrix)

if __name__ == '__main__':
  main(sys.argv)
