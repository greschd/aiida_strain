from aiida.orm import DataFactory
from aiida.orm.data.base import List, Str
from aiida.work.workchain import WorkChain
from aiida.work.class_loader import CLASS_LOADER
from aiida_tools import check_workchain_step

from ._util import _get_structure_key

class ApplyStrains(WorkChain):
    @classmethod
    def define(cls, spec):
        super(ApplyStrains, cls).define(spec)

        spec.input('structure', valid_type=DataFactory('structure'))
        spec.input('strain_kind', valid_type=Str)
        spec.input('strain_parameters', valid_type=Str)
        spec.input('strain_strengths', valid_type=List)

        spec.outputs.dynamic = True
        spec.outline(cls.apply_strain)

    @check_workchain_step
    def apply_strain(self):
        strain_classname = 'strain.structure.' + self.inputs.strain_kind.value
        strain_class = CLASS_LOADER.load_class(strain_classname)

        strain_parametername = 'strain.parameter.' + self.inputs.strain_parameters.value
        strain_parameters = CLASS_LOADER.load_class(strain_parametername)

        strain_instance = strain_class(**strain_parameters)

        structure = self.inputs.structure.get_pymatgen_structure()

        for strength_value in self.inputs.strain_strengths:
            new_structure = strain_instance.apply(structure, strength_multiplier=strength_value)
            new_structure_data = DataFactory('structure')()
            new_structure_data.set_pymatgen(new_structure)
            self.out(_get_structure_key(strength_value), new_structure_data)
