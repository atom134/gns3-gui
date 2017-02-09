# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest
import os
from uuid import uuid4
from unittest.mock import patch, Mock, ANY

from gns3.modules.iou.iou_device import IOUDevice
from gns3.ports.port import Port
from gns3.base_node import BaseNode
from gns3.utils.normalize_filename import normalize_filename
from gns3.modules.iou import IOU


@pytest.fixture
def fake_bin(tmpdir):
    path = str(tmpdir / "test.bin")
    with open(path, "w+") as f:
        f.write("1")
    return path


def test_iou_device_init(local_server, project):

    iou_device = IOUDevice(None, local_server, project)


def test_update(iou_device):

    new_settings = {
        "name": "Unreal IOU",
    }

    with patch('gns3.base_node.BaseNode.controllerHttpPut') as mock:
        iou_device.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}".format(node_id=iou_device.node_id())
        assert kwargs["body"] == {
            'node_id': iou_device._node_id,
            'name': 'Unreal IOU', 'compute_id': 'local', 'node_type': 'iou', 'properties': {}}

        # Callback
        args[1]({"properties": {}})


def test_update_startup_config(iou_device, tmpdir):

    startup_config = str(tmpdir / "config.cfg")
    with open(startup_config, "w+") as f:
        f.write("hostname %h")

    new_settings = {
        "name": "Unreal IOU",
        "startup_config": startup_config
    }

    with patch('gns3.base_node.BaseNode.controllerHttpPut') as mock:
        iou_device.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}".format(node_id=iou_device.node_id())
        assert kwargs["body"]["name"] == "Unreal IOU"
        assert kwargs["body"]["properties"]["startup_config_content"] == "hostname %h"

        # Callback
        args[1]({"properties": {}})


@pytest.mark.skip(reason="Need refactor  to support controller")
def test_exportConfigToDirectory(iou_device, tmpdir):

    path = str(tmpdir)

    with patch("gns3.base_node.BaseNode.httpGet") as mock:
        iou_device.exportConfigToDirectory(path)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/nodes/{node_id}/configs".format(node_id=iou_device.node_id())

        # Callback
        args[1]({"startup_config_content": "TEST"}, context=kwargs["context"])

        with open(os.path.join(path, normalize_filename(iou_device.name()) + "_startup-config.cfg")) as f:
            assert f.read() == "TEST"
