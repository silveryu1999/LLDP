from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.seismology_recipe import SeismologyRecipe

# num_tasks_list = [50, 100, 200, 500]
num_tasks_list = [50]
for task in num_tasks_list:
    print(task)
    # default: 
    # runtime_factor = 0.05
    # input_file_size_factor = 0.003
    # output_file_size_factor = 10
    rf = 1
    of = 100
    recipe = SeismologyRecipe().from_num_tasks(num_tasks=task, runtime_factor=rf ,output_file_size_factor=of)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '_new' +'.json')
