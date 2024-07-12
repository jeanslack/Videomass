# Copyleft (c) Videomass Development Team.
# Distributed under the terms of the GPL3 License.

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class VideomassLanguageBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):

        if self.target_name == "wheel":
            from babel.messages.frontend import compile_catalog

            cmd = compile_catalog()
            cmd.directory = "videomass/data/locale/"
            cmd.domain = "videomass"
            cmd.statistics = True
            cmd.finalize_options()
            cmd.run()
