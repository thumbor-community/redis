# -*- coding: utf-8 -*-

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.context import ServerParameters
from os.path import join, abspath, dirname

SAME_IMAGE_URL = 's.glbimg.com/some_other/image_%d.jpg'
IMAGE_URL = 's.glbimg.com/some/image_%d.jpg'
IMAGE_PATH = join(abspath(dirname(__file__)), 'image.jpg')

with open(IMAGE_PATH, 'r') as img:
    IMAGE_BYTES = img.read()


def get_server(key=None):
    server_params = ServerParameters(
        8888, 'localhost', 'thumbor.conf', None, 'info', None
    )
    server_params.security_key = key
    return server_params
