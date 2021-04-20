from cloudshell.huawei.autoload.huawei_generic_snmp_autoload import HuaweiGenericSNMPAutoload
from cloudshell.huawei.flows.huawei_autoload_flow import HuaweiSnmpAutoloadFlow

from cloudshell.snmp.autoload.core.snmp_autoload_error import GeneralAutoloadError
from cloudshell.snmp.autoload.helper.snmp_autoload_helper import log_autoload_details
from cloudshell.snmp.autoload.snmp_entity_table import PortElement


class CustomAutoloadFlow(HuaweiSnmpAutoloadFlow):
    def _autoload_flow(self, supported_os, resource_model):
        try:
            return super()._autoload_flow(supported_os, resource_model)
        except Exception as e:
            return self._custom_autoload(supported_os, resource_model)

    def _custom_autoload(self, supported_os, resource_model):
        with self._snmp_handler.get_service() as snmp_service:
            snmp_service.add_mib_folder_path(self.MIBS_FOLDER)
            snmp_service.load_mib_tables(
                [
                    "HUAWEI-PORT-MIB",
                    "HUAWEI-TC-MIB",
                ]
            )
            snmp_autoload = HuaweiCustomSNMPAutoload(snmp_service, self._logger)

            return snmp_autoload.discover(
                supported_os, resource_model, validate_module_id_by_port_name=False
            )


class HuaweiPortElement:
    def __init__(self, if_entity):
        self.if_entity = if_entity
        self.port_name = if_entity.port_name

    @property
    def entity(self):
        class _HuaweiEntity:
            @property
            def base_entity(self):
                class _EntityDescr:
                    name = ""
                    description = ""
                return _EntityDescr
        return _HuaweiEntity()


class HuaweiCustomSNMPAutoload(HuaweiGenericSNMPAutoload):
    def discover(
        self, supported_os, resource_model, validate_module_id_by_port_name=False
    ):
        """General entry point for autoload.

        Read device structure and attributes: chassis, modules, submodules, ports,
        port-channels and power supplies
        :type resource_model: cloudshell.shell.standards.autoload_generic_models.GenericResourceModel  # noqa: E501
        :param str supported_os:
        :param bool validate_module_id_by_port_name:
        :return: AutoLoadDetails object
        """
        if not resource_model:
            return
        self._resource_model = resource_model
        self.if_table_service.PORT_EXCLUDE_LIST.append("tunnel")

        if not self.system_info_service.is_valid_device_os(supported_os):
            raise GeneralAutoloadError("Unsupported device OS")

        self.logger.debug("*" * 70)
        self.logger.debug("Start SNMP discovery process .....")
        self.system_info_service.fill_attributes(resource_model)
        dummy_chassis = self._resource_model.entities.Chassis(index="0")
        self._resource_model.connect_chassis(dummy_chassis)

        for if_port in self.if_table_service.if_ports.values():
            port = HuaweiPortElement(if_port)
            self._get_ports_attributes(port, dummy_chassis)

        self._get_port_channels(resource_model)

        autoload_details = resource_model.build(
            filter_empty_modules=True, use_new_unique_id=True
        )

        log_autoload_details(self.logger, autoload_details)
        return autoload_details
