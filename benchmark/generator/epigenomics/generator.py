from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.epigenomics_recipe import EpigenomicsRecipe

# num_tasks_list = [100, 250, 400, 500, 750, 1000]
num_tasks_list = [150]
for task in num_tasks_list:
    print(task)
    # default: 
    # runtime_factor = 0.03
    # input_file_size_factor = 0.003
    # output_file_size_factor = 0.03
    rf = 0.03
    ipf = 0.003
    of = 0.3
    recipe = EpigenomicsRecipe().from_num_tasks(num_tasks=task, runtime_factor=rf, input_file_size_factor=ipf, output_file_size_factor=of)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '_new' + '.json')
