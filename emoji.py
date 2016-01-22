# region Imports
from PIL import Image
import numpy as np
import os
import argparse

# endregion

# region Globals
ICON_SIZE = 20
DEFAULT_EMOJI_SPRITE = "emoji_sprite.png"
NEW_EXT = ".out.png"


# endregion

class EmojiConverter:
    def __init__(self, args):
        self.image_path = args.image_path
        self.icon_size = args.sprite_size
        self.emoji_path = args.emoji_sprites_path
        self.show = args.show
        self.dst = args.destination if args.destination is not None else os.path.dirname(self.image_path)

    def crop_icon(self, img, row, col):
        return img.crop((
            col * self.icon_size,
            row * self.icon_size,
            (col + 1) * self.icon_size,
            (row + 1) * self.icon_size))

    @staticmethod
    def img_hist(img):
        arr = np.array(img.getdata(), np.uint8)
        return np.histogramdd(arr[:, :-1], bins=6, range=[[0, 256]] * 3, weights=arr[:, 3])[0]

    @staticmethod
    def hist_distance(hist1, hist2):
        return np.linalg.norm(hist1 - hist2)

    def run(self):

        icons_image = Image.open(self.emoji_path)
        x_size, y_size = icons_image.size
        x_icons = x_size / self.icon_size
        y_icons = y_size / self.icon_size

        icons = [
            self.crop_icon(icons_image, row, col)
            for col in range(x_icons) for row in range(y_icons)]
        icon_hists = map(self.img_hist, icons)

        img_filename = self.image_path
        img = Image.open(img_filename).convert('RGBA')
        x_size, y_size = img.size
        x_size -= (x_size % self.icon_size)
        y_size -= (y_size % self.icon_size)

        new_img = Image.new("RGB", (x_size, y_size), "white")
        for row in range(y_size / self.icon_size):
            for col in range(x_size / self.icon_size):
                region_hist = self.img_hist(self.crop_icon(img, row, col))
                icon = min(
                        enumerate(icons),
                        key=lambda icon: self.hist_distance(icon_hists[icon[0]], region_hist))[1]
                new_img.paste(icon, (col * self.icon_size, row * self.icon_size),
                              mask=icon.split()[3])

        if self.show:
            new_img.show()
        new_img.save(os.path.join(self.dst, os.path.basename(self.image_path)) + NEW_EXT)


def parse_args():
    parser = argparse.ArgumentParser(
            description="A tiny educational project that demonstrates transforming an image to a similar image made of emojis.")

    parser.add_argument("-i", "--image", action="store", help="Path of the image to convert", required=True,
                        dest="image_path")
    parser.add_argument("--show", action="store_true", help="Display the converted image",
                        dest="show")
    parser.add_argument("-e", "--emoji", help="The emoji sprites source", action='store',
                        default=DEFAULT_EMOJI_SPRITE,
                        dest="emoji_sprites_path")
    parser.add_argument("-s", "--sprite-size", dest="sprite_size",
                        help="The size of every emoji in the sprites source (default=%dpx)" % ICON_SIZE,
                        action="store", type=int, default=ICON_SIZE
                        )
    parser.add_argument("-d", "--destination", help="Output image export path", dest="destination")
    return parser.parse_args()


if __name__ == "__main__":
    converter = EmojiConverter(args=parse_args())
    converter.run()
