import torch
from .pix2pix_model import define_G

def __patch_instance_norm_state_dict(state_dict, module, keys, i=0):
    """Fix InstanceNorm checkpoints incompatibility (prior to 0.4)"""
    key = keys[i]
    if i + 1 == len(keys):  # at the end, pointing to a parameter/buffer
        if module.__class__.__name__.startswith('InstanceNorm') and \
                (key == 'running_mean' or key == 'running_var'):
            if getattr(module, key) is None:
                state_dict.pop('.'.join(keys))
        if module.__class__.__name__.startswith('InstanceNorm') and \
           (key == 'num_batches_tracked'):
            state_dict.pop('.'.join(keys))
    else:
        __patch_instance_norm_state_dict(state_dict, getattr(module, key), keys, i + 1)


def style(opt):
    if opt.edges:
        netG = define_G(1, 3, 64, 'resnet_9blocks', norm='instance',use_dropout=True, init_type='normal', gpu_ids=[])
    else:
        netG = define_G(3, 3, 64, 'resnet_9blocks', norm='instance',use_dropout=False, init_type='normal', gpu_ids=[])

    #in other to load old pretrain model
    #https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/models/base_model.py
    if isinstance(netG, torch.nn.DataParallel):
        netG = netG.module
    # if you are using PyTorch newer than 0.4 (e.g., built from
    # GitHub source), you can remove str() on self.device
    state_dict = torch.load(opt.model_path, map_location='cpu')
    if hasattr(state_dict, '_metadata'):
        del state_dict._metadata

    # patch InstanceNorm checkpoints prior to 0.4
    for key in list(state_dict.keys()):  # need to copy keys here because we mutate in loop
        __patch_instance_norm_state_dict(state_dict, netG, key.split('.'))
    netG.load_state_dict(state_dict)

    if opt.use_gpu != -1:
        netG.cuda()
    return netG
