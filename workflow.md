### ...
setting up a canvas and learning how to manipulate individual pixels. This is key for fractals because we need to color each pixel based on fractal math.

## What is the Mandelbrot Set?
It's based on a simple formula that you repeat over and over:
<code>
z = z² + c
</code>
Where z and c are complex numbers.

Complex Numbers - Quick Crash Course
A complex number has two parts:
</code>
c = a + bi
</code>

a = real part (think: x-axis)
b = imaginary part (think: y-axis)
i = √-1 (the "imaginary unit")

For our canvas:

Each pixel position (x, y) maps to a complex number
We test if that number "escapes to infinity" or stays bounded
