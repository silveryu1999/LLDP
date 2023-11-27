from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.soykb_recipe import SoyKBRecipe

num_tasks_list = [50]
for task in num_tasks_list:
    print(task)
    # default: 
    # runtime_factor = 0.0005
    # input_file_size_factor = 0.0005
    # output_file_size_factor = 5
    rf = 0.0015
    of = 12
    recipe = SoyKBRecipe().from_num_tasks(num_tasks=task, runtime_factor=rf, input_file_size_factor=0.0005, output_file_size_factor=of)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '_new' + '.json')
