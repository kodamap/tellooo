from argparse import ArgumentParser
import configparser

config = configparser.ConfigParser()
config.read('color.ini')
colors = config.sections()


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument(
        '-a',
        '--algorithm',
        help='selct object tracking algorithm',
        default='camshift',
        choices=['camshift', 'meanshift'])
    parser.add_argument(
        '-t',
        '--test',
        help='test mode (without tracking motion)',
        action='store_true')
    parser.add_argument(
        '-tr',
        '--tracking',
        help='test mode (without tracking motion)',
        action='store_true')
    parser.add_argument(
        '-c',
        '--color',
        help='select tracking color in color.ini',
        default='',
        choices=colors)
    parser.add_argument(
        '--enable_detection',
        help='enable object detection using MobileNet-SSD',
        action='store_true')
    parser.add_argument(
        "-m_ss",
        "--model_ssd",
        help="Required. Path to an .xml file with a trained MobileNet-SSD model.",
        type=str,
        default=None)
    parser.add_argument(
        "-m_fc",
        "--model_face",
        help="Optional. Path to an .xml file with a trained Age/Gender Recognition model.",
        type=str,
        default=None)
    parser.add_argument(
        "-m_ag",
        "--model_age_gender",
        help="Optional. Path to an .xml file with a trained Age/Gender Recognition model.",
        type=str,
        default=None)
    parser.add_argument(
        "-m_em",
        "--model_emotions",
        help="Optional. Path to an .xml file with a trained Emotions Recognition model.",
        type=str,
        default=None)
    parser.add_argument(
        "-m_hp",
        "--model_head_pose",
        help="Optional. Path to an .xml file with a trained Head Pose Estimation model.",
        type=str,
        default=None)
    parser.add_argument(
        "-m_lm",
        "--model_facial_landmarks",
        help="Optional. Path to an .xml file with a trained Facial Landmarks Estimation model.",
        type=str,
        default=None)
    parser.add_argument(
        "-l",
        "--cpu_extension",
        help="MKLDNN (CPU)-targeted custom layers.Absolute path to a shared library with the kernels impl.",
        type=str,
        default=None)
    parser.add_argument(
        "-d",
        "--device",
        help="Specify the target device for MobileNet-SSSD / Face Detection to infer on; CPU, GPU, FPGA or MYRIAD is acceptable.",
        default="CPU",
        choices=['CPU', 'GPU', 'FPGA', 'MYRIAD'],
        type=str)
    parser.add_argument(
        "-d_ag",
        "--device_age_gender",
        help="Specify the target device for Age/Gender Recognition to infer on; CPU, GPU, FPGA or MYRIAD is acceptable.",
        default="CPU",
        choices=['CPU', 'GPU', 'FPGA', 'MYRIAD'],
        type=str)
    parser.add_argument(
        "-d_em",
        "--device_emotions",
        help="Specify the target device for Emotions Recognition to infer on; CPU, GPU, FPGA or MYRIAD is acceptable.",
        default="CPU",
        choices=['CPU', 'GPU', 'FPGA', 'MYRIAD'],
        type=str)
    parser.add_argument(
        "-d_hp",
        "--device_head_pose",
        help="Specify the target device for Head Pose Estimation to infer on; CPU, GPU, FPGA or MYRIAD is acceptable.",
        default="CPU",
        choices=['CPU', 'GPU', 'FPGA', 'MYRIAD'],
        type=str)
    parser.add_argument(
        "-d_lm",
        "--device_facial_landmarks",
        help="Specify the target device for Facial Landmarks Estimation to infer on; CPU, GPU, FPGA or MYRIAD is acceptable.",
        default="CPU",
        choices=['CPU', 'GPU', 'FPGA', 'MYRIAD'],
        type=str)
    parser.add_argument(
        "-pp",
        "--plugin_dir",
        help="Path to a plugin folder",
        type=str,
        default=None)
    parser.add_argument(
        "--labels", help="Labels mapping file", default=None, type=str)
    parser.add_argument(
        "-pt",
        "--prob_threshold",
        help="Probability threshold for object detections filtering",
        default=0.3,
        type=float)
    parser.add_argument(
        "-ptf",
        "--prob_threshold_face",
        help="Probability threshold for face detections filtering",
        default=0.5,
        type=float)

    return parser
