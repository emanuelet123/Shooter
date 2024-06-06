# Importing Image class from PIL module
from PIL import Image

# Opens a image in RGB mode
color = "yellow"
data = {
    "death": {
        "0": {
            "x1": 12,
            "y1": 3,
            "x2": 41,
            "y2": 39,
        },
        "1": {
            "x1": 62,
            "y1": 3,
            "x2": 91,
            "y2": 39,
        },
        "2": {
            "x1": 111,
            "y1": 3,
            "x2": 137,
            "y2": 39,
        },
        "3": {
            "x1": 155,
            "y1": 3,
            "x2": 184,
            "y2": 39,
        },
        "4": {
            "x1": 198,
            "y1": 3,
            "x2": 228,
            "y2": 39,
        },
        "5": {
            "x1": 244,
            "y1": 3,
            "x2": 279,
            "y2": 39,
        },
        "6": {
            "x1": 292,
            "y1": 3,
            "x2": 329,
            "y2": 39,
        },
        "7": {
            "x1": 340,
            "y1": 3,
            "x2": 375,
            "y2": 39,
        },
    },
    "idle": {
        "0": {
            "x1": 12,
            "y1": 3,
            "x2": 40,
            "y2": 39,
        },
        "1": {
            "x1": 60,
            "y1": 3,
            "x2": 88,
            "y2": 39,
        },
        "2": {
            "x1": 108,
            "y1": 3,
            "x2": 136,
            "y2": 39,
        },
        "3": {
            "x1": 156,
            "y1": 3,
            "x2": 184,
            "y2": 39,
        },
        "4": {
            "x1": 204,
            "y1": 3,
            "x2": 232,
            "y2": 39,
        },
    },
    "jump": {
        "0": {
            "x1": 13,
            "y1": 3,
            "x2": 41,
            "y2": 39,
        }
    },
    "run": {
        "0": {
            "x1": 12,
            "y1": 3,
            "x2": 40,
            "y2": 39,
        },
        "1": {
            "x1": 60,
            "y1": 3,
            "x2": 88,
            "y2": 39,
        },
        "2": {
            "x1": 108,
            "y1": 3,
            "x2": 136,
            "y2": 39,
        },
        "3": {
            "x1": 156,
            "y1": 3,
            "x2": 184,
            "y2": 39,
        },
        "4": {
            "x1": 204,
            "y1": 3,
            "x2": 232,
            "y2": 39,
        },
        "5": {
            "x1": 252,
            "y1": 3,
            "x2": 280,
            "y2": 39,
        },
    }
}

for key1, value1 in data.items():
    im = Image.open(f"./img/characters/{color}/Gunner_{color.title()}_{key1.title()}.png")
    for i, (key2, value2) in enumerate(value1.items()):
        print(key1, key2, value2)
        img = im.crop((value2["x1"], value2["y1"], value2["x2"], value2["y2"]))
        img.save(f"./img/characters/{color}/{key1}/{i}.png")
