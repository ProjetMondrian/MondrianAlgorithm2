# MondrianAlgorithm2

- Oscar Thomsen

The stategy used for this algorithm is to split the image into a given number of smaller regions then for each region look at each pixel and calculate either the mean or the median (more about that further below), the calculated value is then applied to each pixel in that region.

Once that is done for all the regions then the ones that are the same color are merged to create larger homogeneous regions.

This is not quite the split and merge algorithm that was disussed because for now the splitting is not a recursion based on a homogeneity criterion, instead we simply choose the number of regions the image is split into. It is not meant to stay this  way, the purpose was just to work on the merging part first without spending too much time figuring out the splitting in order to get more representative results and get a better idea of how the algorithm should be adapted to achieve our goals.

Now back to the mean or median problem, the advantage of the mean is that it can be calculated in linear time whereas here the median is is calculated in n² because the color of a pixel is a triplet so there is no obvious way to turn them into a sorted list. However using the mean creates colors that didn't exist in the original image which goes against Mondrian's technique of using very few different colors. Also using the mean does not look good at all for images with few different colors to start with.

Possible improvements:

-Integrate some contour recognition into the split algorithm to split the image into smaller squares where there is a contour in order to obtai a greater level of detail.

-Some shapes that we obtain are not rectangular, could implement a function that draws the missing lines in order to only have rectangles of the same color.


## Some examples : 

Original Image : 

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/lena.jpg)

Result : 

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/lena_temp_output.png)

With merging but also with non-rectangular shapes (for now):

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/lena_output.png)

(also here the colors are somewhat normalized otherwise merging changes almost nothing since there would be too many similar but slightly different colors that would thus not be merged into one bigger homogeneous region)


Original Image :

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/white_background_input.jpg)

Result :

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/white_background_temp_output.png)

With merging but also with non-rectangular shapes (for now):

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/white_background_merged_output.png)

Using one of David's examples :

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/women.jpg)

Result : 

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/women_output.png)

It is also possible to use only the 5 colors Mondrian is known for (red, yellow, blue, black and white), which for the same image produces the following result:

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/women_output2.png)

This technique can be interesting for some images but for others it does not work well at all so if we do not control the input it is safer to use the previous technique.

Also this is where it could be interesting to have a method that draws lines within a region of the same color in order to create only rectangular shapes.
