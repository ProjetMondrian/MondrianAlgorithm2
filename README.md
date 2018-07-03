# MondrianAlgorithm2

- Oscar Thomsen

The stategy used for this algorithm is to split the image into a given number of smaller regions then for each region look at each pixel and calculate either the mean or the median (more about that further below), the calculated value is then applied to each pixel in that region.

Once that is done for all the regions then the ones that are the same color are merged to create larger homogeneous regions.

This is not quite the split and merge algorithm that was disussed because for now the splitting is not a recursion based on a homogeneity criterion, instead we simply choose the number of regions the image is split into. It is not meant to stay this  way, the purpose was just to work on the merging part first without spending too much time figuring out the splitting in order to get more representative results and get a better idea of how the algorithm should be adapted to achieve our goals.

The merging does not yet work as intended, so for now all there is to show is the result of the splitting.

Now back to the mean or median problem, the advantage of the mean is that it can be calculated in linear time whereas here the median is is calculated in n² because the color of a pixel is a triplet so there is no obvious way to turn them into a sorted list. However using the mean creates colors that didn't exist in the original image which goes against Mondrian's technique of using very few different colors. Also using the mean does not look good at all for images with few different colors to start with.

Tasks left to do: 
- Fix merge algorithm
- Possibly change split algorithm once the above is done
- Optimise the way the median is calculated
- Make the program work for all image sizes


## Some examples : 

Original Image : 
![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/lena.jpg)

Result : 
![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/lena_temp_output.png)


Original Image :
![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/white_background_input.jpg)

Result :
![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/white_background_temp_output.png)
