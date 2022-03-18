import pygame

screen_specs = {
    "WIDTH": 600,
    "HEIGHT": 450,
    "RED": (255, 0, 0),
}


def screen_init():
    screen = pygame.display.set_mode((screen_specs["WIDTH"], screen_specs["HEIGHT"]))
    pygame.display.set_caption("Cozmo view")
    font = pygame.font.Font("freesansbold.ttf", 15)
    return screen, font


def screen_update(obs, infos, screen, font):
    # get last image.
    img_cozmo_feed = obs
    # resize image
    img_cozmo_feed = img_cozmo_feed.resize(
        (screen_specs["WIDTH"], screen_specs["HEIGHT"])
    )
    # convert PIL img to Pygame Surface img (to display in Pygame window)
    mode = img_cozmo_feed.mode
    size = img_cozmo_feed.size
    data = img_cozmo_feed.tobytes()
    pg_img_cozmo_feed = pygame.image.fromstring(data, size, mode)

    # draw frame
    screen.blit(pg_img_cozmo_feed, (0, 0))
    text = font.render(
        "Battery level: {:2.1f} V".format(infos["battery_level"]),
        True,
        screen_specs["RED"],
        None,
    )
    screen.blit(text, (15, 15))
    text = font.render(
        "L wheel speed: {:2.1f} mmps".format(infos["wheels_speed_mmps"][0]),
        True,
        screen_specs["RED"],
        None,
    )
    screen.blit(text, (15, 30))
    text = font.render(
        "R wheel speed: {:2.1f} mmps".format(infos["wheels_speed_mmps"][1]),
        True,
        screen_specs["RED"],
        None,
    )
    screen.blit(text, (15, 45))
    text = font.render(
        "Timestamp: {:2.1f}".format(infos["time_stamp"]),
        True,
        screen_specs["RED"],
        None,
    )
    screen.blit(text, (15, 60))
    text = font.render(
        "(x, y, z): ({:2.1f},{:2.1f},{:2.1f})".format(
            infos["pose_x"], infos["pose_y"], infos["pose_z"]
        ),
        True,
        screen_specs["RED"],
        None,
    )
    screen.blit(text, (15, 75))
    pygame.display.flip()
