import numpy as np

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap  # Needed for custom colormap
from matplotlib.pyplot import cm, Normalize  # Needed for heatmap

from typing import Literal

from numpy.typing import NDArray


######################################################################

# class NPArray:
#     """Add context specific metadata to a type.
#
#     NDArrayMeta[np.generic,
#     """
#
#     @typing._tp_cache
#     def __class_getitem__(cls, param):
#         dtype = param[0]
#         print(dtype)
#         ndarray_type = NP_NDArray[dtype]
#         shape_info = Literal[param[1:]]
#         return Annotated[ndarray_type, shape_info]
#
#
# class NPArrayF(NPArray):
#     @typing._tp_cache
#     def __class_getitem__(cls, param):
#         return NPArray[float, param]


######################################################################


def show_with_clean_interface():
    plt.axis("off")
    plt.show()


def save_tight_image(name: str, clear: bool = True):
    plt.axis("off")
    plt.savefig(f"{name}.png", bbox_inches="tight")
    if clear:
        plt.cla()
        plt.clf()


def blend_heatmap(
    heatmap_source: Literal["NDArray[H, W]"],
    image_to_blend: Literal["NDArray[H, W, C]"],
    cmap=cm.plasma,
    vmin: float = None,
    vmax: float = None,
):
    """
    heatmap_source.shape: H, W
    image_to_blend.shape: H, W, C
    """

    # Generate custom colormap with alpha channel,
    # cf. https://stackoverflow.com/a/37334212/11089932
    # cmap = cm.autumn_r
    # cmap = cm.Reds
    # cmap = cm.bwr
    # cmap = cm.plasma
    c_cmap = cmap(np.arange(cmap.N))
    c_cmap[:, -1] = np.linspace(0, 1, cmap.N)
    c_cmap = ListedColormap(c_cmap)

    # Generate heatmap, cf. https://stackoverflow.com/a/31546410/11089932
    norm = Normalize(
        vmin=vmin if vmin is None else heatmap_source.min(),
        vmax=vmax if vmax is None else heatmap_source.max(),
    )
    heatmap = c_cmap(norm(heatmap_source))

    # Blend image with heatmap
    heatmap = np.uint8(heatmap * 255)
    alpha = heatmap[..., 3] / 255
    alpha = np.tile(np.expand_dims(alpha, axis=2), [1, 1, 3])
    blended = (image_to_blend * (1 - alpha) + heatmap[..., :3] * alpha).astype(np.uint8)
    return blended


def to_contour(array: Literal["NDArray[H, W]"], level: int = 5):
    """
    Given a 2D map of continuous values; returns one that are
    discretised level set.

    Probably similar to ax.contourf.
    """
    value_range = array.max() - array.min()
    gap = value_range / level

    output = array.copy()
    for i in range(level):
        output[(output > i * gap) & (output < (i + 1) * gap)] = i * gap
    return output


def get_contour_path_collection(
    heatmap: Literal["NDArray[H, W]"], level: int = 4, vmin: int = 0
):
    x = np.arange(0, heatmap.shape[1], 1)
    y = np.arange(0, heatmap.shape[0], 1)
    xx, yy = np.meshgrid(x, y)

    # get contour line
    fig, ax = plt.subplots()
    cs = ax.contourf(xx, yy, heatmap, levels=level, vmin=vmin)
    plt.close()
    return cs


def draw_contour_outline(heatmap: Literal["NDArray[H, W]"], ax=None):
    if ax is None:
        ax = plt.gca()
    cs = get_contour_path_collection(heatmap)

    for i in range(len(cs.collections)):
        for p in cs.collections[i].get_paths():
            patch = patches.PathPatch(
                p, facecolor=(0, 0, 0, 1), edgecolor=(0, 0, 0, 0), alpha=0.1
            )

            ax.add_patch(patch)


def add_arrow_from_line(
    line: Line2D,
    arrow_head_idx: int = -1,
    size: int = 15,
    color: str = None,
    line_seg_threshold: float = 1.1,
    arrow_head_offset_ratio: float = 0.65,
    **kwargs,
):
    """
    add an arrow to a line.

    line:       Line2D object
    position:   x-position of the arrow. If None, mean of xdata is taken
    direction:  'left' or 'right'
    size:       size of the arrow in fontsize points
    color:      if None, line color is taken.

    if line segment norm is < line_seg_threshold, skip plotting arrow head
    """
    if color is None:
        color = line.get_color()

    xdata = line.get_xdata()
    ydata = line.get_ydata()

    p1 = np.array([xdata[arrow_head_idx - 1], ydata[arrow_head_idx - 1]])
    p2 = np.array([xdata[arrow_head_idx], ydata[arrow_head_idx]])
    dxy = p2 - p1

    if np.linalg.norm(dxy) < line_seg_threshold:
        return

    arrow_head_origin = p2 - dxy * arrow_head_offset_ratio
    plt.arrow(
        *arrow_head_origin,  # 2 value
        *dxy,  # 2 value
        shape="full",
        lw=0,
        length_includes_head=True,
        head_width=size,
        color=color,
        **kwargs,
    )
