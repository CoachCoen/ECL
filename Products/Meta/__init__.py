import clsDataObjectDefinition

def initialize(context):
    "Get started"
    context.registerClass(clsDataObjectDefinition.DataObjectDefinition, constructors = (clsDataObjectDefinition.addDataObjectDefinitionForm, clsDataObjectDefinition.addDataObjectDefinition))
