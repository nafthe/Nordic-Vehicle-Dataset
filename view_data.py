import argparse
import os
import sys
import prepare_data
import yaml
import imageio
from Util import utility


def main(opt):
    data_file = opt.data_file
    ann_file = opt.annotation_file
    ann_file_basename = None
    if ann_file is not None:
        ann_file_basename = os.path.splitext(os.path.basename(ann_file))[0]

    if not os.path.isfile(data_file):
        sys.exit(
            f"{data_file} not found! Have you run 'prepare_data.py'?"
        )

    with open(data_file) as file:
        data = yaml.safe_load(file)

    data_type = opt.type.lower()
    data_path = data['path']
    list_file = os.path.join(data['path'], data[data_type])

    with open(list_file, "r") as file:
        lines = file.readlines()
        for img_path in lines:
            if ann_file_basename is not None and ann_file_basename not in img_path:
                continue
            img_full_path = os.path.join(data_path, img_path.strip())
            lbl_full_path = img_full_path.replace('images', 'labels').replace(
                '.png', '.txt')
            img = imageio.imread(img_full_path)
            img_height, img_width = img.shape[:2]
            if os.path.isfile(lbl_full_path):
                with open(lbl_full_path, 'r') as file:
                    for line in file:
                        splits = line.split(' ')
                        cx = float(splits[1])
                        cy = float(splits[2])
                        w = float(splits[3])
                        h = float(splits[4])
                        utility.AnnotationBox.CreateFromNormalizedStraightBox(
                            img_width, img_height, cx, cy, w,
                            h).Draw(img, (0, 255, 0), 2)
            utility.DisplayImage('View Data', img, -1, 'q')


def parse_opt(known=False):
    parser = argparse.ArgumentParser(
        description=
        "\nThis python script visualize the data generated by 'prepare_data.py'.\
            \nRun it after 'prepare_data.py' to make sure the generated data is correct.\
            \nIf the video file name is provided (recommended), only the data related to the video will be displayed."
    )
    parser.add_argument(
        '--type',
        type=str,
        help='The data type: train, val, test. (default: train)',
        default='train',
    )
    parser.add_argument(
        '--annotation_file',
        type=str,
        help=
        'The annotation file name. If provided, only the data related to this annotation file will be displayed.',
        required=False)
    
    parser.add_argument(
        '--data_file',
        type=str,
        help=f"yaml data file. Default: '{prepare_data.data_file}",
        default=prepare_data.data_file)

    return parser.parse_known_args()[0] if known else parser.parse_args()


def run(**kwargs):
    opt = parse_opt(True)
    for k, v in kwargs.items():
        setattr(opt, k, v)
    main(opt)


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)
