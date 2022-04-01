import numpy as np
from PIL import Image
from typing import List, Tuple


class Compose:
    def __init__(self, transforms: List['Transform']) -> None:
        self.transforms = transforms

    def __repr__(self) -> str:
        return f'Compose(transforms={self.transforms})'

    def __call__(self, img: Image.Image or np.ndarray) -> Image.Image or np.ndarray:
        for transform in self.transforms:
            img = transform(img)
        return img


class Transform:
    pass


#########################################################################################
#                                         Image                                         #
#########################################################################################


class Resize(Transform):
    def __init__(self, size: Tuple[int, ...]) -> None:
        if np.isscalar(size):
            self.size = (size, size)
        else:
            self.size = size

    def __repr__(self) -> str:
        return f'Transform(Resize(size={self.size}))'

    def __call__(self, img: Image.Image) -> Image.Image:
        return img.resize(self.size)


class CenterCrop(Transform):
    def __init__(self, size: Tuple[int, ...]) -> None:
        if np.isscalar(size):
            self.size = (size, size)
        else:
            self.size = size

    def __repr__(self) -> str:
        return f'Transform(CenterCrop(size={self.size}))'

    def __call__(self, img: Image.Image) -> Image.Image:
        w, h = img.size
        tw, th = self.size, self.size
        if w == tw and h == th:
            return img
        else:
            left = (w - tw) // 2
            top = (h - th) // 2
            right = left + tw
            bottom = top + th
            return img.crop((left, top, right, bottom))


class RandomResizedCrop(Transform):
    def __init__(self, size: Tuple[int, ...]) -> None:
        if np.isscalar(size):
            self.size = (size, size)
        else:
            self.size = size

    def __repr__(self) -> str:
        return f'Transform(RandomResizedCrop(size={self.size}))'

    def __call__(self, img: Image.Image) -> Image.Image:
        w, h = img.size
        th, tw = self.size, self.size
        if w == tw and h == th:
            return img
        elif w < tw or h < th:
            return img.resize((tw, th))
        else:
            x1 = np.random.randint(0, w - tw)
            y1 = np.random.randint(0, h - th)
            return img.crop((x1, y1, x1 + tw, y1 + th))


class ToTensor(Transform):
    def __repr__(self) -> str:
        return 'Transform(ToTensor)'

    def __call__(self, img: Image.Image or np.ndarray) -> np.ndarray:
        if isinstance(img, Image.Image):
            img = np.array(img).transpose(2, 0, 1)
        return img / 255.0


#########################################################################################
#                                         Array                                         #
#########################################################################################


class ToPILImage(Transform):
    def __repr__(self) -> str:
        return 'Transform(ToPILImage)'

    def __call__(self, img: np.ndarray) -> Image.Image:
        return Image.fromarray(img.transpose(1, 2, 0))


class Normalize(Transform):
    def __init__(self, mean: Tuple[float, ...], std: Tuple[float, ...]) -> None:
        self.mean = mean
        self.std = std

    def __repr__(self) -> str:
        return f'Transform(Normalize(mean={self.mean}, std={self.std}))'

    def __call__(self, array: np.ndarray) -> np.ndarray:
        if np.isscalar(self.mean):
            mean = self.mean
        else:
            shape_ = [1 for _ in range(array.ndim)]
            shape_[0] = len(array) if len(self.mean) == 1 else len(self.mean)
            mean = np.reshape(self.mean, shape_)

        if np.isscalar(self.std):
            std = self.std
        else:
            shape_ = [1 for _ in range(array.ndim)]
            shape_[0] = len(array) if len(self.std) == 1 else len(self.std)
            std = np.reshape(self.std, shape_)

        return (array - mean) / std


class Flatten(Transform):
    def __repr__(self) -> str:
        return 'Transform(Flatten)'

    def __call__(self, array: np.ndarray) -> np.ndarray:
        return array.flatten()
