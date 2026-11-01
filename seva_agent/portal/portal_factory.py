"""
SevaAgent Portal Factory
Instantiates the appropriate portal adapter based on execution mode.
"""

from seva_agent.core.state import ExecutionMode
from seva_agent.portal.base_adapter import BasePortalAdapter
from seva_agent.portal.nsp_emulator_adapter import NSPEmulatorAdapter
from seva_agent.portal.nsp_live_adapter import NSPLiveAdapter


class PortalFactory:
    @staticmethod
    def get_adapter(mode: ExecutionMode, simulate_layout_shift: bool = False) -> BasePortalAdapter:
        if mode == ExecutionMode.LIVE_OFFICIAL_PORTAL:
            return NSPLiveAdapter()
        else:
            return NSPEmulatorAdapter(simulate_layout_shift=simulate_layout_shift)
