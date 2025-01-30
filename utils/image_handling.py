from PIL import Image
from PIL.Image import Image as Img
from typing import Union, Tuple, List, Optional
from io import BytesIO
from math import lcm
from logging import warning


def load_image(img_buf: BytesIO) -> Img:
    """Loads a PIL.Image object from Image bytes."""
    img = Image.open(img_buf)
    return img


def load_image_from_path(img_path: str) -> Img:
    """Loads a PIL.Image object from Image path."""
    img = Image.open(img_path)
    return img


def load_image_from_url(img_url: str) -> Img:
    """Loads a PIL.Image object from Image URL."""
    import requests

    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    return img


def extract_frames(img: Img) -> List[Img]:
    """Extracts frames from an Image."""
    frame_count = getattr(img, "n_frames", 1)
    frames: List[Img] = list()
    for i in range(frame_count):
        img.seek(i)
        frames.append(img.copy().convert("RGBA"))
    return frames


def resize(
    img: Img, size: Optional[Tuple[int, int]] = None, multiplier: Optional[float] = None
) -> Img:
    if size is None and multiplier is None:
        raise ValueError("Either size or multiplier must be specified.")
    if size is not None and multiplier is not None:
        raise ValueError("Both size and multiplier can't be specified.")

    if multiplier is not None:
        size = int(multiplier * img.width), int(multiplier * img.height)

    assert size is not None
    new_img = img.resize(size, resample=Image.Resampling.NEAREST)  # type: ignore
    return new_img


def canvas_resize(
    img: Img, new_size: Tuple[int, int], coords: Tuple[int, int] = (0, 0)
) -> Union[Img, None]:
    """Resizes the canvas of an Image."""
    new_width, new_height = new_size
    x, y = coords
    if x == 0 and y == 0 and new_width == img.width and new_height == img.height:
        return img
    new_img = Image.new("RGBA", size=(new_width, new_height))
    new_img.paste(img, box=(x, y))
    return new_img


def flip(img: Img, vertical: bool = False):
    """Flips the image"""
    return img.transpose(Image.FLIP_TOP_BOTTOM if vertical else Image.FLIP_LEFT_RIGHT)  # type: ignore


def rotate_90_clockwise(img: Img, count: int = 1):
    """Rotates the image 90 degrees clockwise"""
    count = count % 4
    return img.rotate(-90 * count, expand=True)


def extra_frames(
    imgs: List[Img], final_count: int, add_blank: bool = False
) -> List[Img]:
    """Adds frames to get the required frame count."""
    original_frame_count = len(imgs)
    add_count = final_count - original_frame_count

    if original_frame_count == 0:
        raise ValueError("No frames received")

    if add_count < 0:
        raise ValueError("Final count is less than original count")

    new_frames: List[Img] = []
    for i in range(add_count):
        if add_blank:
            new_frames.append(Image.new("RGBA", size=imgs[0].size))
        else:
            new_frames.append(imgs[i % original_frame_count].copy())
    return new_frames


def stack_layers(
    layers: List[List[Img]],
    layer_order: Optional[List[int]] = None,
    layers_coords: Optional[List[Tuple[int, int]]] = None,
) -> List[Img]:
    """
    Merges the layers according to the given order.

    :param layers: list of layers where a layer is a list of frames
    :param layer_order: order of layers
    :param layers_coords: list of coords of the layers, same order as layers
    """

    # Using the original order if layer_order is not provided
    if layer_order is None:
        layer_order = list(range(len(layers)))

    # Placing the layers at (0, 0) if coords are not provided
    if layers_coords is None:
        layers_coords = [(0, 0) for _ in layers]

    # Validating the parameters
    if len(layers) == 0:
        warning("No layers received.")

    if len(layers) != len(layer_order):
        raise ValueError("Layer count doesn't match order count.")

    if len(layers) != len(layers_coords):
        raise ValueError("Layer count doesn't match coords count.")

    if any(i < 0 or i >= len(layers_coords) for i in layer_order):
        raise ValueError("Layer index out of range.")

    if len(layer_order) != len(set(layer_order)):
        raise ValueError("Duplicate detected in layer order.")

    layer_count = len(layers)

    for i in range(layer_count):
        size = layers[i][0].size
        for frame in layers[i]:
            if frame.size != size:
                raise ValueError("A layer has frame size mismatch.")

    max_width = max(layer[0].width for layer in layers)
    max_height = max(layer[0].height for layer in layers)

    # Matching the Frame count
    lcm_frame_count = 1
    for i in range(layer_count):
        lcm_frame_count = lcm(lcm_frame_count, len(layers[i]))
    for i in range(layer_count):
        layers[i] += extra_frames(layers[i], final_count=lcm_frame_count)

    # Stacking the layers
    stacked = [
        Image.new("RGBA", size=(max_width, max_height)) for _ in range(lcm_frame_count)
    ]
    for i in range(layer_count):
        for j in range(lcm_frame_count):
            current_layer = layer_order[i]
            stacked[j].alpha_composite(
                layers[current_layer][j], layers_coords[current_layer]
            )
    return stacked


def animate(imgs: List[Img], duration: int = 200) -> BytesIO:
    """Creates a GIF from a list of frames."""
    if len(imgs) == 0:
        print("ERROR: No images received.")
        raise ValueError("No images received.")

    bytes_array = BytesIO()
    if len(imgs) == 1:
        imgs[0].save(bytes_array, format="PNG")
    else:
        imgs[0].save(
            bytes_array,
            format="GIF",
            append_images=imgs[1:],
            save_all=True,
            duration=duration,
            optimize=False,
            loop=0,
            disposal=2,
        )
    bytes_array.seek(0)
    return bytes_array


def stack_and_animate(
    layers: List[List[Img]],
    *,
    layer_order: Optional[List[int]] = None,
    layers_coords: Optional[List[Tuple[int, int]]] = None
) -> BytesIO:
    frames = stack_layers(layers, layer_order, layers_coords)
    animation = animate(frames)
    return animation


def center_image_coords(
    img_size: Tuple[int, int], base_size: Tuple[int, int]
) -> Tuple[int, int]:
    """Returns the coordinates to center an image."""
    x = (base_size[0] - img_size[0]) // 2
    y = (base_size[1] - img_size[1]) // 2
    return x, y
