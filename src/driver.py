#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.shell.core.driver_context import (
    AutoLoadCommandContext,
    AutoLoadDetails,
    InitCommandContext,
    ResourceCommandContext,
)
from cloudshell.shell.core.driver_utils import GlobalLock
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.shell.standards.networking.autoload_model import NetworkingResourceModel
from cloudshell.shell.standards.networking.driver_interface import (
    NetworkingResourceDriverInterface,
)
from cloudshell.shell.standards.networking.resource_config import (
    NetworkingResourceConfig,
)

from cloudshell.huawei.wdm.cli.huawei_cli_handler import HuaweiCli
from cloudshell.huawei.wdm.flows.huawei_autoload_flow import (
    HuaweiSnmpAutoloadFlow as AutoloadFlow,
)
from cloudshell.huawei.wdm.flows.huawei_run_command_flow import (
    HuaweiRunCommandFlow as CommandFlow,
)
from cloudshell.huawei.wdm.flows.huawei_state_flow import HuaweiStateFlow as StateFlow
from cloudshell.huawei.wdm.snmp.huawei_snmp_handler import (
    HuaweiWDMSnmpHandler as SNMPHandler,
)


class HuaweiVRPWDMShellDriver(
    ResourceDriverInterface, NetworkingResourceDriverInterface, GlobalLock
):
    SUPPORTED_OS = [r"VRP"]
    SHELL_NAME = "Huawei VRP WDM 2G"

    def __init__(self):
        super(HuaweiVRPWDMShellDriver, self).__init__()
        self._cli = None

    def initialize(self, context: InitCommandContext) -> str:
        """Initialize method.

        :param context: an object with all Resource Attributes inside
        """
        resource_config = NetworkingResourceConfig.from_context(
            shell_name=self.SHELL_NAME, supported_os=self.SUPPORTED_OS, context=context
        )

        self._cli = HuaweiCli(resource_config)
        return "Finished initializing"

    def health_check(self, context: ResourceCommandContext):
        """Performs device health check.

        :param context: an object with all Resource Attributes inside
        :return: Success or Error message
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )
            cli_handler = self._cli.get_cli_handler(resource_config, logger)

            state_operations = StateFlow(
                logger=logger,
                api=api,
                resource_config=resource_config,
                cli_configurator=cli_handler,
            )
            return state_operations.health_check()

    @GlobalLock.lock
    def get_inventory(self, context: AutoLoadCommandContext) -> AutoLoadDetails:
        """Return device structure with all standard attributes.

        :param context: an object with all Resource Attributes inside
        :return: response
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )
            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            snmp_handler = SNMPHandler(resource_config, logger, cli_handler)

            autoload_operations = AutoloadFlow(logger=logger, snmp_handler=snmp_handler)
            logger.info("Autoload started")
            resource_model = NetworkingResourceModel(
                resource_config.name,
                resource_config.shell_name,
                resource_config.family_name,
            )

            response = autoload_operations.discover(
                resource_config.supported_os, resource_model
            )
            logger.info("Autoload completed")
            return response

    def ApplyConnectivityChanges(
        self, context: ResourceCommandContext, request: str
    ) -> str:
        """Create vlan and add or remove it to/from network interface.

        :param context: an object with all Resource Attributes inside
        :param str request: request json
        :return:
        """
        pass

    def run_custom_command(
        self, context: ResourceCommandContext, custom_command: str
    ) -> str:
        """Send custom command.

        :param custom_command: Command user wants to send to the device.
        :param context: an object with all Resource Attributes inside
        :return: result
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            send_command_operations = CommandFlow(
                logger=logger, cli_configurator=cli_handler
            )

            response = send_command_operations.run_custom_command(
                custom_command=custom_command
            )

            return response

    def run_custom_config_command(
        self, context: ResourceCommandContext, custom_command: str
    ) -> str:
        """Send custom command in configuration mode.

        :param custom_command: Command user wants to send to the device
        :param context: an object with all Resource Attributes inside
        :return: result
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = NetworkingResourceConfig.from_context(
                shell_name=self.SHELL_NAME,
                supported_os=self.SUPPORTED_OS,
                context=context,
                api=api,
            )

            cli_handler = self._cli.get_cli_handler(resource_config, logger)
            send_command_operations = CommandFlow(
                logger=logger, cli_configurator=cli_handler
            )

            result_str = send_command_operations.run_custom_config_command(
                custom_command=custom_command
            )

            return result_str

    def save(
        self,
        context: ResourceCommandContext,
        folder_path: str,
        configuration_type: str,
        vrf_management_name: str,
    ) -> str:
        """Save selected file to the provided destination.

        :param context: an object with all Resource Attributes inside
        :param configuration_type: source file, which will be saved
        :param folder_path: destination path where file will be saved
        :param vrf_management_name: VRF management Name
        :return str saved configuration file name
        """
        pass

    @GlobalLock.lock
    def restore(
        self,
        context: ResourceCommandContext,
        path: str,
        configuration_type: str,
        restore_method: str,
        vrf_management_name: str,
    ):
        """Restore selected file to the provided destination.

        :param context: an object with all Resource Attributes inside
        :param path: source config file
        :param configuration_type: running or startup configs
        :param restore_method: append or override methods
        :param vrf_management_name: VRF management Name
        """
        pass

    @GlobalLock.lock
    def load_firmware(
        self, context: ResourceCommandContext, path: str, vrf_management_name: str
    ):
        """Upload and updates firmware on the resource.

        :param context: an object with all Resource Attributes inside
        :param path: full path to firmware file, i.e. tftp://10.10.10.1/firmware.tar
        :param vrf_management_name: VRF management Name
        """
        pass

    def shutdown(self, context):
        """Shutdown device."""
        pass

    def orchestration_save(
        self, context: ResourceCommandContext, mode: str, custom_params: str
    ) -> str:
        """Save selected file to the provided destination.

        :param context: an object with all Resource Attributes inside
        :param mode: mode
        :param custom_params: json with custom save parameters
        :return str response: response json
        """
        pass

    def orchestration_restore(
        self,
        context: ResourceCommandContext,
        saved_artifact_info: str,
        custom_params: str,
    ):
        """Restore selected file to the provided destination.

        :param context: an object with all Resource Attributes inside
        :param saved_artifact_info: OrchestrationSavedArtifactInfo json
        :param custom_params: json with custom restore parameters
        """
        pass

    def cleanup(self):
        """Destroy the driver session.

        This function is called everytime a driver instance is destroyed.
        This is a good place to close any open sessions, finish writing to log files
        """
        pass
