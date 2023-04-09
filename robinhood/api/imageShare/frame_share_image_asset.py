from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
import io
import frappe
from image_edit_helper import put_border_radius, create_gradient_image, get_badge_details, get_count_decorated

@frappe.whitelist(allow_guest=True)
def frameShareImageAsset (img_id, drive_count):
    # Set global variables values
    # Define the colors for the gradient
    color1 = (0, 100, 40)
    color2 = (0, 71, 77)
    font_family = "../../public/fonts/Inter-ExtraBold.ttf"
    padding = 80
    margin = 30
    border_radius = 15
    container_size = (400, 700)
    container_width, container_height = container_size
    used_height = 0

    # ~~~~~~~~ Drive details ~~~~~~~~~~~~~~~~~~~~~
    # get the drive image
    image_response = requests.get('https://checkin.robinhoodarmy.com/files/' + img_id + '.jpg')
    user_image = Image.open(io.BytesIO(image_response.content))
    image = user_image
    # get badge_text and badge image path based on drive count
    badge_text, badge_img_path = get_badge_details(drive_count)
    # ~~~~~~~~ End: Drive details ~~~~~~~~~~~~~~~~~~~~~

    # ################## Start: Decorate the image ##################
    # create gradient container image ~~~~~~~~~~~~~~~~~~~~~
    container = create_gradient_image(container_size, color1, color2)

    # ~~~~~~~~~~ logo image ~~~~~~~~~~~~
    # Put the logo image
    rha_logo_img = Image.open("../../public/images/rha-logo.png")
    # resize the logo image
    new_size = tuple(dim - padding*2.2 for dim in container_size)
    # new_size = tuple(dim // 1.6 for dim in container_size)
    rha_logo_img.thumbnail(new_size)

    # paste the logo image in the center of the container
    logo_width, logo_height = rha_logo_img.size
    x = (container_width - logo_width) // 2
    y = int(used_height + margin)
    container.paste(rha_logo_img, (x, y))
    used_height = y + logo_height
    # ~~~~~~~~~~ end: logo image ~~~~~~~~~~~~

    # ~~~~~~~~~~ image ~~~~~~~~~~~~
    # Crop the image
    # Define crop dimensions
    crop_width, crop_height = 310, 325
    image = ImageOps.fit(image, (crop_width, crop_height), Image.ANTIALIAS)
    border_radius = 40
    image = put_border_radius(image, border_radius)

    # paste image in container at the center
    image_width, image_height = image.size
    x = (container_width - image_width) // 2
    y = int(used_height + margin*0.75)
    container.paste(image, (x, y), image)
    used_height = y + image_height
    # ~~~~~~~~~~ end: image ~~~~~~~~~~~~


    # ~~~~~~~~~~ Badge image ~~~~~~~~~~~~
    badge_image = Image.open(f"../../public/badges/{badge_img_path}.png")
    # resize the badge_image
    new_size = tuple(dim // 4 for dim in image.size)
    badge_image.thumbnail(new_size)
    # paste image in container at the center
    image_width, image_height = badge_image.size
    x = (container_width - image_width) // 2
    y = int(used_height - margin*1.4)
    container.paste(badge_image, (x, y), badge_image)
    used_height = y + image_height
    # ~~~~~~~~~~ end: Badge image ~~~~~~~~~~~~

    # ~~~~~~~~~~ Text: badge text ~~~~~~~~~~~~
    # Add text to the container using the ImageDraw module
    draw = ImageDraw.Draw(container)
    text = f"I'M A ROBIN {badge_text.upper()}"
    font = ImageFont.truetype(font_family, 15)
    # get text box size
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = (
        text_box[2] - text_box[0]), (text_box[3] - text_box[1])
    x = (container.width - text_width) / 2
    y = int(used_height + margin*0.5)
    draw.text((x, y), text, font=font, fill=(30, 228, 179), align='center')
    used_height = y + text_height
    # ~~~~~~~~~~ end Text: badge text ~~~~~~~~~~~~

    # ~~~~~~~~~~ Text: drive_count text ~~~~~~~~~~~~
    draw = ImageDraw.Draw(container)
    drive_count_decorated = get_count_decorated(drive_count)
    text = f"I just checked-in to my \n {drive_count_decorated} drive with RHA!"
    font = ImageFont.truetype(font_family, 30)
    # get text box size
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = (
        text_box[2] - text_box[0]), (text_box[3] - text_box[1])
    x = (container.width - text_width) / 2
    y = int(used_height + margin)
    draw.text((x, y), text, font=font, fill=(255, 255, 255), align='center')
    used_height = y + text_height
    # ~~~~~~~~~~ end Text: drive_count text ~~~~~~~~~~~~

    # ~~~~~~ url box ~~~~~~
    rha_url_img = Image.open("../../public/banner/website-url.png")
    # resize the url image
    new_size = tuple(dim - padding-margin for dim in container_size)
    rha_url_img.thumbnail(new_size)

    # paste the url image in the center of the container
    url_width, url_height = rha_url_img.size
    x = (container_width - url_width) // 2
    y = int(used_height + margin*1.5)
    container.paste(rha_url_img, (x, y))
    used_height = y + url_height
    # ~~~~~~ end: url box ~~~~~~


    # save the image
    return container
