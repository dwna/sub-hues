# sub-hues
The most common hues of a subreddit.


Main Image: https://i.imgur.com/pPOwKcC.jpg



This is a graph of the most common hues on r/all. The data was gathered in praw and graphed using pillow in python.

I downloaded the high quality thumbnails of the first 1000 posts on r/all, the most that praw allows. I then resized the images to make the amount of colors managable and so it does not appear as a solid circle. This makes the more common hues visible, as using the colors from a full sized image did not turn out too well, believe me. I put each color's rgb value into a list and counted the amount of times it occured.

Each point is a different color. I converted each rgb value to hsv. It's position is determined by it's hue and saturation, with the hue angle as the angle on the circle. It's saturation is used to calculate how far it is from the center. The colors with the lowest value (how much black is in the color) are graphed first so that they appear on the bottom. They still exist, but it allows the hues to be more visible with the lighter colors. Each point is slightly transparent so you can see some colors behind it and it blends better.
Some of colors are hidden by the black background of the large circle, so [here is different version with a white background.](https://i.imgur.com/LYva5VY.jpg)

For this visualization, I made every single point the same size, but because I recorded the amount of times each color occured, I have the option to scale the point relative to the maximum number times a color appears. However, even with this option enabled, it is hard to see discernable differences in the sizing as one color (often pure white or black) outweighs the others and causes them to be smaller even though they are all variable.

