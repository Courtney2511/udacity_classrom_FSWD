import turtle

window = turtle.Screen()
window.bgcolor("black")

brad = turtle.Turtle()
brad.shape("classic")
brad.speed(8)
brad.color("pink")

def draw_square(some_turtle) :

    count = 0
    while count < 4:
        some_turtle.forward(100)
        some_turtle.right(90)
        count = count + 1

def draw_circle() :
    angie = turtle.Turtle()
    angie.shape("arrow")
    angie.color("blue")
    angie.circle(100)

def draw_triangle() :
    courtney = turtle.Turtle()
    courtney.color("white")

    count = 0
    while count < 3 :
        courtney.forward(100)
        courtney.left(120)
        count = count + 1

def draw_art():
    for i in range (1, 37) :
        draw_square(brad)
        brad.right(10)
    brad.right(90)
    brad.forward(200)

draw_art()

window.exitonclick()
