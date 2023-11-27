from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.srasearch_recipe import SRASearchRecipe

# num_tasks_list = [25,50,200]
num_tasks_list = [50]
for task in num_tasks_list:
    print(task)
    # default: 
    # runtime_factor = 0.05
    # input_file_size_factor = 0.003
    # output_file_size_factor = 10
    rf = 0.001
    of = 0.001
    recipe = SRASearchRecipe().from_num_tasks(num_tasks=task, runtime_factor=rf, input_file_size_factor=1, output_file_size_factor=of)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '_new' +'.json')
