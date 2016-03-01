#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <iostream>
#include <cmath>
using namespace std;
using namespace cv;

/*
My definition of normalization function for each point
level indicates the level of normalization, 
level=1: L1 normalization,
level=2: L2 normalization,
level=0: infinite normalization,
*/
void normAtPoint(int level, Mat& src1, Mat& src2, Mat& dst)
{
	int num_col = src1.cols;
	int num_row = src1.rows;

	dst = Mat::zeros(num_row, num_col, CV_8UC1);
	if (level == 0)
	{
		for (int i = 0; i < num_row; i++)
		{
			for (int j = 0; j < num_col; j++)
			{
				dst.at<char>(i, j) = max(abs(src1.at<char>(i, j)), abs(src2.at<char>(i, j))); 
			}
		}
	}
	else if (level == 1)
	{
		for (int i = 0; i < num_row; i++)
		{
			for (int j = 0; j < num_col; j++)
			{
				dst.at<char>(i, j) = (abs(src1.at<char>(i, j)) + abs(src2.at<char>(i, j))); 
			}
		}
	}
	else if (level == 2)
	{
		for (int i = 0; i < num_row; i++)
		{
			for (int j = 0; j < num_col; j++)
			{
				dst.at<char>(i, j) = sqrt(pow(src1.at<char>(i, j), 2) + pow(src2.at<char>(i, j), 2)); 
			}
		}
	}
}

int main()
{
	Mat src = imread("cameraman.tif", IMREAD_GRAYSCALE);
	Mat dstRobertsX;
	Mat dstRobertsY;
	Mat dstRoberts;

	Mat dstPrewittX;
	Mat dstPrewittY;
	Mat dstPrewitt;

	Mat dstSobelX;
	Mat dstSobelY;
	Mat dstSobel;

	// input the values of template kernel
	Mat robertsX = (Mat_ <int>(2, 2) << 1, 0, 0, -1);
	Mat robertsY = (Mat_ <int>(2, 2) << 0, 1, -1, 0);
	Mat prewittX = (Mat_ <int>(3, 3) << -1,0,1,-1,0,1,-1,0,1);
	Mat prewittY = (Mat_ <int>(3, 3) << 1,1,1,0,0,0,-1,-1,-1);
	Mat sobelX = (Mat_ <int>(3,3) << -1,0,1,-2,0,2,-1,0,1);
	Mat sobelY = (Mat_ <int>(3,3) << 1,2,1,0,0,0,-1,-2,-1);

	//do 2D convolution using  internal function of OpenCV
	filter2D(src, dstRobertsX, -1, robertsX);
	filter2D(src, dstRobertsY, -1, robertsY);

	filter2D(src, dstPrewittX, -1, prewittX);
	filter2D(src, dstPrewittY, -1, prewittY);

	filter2D(src, dstSobelX, -1, sobelX);
	filter2D(src, dstSobelY, -1, sobelY);

	//merge the x and y data, we use  L1, L2 and L infinite normalzation
	normAtPoint(0, dstRobertsX, dstRobertsY, dstRoberts);
	normAtPoint(0, dstPrewittX, dstPrewittY, dstPrewitt);
	normAtPoint(0, dstSobelX, dstSobelY, dstSobel);
	
	string nameSrc = "Src image";
	string nameRobertsX = "X of Roberts";
	string nameRobertsY = "Y of Roberts";
	string nameRoberts = "Merge of Roberts";

	String namePrewittX = "X of Prewitt";
	String namePrewittY = "Y of Prewitt";
	String namePrewitt = "Merge of Prewitt";

	String nameSobelX = "X of Sobel";
	String nameSobelY = "Y of Sobel";
	String nameSobel = "Merge of Sobel";

	//create window for showing image 
	namedWindow(nameSrc, CV_WINDOW_AUTOSIZE);
	namedWindow(nameRobertsX, CV_WINDOW_AUTOSIZE);
	namedWindow(nameRobertsY, CV_WINDOW_AUTOSIZE);
	namedWindow(nameRoberts, CV_WINDOW_AUTOSIZE);
	namedWindow(namePrewittX, CV_WINDOW_AUTOSIZE);
	namedWindow(namePrewittY, CV_WINDOW_AUTOSIZE);
	namedWindow(namePrewitt, CV_WINDOW_AUTOSIZE);
	namedWindow(nameSobelX, CV_WINDOW_AUTOSIZE);
	namedWindow(nameSobelY, CV_WINDOW_AUTOSIZE);
	namedWindow(nameSobel, CV_WINDOW_AUTOSIZE);
	
	imshow(nameSrc, src);
	imshow(nameRobertsX, dstRobertsX);
	imshow(nameRobertsY, dstRobertsY);
	imshow(nameRoberts, dstRoberts);
	imshow(namePrewittX, dstPrewittX);
	imshow(namePrewittY, dstPrewittY);
	imshow(namePrewitt, dstPrewitt);
	imshow(nameSobelX, dstSobelX);
	imshow(nameSobelY, dstSobelY);
	imshow(nameSobel, dstSobel);

	waitKey(0);
	return 0;
}
