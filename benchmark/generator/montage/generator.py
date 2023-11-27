from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.montage_recipe import MontageRecipe
from workflowhub.generator.workflow.montage_recipe import MontageDataset

# num_tasks_list = [500, 700]
num_tasks_list = [50]
for task in num_tasks_list:
    # default: 
    # runtime_factor = 0.04
    # output_file_size_factor = 0.04
    rf = 0.04
    ipf = 1
    of = 0.04
    print(task)
    recipe = MontageRecipe().from_num_tasks(num_tasks=task, runtime_factor=rf, input_file_size_factor=ipf, output_file_size_factor=of)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '_new' + '.json')
