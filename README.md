# MondrianAlgorithm2

- Oscar Thomsen

The general strategy used for this algorithm is to split the image into a given number of smaller regions then for each of those look at every pixel and calculate the mode for that region (value which appears most frequently), the calculated value is then applied to each pixel in that region. Once that is done for all the regions then the ones that are the same color (or close to the same color) are merged to create larger homogeneous regions.

## Some examples : 

Original Image : 

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/firstPicture.jpg)

Result : 

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/firstPicture_output.png)


The program can also use A. Geitgey's facial recognition library (https://github.com/ageitgey/face_recognition) to identify the eyes and mouth which will then be made more visible in the output. If that library is not installed the program will still run without using it but here is an example to illustrate the need for it when using the program on a close-up of a face:

Original Image :

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/axel.jpg)

Without face recognition :

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/axel_output_withoutFR.png)

With face recognition : 

![alt text](https://github.com/ProjetMondrian/MondrianAlgorithm2/blob/master/axel_output_withFR.png)
