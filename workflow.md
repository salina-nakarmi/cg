

## Setting Up the Canvas

The first step is setting up a canvas and learning how to manipulate **individual pixels**.
This is essential for fractals because **each pixel’s color is determined by fractal mathematics**, not by drawing shapes or lines.

---

## What Is the Mandelbrot Set?

The Mandelbrot set is generated using a simple formula that is repeated over and over:

```text
z = z² + c
```

Here, **z** and **c** are *complex numbers*.

---

## Complex Numbers — Quick Crash Course

A complex number has two parts:

```text
c = a + bi
```

Where:

* **a** → real part (think: x-axis)
* **b** → imaginary part (think: y-axis)
* **i** → √−1 (the imaginary unit)

---

## Mapping Complex Numbers to the Canvas

For our canvas:

* Each pixel position **(x, y)** maps to a **complex number**
* We test whether that complex number:

  * **escapes to infinity**, or
  * **stays bounded**

This behavior determines the pixel’s color.

---

## The Mandelbrot Algorithm

For **each pixel** on the canvas:

1. Convert pixel coordinates **(x, y)** into a complex number **c**
2. Start with:

   ```text
   z = 0
   ```
3. Repeatedly apply:

   ```text
   z = z² + c
   ```
4. Check the magnitude **|z|**:

   * If **|z| > 2**, the value *escapes*
     → color the pixel based on how many iterations it took
   * If it does **not escape** after a fixed maximum number of iterations
     → the pixel is part of the Mandelbrot set (usually colored **black**)

