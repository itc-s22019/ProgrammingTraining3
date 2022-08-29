import tkinter
import math

NUM_H_BLOCK = 15  
NUM_V_BLOCK = 15  
WIDTH_BLOCK = 60  
HEIGHT_BLOCK = 30  
COLOR_BLOCK = "purple"  

HEIGHT_SPACE = 250  

WIDTH_PADDLE = 300  
HEIGHT_PADDLE = 15  
Y_PADDLE = 30  
COLOR_PADDLE = "white"  

RADIUS_BALL = 20  
COLOR_BALL = "yellow"  
NUM_BALL = 5  

UPDATE_TIME = 20


class Ball:
    def __init__(self, x, y, radius, x_min, y_min, x_max, y_max):

        self.x = x
        self.y = y
        self.r = radius
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        
        self.speed = 10

        self.angle = math.radians(30)
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)

    def getCoords(self):

        return (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)

    def move(self):

        self.x += self.dx
        self.y += self.dy

        if self.x < self.x_min:
            
            self.reflectH()
            self.x = self.x_min

        elif self.x > self.x_max:

            self.reflectH()
            self.x = self.x_max

        if self.y < self.y_min:

            self.reflectV()
            self.y = self.y_min


    def turn(self, angle):

        self.angle = angle
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)

    def reflectH(self):

        self.turn(math.atan2(self.dy, -self.dx))

    def reflectV(self):

        self.turn(math.atan2(-self.dy, self.dx))

    def getCollisionCoords(self, object):

        ball_x1, ball_y1, ball_x2, ball_y2 = self.getCoords()
        object_x1, object_y1, object_x2, object_y2 = object.getCoords()

        x1 = max(ball_x1, object_x1)
        y1 = max(ball_y1, object_y1)
        x2 = min(ball_x2, object_x2)
        y2 = min(ball_y2, object_y2)

        if x1 < x2 and y1 < y2:
            
            return (x1, y1, x2, y2)
        else:

            return None

    def reflect(self, object):
        
        object_x1, object_y1, object_x2, object_y2 = object.getCoords()

        x1, y1, x2, y2 = self.getCollisionCoords(object)

        is_collideV = False
        is_collideH = False

        if self.dx < 0:
            
            if x2 == object_x2:
                
                is_collideH = True
        else:
            
            if x1 == object_x1:
                
                is_collideH = True

        if self.dy < 0:
           
            if y2 == object_y2:
               
                is_collideV = True
        else:
            
            if y1 == object_y1:
                
                is_collideV = True

        if is_collideV and is_collideH:
            
            if x2 - x1 > y2 - y1:
                
                self.reflectV()
            elif x2 - x1 < y2 - y1:
                
                self.reflectH()
            else:
                
                self.reflectH()
                self.reflectV()

        elif is_collideV:
            
            self.reflectV()

        elif is_collideH:
           
            self.reflectH()

    def exists(self):
        
        return True if self.y <= self.y_max else False


class Paddle:
    def __init__(self, x, y, width, height, x_min, y_min, x_max, y_max):
        
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def getCoords(self):

        return (self.x - self.w / 2, self.y - self.h / 2, self.x + self.w / 2, self.y + self.h / 2)

    def move(self, mouse_x, mouse_y):

        self.x = min(max(mouse_x, self.x_min), self.x_max)
        self.y = min(max(mouse_y, self.y_min), self.y_max)


class Block:

    def __init__(self, x, y, width, height):
        
        self.x = x
        self.y = y
        self.w = width
        self.h = height

    def getCoords(self):

        return (self.x - self.w / 2, self.y - self.h / 2, self.x + self.w / 2, self.y + self.h / 2)


