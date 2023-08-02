import boto3
import requests
import os
from datetime import date
import frappe


@frappe.whitelist(allow_guest=True)
def upload_image_to_s3(
    image_url, bucket_name="rha-checkin", country="india", state="delhi"
):
    """
    Make sure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables
    are set in your machine before running the script.

    This function sets up the connection with S3, downloads the image from web,
    uploads the file object to the specified path and returns the file object
    URI.

    :param image_url: public URL of the image to be uploaded on S3.
    :param bucket_name: S3 bucket where image has to be uploaded.
    :param country: country where the checkin was performed.
    :param state: state where the checkin was performed.
    :return: public URI of the uploaded file object.
    """
    s3 = boto3.client("s3")
    r = requests.get(image_url, stream=True)

    today = date.today()
    today_date = today.day
    today_month = today.month
    today_year = today.year

    file_name = image_url.split("/")[-1]
    s3_path = "dev/{0}/{1}/{2}/{3}/{4}/{5}".format(
        today_year, today_month, today_date, country, state, file_name
    )
    s3.upload_fileobj(r.raw, bucket_name, s3_path)

    bucket_location = s3.get_bucket_location(Bucket=bucket_name)
    return "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location["LocationConstraint"], bucket_name, s3_path
    )


# Test image upload
# s3_path = "dev/india/delhi/najafgarh/2023/07/20/TestImage"
# image_url = "https://checkin-dev.robinhoodarmy.com/files/6f43e44288c54df.jpeg"

# print("upload file url is " + upload_image_to_s3(image_url))
