from PIL import Image, ImageDraw


# create_gradient_image
def create_gradient_image(container_size, color1, color2):
    # get the size of the gradient image
    width, height = container_size

    # Create a new image with a white background
    gradient_image = Image.new('RGB', (width, height), color=(255, 255, 255))

    # Create a draw object for the image
    draw = ImageDraw.Draw(gradient_image)

    # Draw the vertical gradient on the image
    for y in range(height):
        # Calculate the color for this row
        r = int(color1[0] + (y / (height - 1)) * (color2[0] - color1[0]))
        g = int(color1[1] + (y / (height - 1)) * (color2[1] - color1[1]))
        b = int(color1[2] + (y / (height - 1)) * (color2[2] - color1[2]))
        color = (r, g, b)
        # Draw a line for this row with the calculated color
        draw.line((0, y, width, y), fill=color)

    # Save the gradient image
    # gradient_image.save('gradient_image.png')

    return gradient_image


# put_border_radius
def put_border_radius(image, border_radius, border_width=5, border_color=(255, 255, 255)):
    # create a new image
    img_container_size = (image.width, image.height)
    img_container = Image.new('RGBA', img_container_size, (0, 0, 0, 0))
    mask = Image.new("L", img_container_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0)+img_container_size,
                           radius=border_radius, fill=255, outline=255, width=border_width)

    # paste the image onto the img_container using the mask
    img_container.paste(image, (0, 0))
    img_container.putalpha(mask)

    # Draw the border
    draw = ImageDraw.Draw(img_container)
    draw.rounded_rectangle((0, 0) + img_container_size,
                           radius=border_radius, outline=border_color, width=border_width)

    return img_container


# get_badge_details
def get_badge_details(drive_count):
    badge_text = ""
    badge_img_path = ""
    if(drive_count >= 100):
        badge_text = "centurion"
        badge_img_path = "centurion"
    elif(drive_count >= 50):
        badge_text = "gladiator"
        badge_img_path = "gladiator"
    elif(drive_count >= 10):
        badge_text = "ninja"
        badge_img_path = "ninja"
    elif(drive_count >= 0):
        badge_text = "cadet"
        badge_img_path = "cadet"

    return badge_text, badge_img_path


# get_count_decorated
def get_count_decorated(drive_count):
    count_decorated = ""
    if(drive_count == 1):
        count_decorated = "1ˢᵗ"
    elif(drive_count == 2):
        count_decorated = "2ⁿᵈ"
    elif(drive_count == 3):
        count_decorated = "3ʳᵈ"
    else:
        count_decorated = f"{drive_count}ᵗʰ"

    return count_decorated