class Breakout:

    def __init__(self, master):
        
        self.master = master

        
        self.width = NUM_H_BLOCK * WIDTH_BLOCK
        self.height = NUM_V_BLOCK * HEIGHT_BLOCK + HEIGHT_SPACE

        self.is_playing = False

        self.createWidgets()
        self.createObjects()
        self.drawFigures()
        self.setEvents()

    def start(self, event):

        if len(self.blocks) == 0 or len(self.balls) == 0:
            
            self.canvas.delete("all")

            self.createObjects()
            self.drawFigures()

        if not self.is_playing:
            self.is_playing = True
            self.loop()
        else:
            self.is_playing = False

    def loop(self):
        

        if not self.is_playing:
            
            return

        self.master.after(UPDATE_TIME, self.loop)

        for ball in self.balls:
            ball.move()

        delete_balls = []
        for ball in self.balls:
            if not ball.exists():
                
                delete_balls.append(ball)

        for ball in delete_balls:
            
            self.delete(ball)

        self.collision()
        self.updateFigures()
        self.result()

    def motion(self, event):

        self.paddle.move(event.x, event.y)

    def delete(self, target):

        figure = self.figs.pop(target)
        self.canvas.delete(figure)

        if isinstance(target, Ball):
            self.balls.remove(target)
        elif isinstance(target, Block):
            self.blocks.remove(target)

    def collision(self):
        
        for ball in self.balls:

            collided_block = None  
            max_area = 0 

            for block in self.blocks:

                collision_rect = ball.getCollisionCoords(block)
                if collision_rect is not None:
                    
                    x1, y1, x2, y2 = collision_rect
                    area = (x2 - x1) * (y2 - y1)

                    if area > max_area:
                        
                        max_area = area

                        collided_block = block

            if collided_block is not None:

                ball.reflect(collided_block)

                self.delete(collided_block)

            for another_ball in self.balls:
                if another_ball is ball:
                    
                    continue

                if ball.getCollisionCoords(another_ball) is not None:

                    ball.reflect(another_ball)

            if ball.getCollisionCoords(self.paddle) is not None:

                ball.reflect(self.paddle)

    def result(self):
        
        if len(self.blocks) == 0:
            self.canvas.create_text(
                self.width // 2, self.height // 2,
                text="GAME CLEAR",
                font=("", 30),
                fill="gold"
            )

            self.is_playing = False

        if len(self.balls) == 0:
            self.canvas.create_text(
                self.width // 2, self.height // 2,
                text="GAME OVER",
                font=("", 30),
                fill="bronze"
            )

            self.is_playing = False

    def setEvents(self):
       

        self.canvas.bind("<ButtonPress>", self.start)
        self.canvas.bind("<Motion>", self.motion)

    def createWidgets(self):
        
        self.canvas = tkinter.Canvas(
            self.master,
            width=self.width,
            height=self.height,
            highlightthickness=0,
            bg="gray"
        )
        self.canvas.pack(padx=10, pady=10)

    def createObjects(self):
        
        self.balls = []
        for i in range(NUM_BALL):
            x = self.width / NUM_BALL * i + self.width / NUM_BALL / 2
            ball = Ball(
                x, self.height // 2,
                RADIUS_BALL,
                RADIUS_BALL, RADIUS_BALL,
                self.width - RADIUS_BALL, self.height - RADIUS_BALL
            )
            self.balls.append(ball)

        self.paddle = Paddle(
            self.width // 2, self.height - Y_PADDLE,
            WIDTH_PADDLE, HEIGHT_PADDLE,
            WIDTH_PADDLE // 2, self.height - Y_PADDLE,
            self.width - WIDTH_PADDLE // 2, self.height - Y_PADDLE
        )

        self.blocks = []
        for v in range(NUM_V_BLOCK):
            for h in range(NUM_H_BLOCK):
                block = Block(
                    h * WIDTH_BLOCK + WIDTH_BLOCK // 2,
                    v * HEIGHT_BLOCK + HEIGHT_BLOCK // 2,
                    WIDTH_BLOCK,
                    HEIGHT_BLOCK
                )
                self.blocks.append(block)

    def drawFigures(self):
        
        self.figs = {}

        for ball in self.balls:
            x1, y1, x2, y2 = ball.getCoords()
            figure = self.canvas.create_oval(
                x1, y1, x2, y2,
                fill=COLOR_BALL
            )
            self.figs[ball] = figure

        x1, y1, x2, y2 = self.paddle.getCoords()
        figure = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=COLOR_PADDLE
        )
        self.figs[self.paddle] = figure

        for block in self.blocks:
            x1, y1, x2, y2 = block.getCoords()
            figure = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=COLOR_BLOCK
            )
            self.figs[block] = figure

    def updateFigures(self):
       
        for ball in self.balls:
            x1, y1, x2, y2 = ball.getCoords()
            figure = self.figs[ball]
            self.canvas.coords(figure, x1, y1, x2, y2)

        x1, y1, x2, y2 = self.paddle.getCoords()
        figure = self.figs[self.paddle]
        self.canvas.coords(figure, x1, y1, x2, y2)


app = tkinter.Tk()
Breakout(app)
app.mainloop()
