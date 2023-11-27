from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.cycles_recipe import CyclesRecipe

# num_tasks_list = [400, 750, 900]
num_tasks_list = [150]
for task in num_tasks_list:
    print(task)
    # default: 
    # runtime_factor = 0.1
    # input_file_size_factor = 1
    # output_file_size_factor = 10
    rf = 0.02
    ipf = 0.2
    of = 2
    recipe = CyclesRecipe().from_num_tasks(num_tasks=task, runtime_factor=rf, input_file_size_factor=ipf, output_file_size_factor=of)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '_new' + '.json')
