# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
from termux_aichain.core.providers.bitnet import BitNetChat

def test_bitnet_chat_initialization():
    chat = BitNetChat(base_url="http://127.0.0.1:8080/v1", model="bitnet-b1.58-large")
    assert chat.model == "bitnet-b1.58-large"
    assert chat.base_url == "http://127.0.0.1:8080/v1"