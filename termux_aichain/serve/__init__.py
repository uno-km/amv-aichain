# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
==============================================================================
termux-aichain Serve Module Exports (LangServe Alternative)
==============================================================================
"""

from termux_aichain.serve.server import AgentServer, serve
from termux_aichain.serve.dashboard import DASHBOARD_HTML

__all__ = [
    "AgentServer",
    "serve",
    "DASHBOARD_HTML",
]