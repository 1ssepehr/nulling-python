import argparse
import os


class BaseOptions():
    """This class defines options used in the nulling program.
    """

    def __init__(self):
        """Reset the class; indicates the class hasn't been initailized"""
        self.initialized = False

    def initialize(self, parser):
        """Define the options used in the program."""
        # basic parameters
        parser.add_argument('--N', type=int, default=16, help='number of antenna elements')
        parser.add_argument('--alg', type=str, default='genetic', help='algorithm used to do optimization.')
        parser.add_argument('--k', type=float, default=1, help='d over lambda ratio, where lambda is the wavelength')
        parser.add_argument('--total_bits', type=int, defualt=6, help='total number of bits available')
        parser.add_argument('--patterns_file', type=str, default='all_one', help='individual pattern')
        parser.add_argument('--calib_file', type=str, default='all_zero', help='filepath containing calibration values')
        parser.add_argument('--weights_file', type=str, default='all_one', help='filepath containing antenna weights and turn on/offs')
        parser.add_argument('--angles', type=str, default='linear', help='how antenna vector angles are defined.')
        parser.add_argument('--ang_offset', type=int, default=0, help='angle offset after calibration')
        parser.add_argument('--comp_file', type=str, default='all_one', help='filepath containing temporal compensation vectors')
        parser.add_argument('--main_ang', type=float, default=90, help='mainlobe angle in degrees')
        parser.add_argument('--plot_results', type=bool, default=False, help='whether or not to plot the results')

        parser.add_argument('--signal', type=float, default=1.0, help='signal power (normalized)')
        parser.add_argument('--signal_ang', type=float, default=90, help='direction at which we receive the signal')

        parser.add_argument('--noise', type=float, default = 0.0, help='noise power (normalized)')

        parser.add_argument('--interference_file', type=str, default='all_zero', help='filepath containing interference information')
        parser.add_argument('--null_degs_file', type=str, default='empty', help='filepath containing the null degrees (and weights)')

        self.initialized = True
        return parser

    def gather_options(self):
        """Initialize our parser with basic options(only once).
        Add additional model-specific and dataset-specific options.
        These options are defined in the <modify_commandline_options> function
        in model and dataset classes.
        """
        if not self.initialized:  # check if it has been initialized
            parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser = self.initialize(parser)

        # get the basic options
        opt, _ = parser.parse_known_args()

        # modify model-related parser options
        model_name = opt.model
        model_option_setter = models.get_option_setter(model_name)
        parser = model_option_setter(parser, self.isTrain)
        opt, _ = parser.parse_known_args()  # parse again with new defaults

        # modify dataset-related parser options
        dataset_name = opt.dataset_mode
        dataset_option_setter = data.get_option_setter(dataset_name)
        parser = dataset_option_setter(parser, self.isTrain)

        # save and return the parser
        self.parser = parser
        return parser.parse_args()

    def print_options(self, opt):
        """Print and save options

        It will print both current options and default values(if different).
        It will save options into a text file / [checkpoints_dir] / opt.txt
        """
        message = ''
        message += '----------------- Options ---------------\n'
        for k, v in sorted(vars(opt).items()):
            comment = ''
            default = self.parser.get_default(k)
            if v != default:
                comment = '\t[default: %s]' % str(default)
            message += '{:>25}: {:<30}{}\n'.format(str(k), str(v), comment)
        message += '----------------- End -------------------'
        print(message)

        # save to the disk
        expr_dir = os.path.join(opt.checkpoints_dir, opt.name)
        util.mkdirs(expr_dir)
        file_name = os.path.join(expr_dir, '{}_opt.txt'.format(opt.phase))
        with open(file_name, 'wt') as opt_file:
            opt_file.write(message)
            opt_file.write('\n')

    def parse(self):
        """Parse our options, create checkpoints directory suffix, and set up gpu device."""
        opt = self.gather_options()
        opt.isTrain = self.isTrain   # train or test

        # process opt.suffix
        if opt.suffix:
            suffix = ('_' + opt.suffix.format(**vars(opt))) if opt.suffix != '' else ''
            opt.name = opt.name + suffix

        self.print_options(opt)

        # set gpu ids
        str_ids = opt.gpu_ids.split(',')
        opt.gpu_ids = []
        for str_id in str_ids:
            id = int(str_id)
            if id >= 0:
                opt.gpu_ids.append(id)
        if len(opt.gpu_ids) > 0:
            torch.cuda.set_device(opt.gpu_ids[0])

        self.opt = opt
        return self.opt
